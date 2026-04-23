#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量抓取60个药品的详细说明书内容
从湖南药事服务网抓取并更新到JSON文件
"""

import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"
SUMMARY_FILE = BASE_DIR / "药品网址汇总.md"

def get_drug_ids_with_empty_manual():
    """获取内容空缺的药品ID列表（从药品网址汇总.md中读取）"""
    drug_ids = []
    
    with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到"缺少说明书待补充的药品"部分
    match = re.search(r'缺少说明书待补充的药品.*?\n\|.*?\|\n\|[-:| ]+\|\n(.*?)(?=##|$)', content, re.DOTALL)
    if match:
        table_content = match.group(1)
        # 解析表格行
        for line in table_content.strip().split('\n'):
            if line.startswith('|'):
                parts = line.split('|')
                if len(parts) >= 3:
                    try:
                        drug_id = int(parts[1].strip())
                        drug_ids.append(drug_id)
                    except ValueError:
                        pass
    
    return drug_ids

def fetch_drug_info(drug_id):
    """从JSON文件获取药品基本信息和网址"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    return drug_data

def fetch_webpage_content(url):
    """抓取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        return None

def parse_drug_manual(html_content):
    """解析网页内容，提取药品说明书信息"""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    manual = {
        'indications': '',
        'full_indications': '',
        'dosage': '',
        'full_dosage': '',
        'contraindications': '',
        'full_contraindications': '',
        'adverse_reactions': '',
        'full_adverse_reactions': '',
        'interactions': '',
        'full_interactions': '',
        'pregnancy_category': '',
        'pharmacokinetics': '',
        'full_pharmacokinetics': '',
        'precautions': '',
        'full_precautions': '',
        'source': '湖南药事服务网',
        'url_added': True
    }
    
    # 查找说明书内容区域
    # 通常湖南药事服务网的说明书在特定的div或table中
    
    # 尝试多种可能的选择器
    content_div = soup.find('div', class_='goods_desc') or \
                  soup.find('div', id='goods_desc') or \
                  soup.find('div', class_='description') or \
                  soup.find('div', {'class': re.compile('desc|detail|content', re.I)})
    
    if not content_div:
        # 尝试查找包含"说明书"字样的区域
        for div in soup.find_all('div'):
            if '说明书' in div.get_text():
                content_div = div
                break
    
    if content_div:
        text = content_div.get_text(separator='\n', strip=True)
        
        # 提取适应症
        indications_match = re.search(r'【适应证】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if indications_match:
            manual['full_indications'] = indications_match.group(1).strip()
            manual['indications'] = condense_indications(manual['full_indications'])
        
        # 提取用法用量
        dosage_match = re.search(r'【用法与用量】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if dosage_match:
            manual['full_dosage'] = dosage_match.group(1).strip()
            manual['dosage'] = condense_dosage(manual['full_dosage'])
        
        # 提取禁忌症
        contraindications_match = re.search(r'【禁忌症?】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if contraindications_match:
            manual['full_contraindications'] = contraindications_match.group(1).strip()
            manual['contraindications'] = condense_contraindications(manual['full_contraindications'])
        
        # 提取不良反应
        adverse_match = re.search(r'【不良反应】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if adverse_match:
            manual['full_adverse_reactions'] = adverse_match.group(1).strip()
            manual['adverse_reactions'] = condense_adverse_reactions(manual['full_adverse_reactions'])
        
        # 提取药物相互作用
        interactions_match = re.search(r'【药物相互作用】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if interactions_match:
            manual['full_interactions'] = interactions_match.group(1).strip()
            manual['interactions'] = condense_interactions(manual['full_interactions'])
        
        # 提取妊娠分级
        pregnancy_match = re.search(r'【FDA妊娠分级】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if pregnancy_match:
            manual['pregnancy_category'] = pregnancy_match.group(1).strip()
        
        # 提取药代动力学
        pharma_match = re.search(r'【药理作用】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if pharma_match:
            manual['full_pharmacokinetics'] = pharma_match.group(1).strip()
            manual['pharmacokinetics'] = extract_pharmacokinetics(manual['full_pharmacokinetics'])
        
        # 提取注意事项
        precautions_match = re.search(r'【注意事项】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if precautions_match:
            manual['full_precautions'] = precautions_match.group(1).strip()
            manual['precautions'] = condense_precautions(manual['full_precautions'])
    
    return manual

def condense_indications(text):
    """精简适应症"""
    if not text:
        return ""
    # 去除说明性文字，保留关键疾病名称
    text = re.sub(r'本品适用于治疗', '用于', text)
    text = re.sub(r'本品用于', '用于', text)
    text = re.sub(r'请?', '', text)
    # 限制长度
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def condense_dosage(text):
    """精简用法用量"""
    if not text:
        return ""
    # 提取关键剂量信息
    lines = text.split('\n')
    condensed = []
    for line in lines:
        line = line.strip()
        if '口服' in line or '一次' in line or '一日' in line or 'mg' in line:
            condensed.append(line)
    result = ' '.join(condensed[:3])  # 最多保留3行
    if len(result) > 200:
        result = result[:197] + "..."
    return result if result else text[:200]

def condense_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    # 去除解释性文字
    text = re.sub(r'因为.*?(?=。|$)', '。', text)
    text = re.sub(r'由于.*?(?=。|$)', '。', text)
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def condense_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    # 按系统分类，提取常见反应
    lines = text.split('\n')
    condensed = []
    for line in lines:
        line = line.strip()
        if '常见' in line or '偶见' in line or '罕见' in line:
            condensed.append(line)
    result = ' '.join(condensed[:5])
    if len(result) > 200:
        result = result[:197] + "..."
    return result if result else text[:200]

def condense_interactions(text):
    """精简药物相互作用"""
    if not text or '尚未' in text or '暂无' in text or '不明确' in text:
        return "暂未发现有临床意义的药物相互作用。"
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def extract_pharmacokinetics(text):
    """提取药代动力学关键参数"""
    if not text:
        return ""
    
    params = []
    
    # 提取达峰时间
    tmax_match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', text)
    if tmax_match:
        params.append(f"达峰时间{tmax_match.group(1)}h")
    
    # 提取半衰期
    half_life_match = re.search(r'半衰期.*?([\d\.]+)\s*小时', text)
    if half_life_match:
        params.append(f"半衰期{half_life_match.group(1)}h")
    
    # 提取生物利用度
    bio_match = re.search(r'生物利用度.*?([\d\.]+)%', text)
    if bio_match:
        params.append(f"生物利用度{bio_match.group(1)}%")
    
    return '，'.join(params) if params else ""

def condense_precautions(text):
    """精简注意事项"""
    if not text:
        return ""
    # 去除解释性文字
    text = re.sub(r'建议.*?(?=。|$)', '。', text)
    text = re.sub(r'注意.*?(?=：|$)', '：', text)
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def update_drug_json(drug_id, manual):
    """更新药品JSON文件"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    # 更新manual字段
    drug_data['manual'] = manual
    
    # 更新网址信息
    if 'url' not in drug_data:
        drug_data['url'] = {}
    drug_data['url']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    print("=" * 70)
    print("批量抓取药品说明书内容")
    print("=" * 70)
    
    # 1. 获取需要处理的药品ID
    print("\n📋 步骤1: 读取需要处理的药品列表...")
    drug_ids = get_drug_ids_with_empty_manual()
    print(f"   找到 {len(drug_ids)} 个需要处理的药品")
    
    # 2. 批量处理
    print("\n🌐 步骤2: 开始抓取网页内容...")
    success_count = 0
    failed_count = 0
    failed_drugs = []
    
    for i, drug_id in enumerate(drug_ids, 1):
        print(f"\n[{i}/{len(drug_ids)}] 处理药品 ID: {drug_id}")
        
        # 获取药品信息
        drug_data = fetch_drug_info(drug_id)
        if not drug_data:
            print(f"  ❌ 药品文件不存在")
            failed_count += 1
            failed_drugs.append(drug_id)
            continue
        
        drug_name = drug_data.get('name', 'Unknown')
        url = drug_data.get('url', {}).get('hnysfww', '')
        
        if not url:
            print(f"  ❌ 无网址信息: {drug_name}")
            failed_count += 1
            failed_drugs.append(drug_id)
            continue
        
        print(f"  📄 {drug_name}")
        print(f"  🔗 {url}")
        
        # 抓取网页
        html_content = fetch_webpage_content(url)
        if not html_content:
            print(f"  ❌ 抓取失败")
            failed_count += 1
            failed_drugs.append(drug_id)
            time.sleep(1)
            continue
        
        # 解析内容
        manual = parse_drug_manual(html_content)
        if not manual or not manual['indications']:
            print(f"  ❌ 未找到说明书内容")
            failed_count += 1
            failed_drugs.append(drug_id)
            time.sleep(1)
            continue
        
        # 更新JSON
        if update_drug_json(drug_id, manual):
            print(f"  ✅ 更新成功")
            success_count += 1
        else:
            print(f"  ❌ 更新失败")
            failed_count += 1
            failed_drugs.append(drug_id)
        
        # 延迟，避免请求过快
        time.sleep(1.5)
    
    # 3. 生成报告
    print("\n" + "=" * 70)
    print("📊 处理结果汇总")
    print("=" * 70)
    print(f"总药品数: {len(drug_ids)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    
    if failed_drugs:
        print(f"\n❌ 失败的药品ID: {', '.join(map(str, failed_drugs))}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
