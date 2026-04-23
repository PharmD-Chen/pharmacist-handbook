#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从湖南药事服务网抓取药品详细内容并生成精简版
"""

import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"
OUTPUT_DIR = PROJECT_ROOT / "output"

# HTTP请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def load_drug(drug_id):
    """加载药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    if not drug_file.exists():
        return None
    with open(drug_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_drug(drug_id, drug_data):
    """保存药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    with open(drug_file, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def fetch_drug_content(url):
    """从网站抓取药品内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if not tables:
            return None
        
        text = tables[0].get_text()
        return text
    except Exception as e:
        print(f"抓取失败: {e}")
        return None

def extract_field(text, field_name, patterns):
    """提取字段内容"""
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return clean_text(match.group(1))
    return ""

def parse_drug_info(text):
    """解析药品信息"""
    if not text:
        return None
    
    info = {}
    
    # 适应证/功能主治
    info['full_indications'] = extract_field(text, 'indications', [
        r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)',
        r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
        r'适应症(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
    ])
    
    # 药理作用/成份
    info['full_pharmacokinetics'] = extract_field(text, 'pharmacokinetics', [
        r'成份/药理作用(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)',
        r'药理作用(.+?)(?:用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
        r'成份(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)',
    ])
    
    # 用法用量
    info['full_dosage'] = extract_field(text, 'dosage', [
        r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
    ])
    
    # 禁忌/禁忌症
    info['full_contraindications'] = extract_field(text, 'contraindications', [
        r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)',
    ])
    
    # 不良反应
    info['full_adverse_reactions'] = extract_field(text, 'adverse_reactions', [
        r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)',
    ])
    
    # 药物相互作用
    info['full_interactions'] = extract_field(text, 'interactions', [
        r'药物相互作用(.+?)(?:注意事项|贮藏|$)',
    ])
    
    # 注意事项
    info['full_precautions'] = extract_field(text, 'precautions', [
        r'注意事项(.+?)(?:贮藏|$)',
    ])
    
    # 妊娠分级
    pregnancy_match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
    if pregnancy_match:
        info['pregnancy_category'] = pregnancy_match.group(1)
    else:
        info['pregnancy_category'] = None
    
    return info

def simplify_indications(text):
    """精简适应症"""
    if not text:
        return ""
    text = re.sub(r'适用于治疗', '用于', text)
    text = re.sub(r'请?用于治疗', '用于', text)
    return text[:300]

def simplify_dosage(text, dosage_form):
    """精简用法用量"""
    if not text:
        return ""
    
    # 根据剂型筛选
    if '注射' in dosage_form:
        text = re.sub(r'口服[^。]*。', '', text)
    elif any(x in dosage_form for x in ['片', '胶囊', '颗粒', '丸']):
        text = re.sub(r'静脉注射[^。]*。', '', text)
        text = re.sub(r'肌内注射[^。]*。', '', text)
    
    text = re.sub(r'请?', '', text)
    text = re.sub(r'建议', '', text)
    
    return text[:400]

def simplify_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    text = re.sub(r'禁用于', '禁用：', text)
    return text[:250]

def simplify_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    
    # 尝试提取常见不良反应
    match = re.search(r'常见(?:不良)?反应[：:]?([^。]+)', text)
    if match:
        return f"常见：{match.group(1).strip()[:200]}"
    
    return text[:200]

def simplify_interactions(text):
    """精简药物相互作用"""
    if not text or len(text.strip()) < 10:
        return "暂未发现有临床意义的药物相互作用"
    return text[:250]

def simplify_pharmacokinetics(text):
    """精简药代动力学"""
    if not text:
        return ""
    
    params = []
    
    # 提取关键参数
    patterns = [
        (r'(\d+(?:\.\d+)?)\s*小时?达峰', 'Tmax{}h'),
        (r'半衰期.*?([\d\.]+)\s*小时?', 't1/2{}h'),
        (r'生物利用度.*?([\d\.]+)', 'F{}%'),
        (r'蛋白结合率.*?([\d\.]+)', '蛋白结合率{}%'),
    ]
    
    for pattern, template in patterns:
        match = re.search(pattern, text)
        if match:
            params.append(template.format(match.group(1)))
    
    if params:
        return "；".join(params)
    
    return text[:150]

def simplify_precautions(text):
    """精简注意事项"""
    if not text:
        return ""
    
    text = re.sub(r'请?', '', text)
    text = re.sub(r'建议', '', text)
    text = re.sub(r'应(该)?', '', text)
    
    return text[:250]

def generate_simplified_version(full_info, dosage_form):
    """生成精简版内容"""
    simplified = {}
    
    if full_info.get('full_indications'):
        simplified['indications'] = simplify_indications(full_info['full_indications'])
    
    if full_info.get('full_dosage'):
        simplified['dosage'] = simplify_dosage(full_info['full_dosage'], dosage_form)
    
    if full_info.get('full_contraindications'):
        simplified['contraindications'] = simplify_contraindications(full_info['full_contraindications'])
    
    if full_info.get('full_adverse_reactions'):
        simplified['adverse_reactions'] = simplify_adverse_reactions(full_info['full_adverse_reactions'])
    
    if full_info.get('full_interactions'):
        simplified['interactions'] = simplify_interactions(full_info['full_interactions'])
    
    if full_info.get('full_pharmacokinetics'):
        simplified['pharmacokinetics'] = simplify_pharmacokinetics(full_info['full_pharmacokinetics'])
    
    if full_info.get('full_precautions'):
        simplified['precautions'] = simplify_precautions(full_info['full_precautions'])
    
    return simplified

def update_drug_manual(drug_id, drug_data, full_info):
    """更新药品手册"""
    dosage_form = drug_data.get('dosage_form', '')
    
    # 生成精简版
    simplified = generate_simplified_version(full_info, dosage_form)
    
    # 合并完整版和精简版
    manual = drug_data.get('manual', {})
    manual.update(full_info)  # 添加完整版
    manual.update(simplified)  # 添加精简版
    manual['source'] = '湖南药事服务网'
    
    drug_data['manual'] = manual
    
    # 保存
    save_drug(drug_id, drug_data)
    
    return True

def process_drug(drug_id):
    """处理单个药品"""
    drug_data = load_drug(drug_id)
    if not drug_data:
        return False, "文件不存在"
    
    drug_name = drug_data.get('name', '')
    
    # 检查是否有URL
    url_data = drug_data.get('url', {})
    url = url_data.get('hnysfww', '')
    
    if not url:
        return False, "无湖南药事服务网网址"
    
    # 检查是否已有完整内容
    manual = drug_data.get('manual', {})
    has_full = any(k.startswith('full_') for k in manual.keys())
    
    if has_full:
        # 已有完整内容，只生成精简版
        full_info = {k: v for k, v in manual.items() if k.startswith('full_')}
        dosage_form = drug_data.get('dosage_form', '')
        simplified = generate_simplified_version(full_info, dosage_form)
        
        # 更新精简版
        for key, value in simplified.items():
            manual[key] = value
        
        drug_data['manual'] = manual
        save_drug(drug_id, drug_data)
        
        return True, "已更新精简版"
    
    # 需要从网站抓取
    print(f"  正在抓取 {drug_name} 的内容...")
    text = fetch_drug_content(url)
    
    if not text:
        return False, "无法抓取网页内容"
    
    # 解析内容
    full_info = parse_drug_info(text)
    
    if not full_info or not any(full_info.values()):
        return False, "无法解析内容"
    
    # 更新药品数据
    update_drug_manual(drug_id, drug_data, full_info)
    
    return True, "已抓取并更新完整内容"

def main():
    """主函数"""
    print("=" * 80)
    print("抓取药品详细内容并生成精简版")
    print("=" * 80)
    
    # 加载药品索引
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)
    
    processed = []
    skipped = []
    failed = []
    
    # 只处理有网址的药品
    drugs_with_url = [d for d in drugs_index if d.get('url', {}).get('hnysfww')]
    
    print(f"\n找到 {len(drugs_with_url)} 个有网址的药品")
    print(f"开始处理...\n")
    
    for i, drug in enumerate(drugs_with_url, 1):
        drug_id = drug['id']
        drug_name = drug['name']
        
        print(f"[{i}/{len(drugs_with_url)}] ID {drug_id}: {drug_name}")
        
        success, message = process_drug(drug_id)
        
        if success:
            processed.append({'id': drug_id, 'name': drug_name, 'message': message})
            print(f"  ✓ {message}")
        else:
            failed.append({'id': drug_id, 'name': drug_name, 'reason': message})
            print(f"  ✗ {message}")
        
        # 添加延迟，避免请求过快
        time.sleep(0.5)
    
    # 输出统计
    print("\n" + "=" * 80)
    print("处理统计")
    print("=" * 80)
    print(f"已处理: {len(processed)} 个")
    print(f"失败: {len(failed)} 个")
    
    if failed:
        print("\n失败的药品:")
        for item in failed[:20]:
            print(f"  - ID {item['id']}: {item['name']} - {item['reason']}")
        if len(failed) > 20:
            print(f"  ... 还有 {len(failed) - 20} 个")
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()
