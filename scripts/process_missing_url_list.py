#!/usr/bin/env python3
"""
处理仍缺少网址的药品清单
- 解析清单文件，识别真正有网址的药品
- 为这些药品补充详细信息和精简版
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

# 项目路径
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_DIR = PROJECT_ROOT / "pharmacist-handbook" / "data" / "drugs"
OUTPUT_DIR = PROJECT_ROOT / "output"
LIST_FILE = OUTPUT_DIR / "仍缺少网址的药品清单_最新.md"

def parse_missing_list():
    """解析缺少网址的药品清单，提取有网址的药品"""
    drugs_with_url = []
    drugs_without_url = []

    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配西药表格行
    western_pattern = r'\|\s*\d+\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(https://[^\s|]+)?\s*\|'
    matches = re.findall(western_pattern, content)

    for match in matches:
        drug_id = match[0].strip()
        name = match[1].strip()
        dosage_form = match[2].strip()
        notes = match[3].strip()
        url = match[4].strip() if len(match) > 4 and match[4] else ""

        drug_info = {
            'id': int(drug_id),
            'name': name,
            'dosage_form': dosage_form,
            'notes': notes,
            'url': url
        }

        if url and url.startswith('http'):
            drugs_with_url.append(drug_info)
        else:
            drugs_without_url.append(drug_info)

    return drugs_with_url, drugs_without_url

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def fetch_drug_content(url):
    """从湖南药事服务网获取药品内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if tables:
            text = tables[0].get_text()
            return text
        return None
    except Exception as e:
        print(f"获取内容失败: {url}, 错误: {e}")
        return None

def extract_fields(text, dosage_form):
    """提取各字段内容"""
    fields = {}

    # 适应证/功能主治 - 优先匹配功能主治（中成药）
    match = re.search(r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        fields['indications'] = clean_text(match.group(1))
    else:
        match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            fields['indications'] = clean_text(match.group(1))

    # 药理作用/成份
    match = re.search(r'(?:成份/药理作用|药理作用|成份)(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        fields['pharmacokinetics'] = clean_text(match.group(1))

    # 用法用量
    match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        fields['dosage'] = clean_text(match.group(1))

    # 禁忌/禁忌症
    match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        fields['contraindications'] = clean_text(match.group(1))

    # 不良反应
    match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        fields['adverse_reactions'] = clean_text(match.group(1))

    # 药物相互作用
    match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        fields['interactions'] = clean_text(match.group(1))

    # 注意事项
    match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
    if match:
        fields['precautions'] = clean_text(match.group(1))

    # 妊娠分级
    match = re.search(r'妊娠期用药安全分级\s*([A-Z]\s*级?)', text)
    if match:
        fields['pregnancy_category'] = match.group(1)
    else:
        match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
        if match:
            fields['pregnancy_category'] = match.group(1)

    return fields

def simplify_indications(text):
    """精简适应症"""
    if not text:
        return ""
    # 去除"请"、"建议"等客套用语，保留关键信息
    text = re.sub(r'(?:请|建议|应该|需要)', '', text)
    text = re.sub(r'本品适用于治疗', '用于', text)
    text = re.sub(r'本品用于', '用于', text)
    # 使用编号格式
    text = re.sub(r'[；;]', ' ', text)
    return text[:200] if len(text) > 200 else text

def simplify_dosage(text, dosage_form):
    """精简用法用量，根据剂型筛选"""
    if not text:
        return ""

    # 根据剂型筛选相关内容
    if '注射' in dosage_form:
        # 只保留注射用法
        text = re.sub(r'口服.*?(?:。|；|$)', '', text)
    elif '片' in dosage_form or '胶囊' in dosage_form or '颗粒' in dosage_form:
        # 只保留口服用法
        text = re.sub(r'(?:静脉|肌内|皮下)注射.*?(?:。|；|$)', '', text)
    elif '软膏' in dosage_form or '乳膏' in dosage_form or '贴剂' in dosage_form:
        # 只保留外用方法
        text = re.sub(r'(?:口服|注射).*?(?:。|；|$)', '', text)

    # 精简表达
    text = re.sub(r'(?:一般|通常|常规)', '', text)
    return text[:200] if len(text) > 200 else text

def simplify_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    text = re.sub(r'(?:因为|由于).*?(?:。|；|$)', '', text)
    return text[:200] if len(text) > 200 else text

def simplify_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    # 保留反应名称，去除机制解释
    text = re.sub(r'(?:可能|通常|一般).*?(?:引起|导致)', '', text)
    return text[:200] if len(text) > 200 else text

def simplify_precautions(text):
    """精简注意事项"""
    if not text:
        return ""
    text = re.sub(r'(?:因为|由于|因此).*?(?:。|；|$)', '', text)
    text = re.sub(r'(?:建议|请|应该)', '', text)
    return text[:200] if len(text) > 200 else text

def simplify_pharmacokinetics(text):
    """精简药代动力学，提取关键参数"""
    if not text:
        return ""

    # 提取关键参数
    result = []

    # 达峰时间
    match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', text)
    if match:
        result.append(f"Tmax:约{match.group(1)}h")

    # 半衰期
    match = re.search(r'半衰期.*?([\d\.]+)\s*小时?', text)
    if match:
        result.append(f"t1/2:约{match.group(1)}h")

    # 生物利用度
    match = re.search(r'生物利用度.*?([\d\.]+)%', text)
    if match:
        result.append(f"F:{match.group(1)}%")

    # 蛋白结合率
    match = re.search(r'蛋白结合率.*?([\d\.]+)%', text)
    if match:
        result.append(f"PB:{match.group(1)}%")

    return "，".join(result) if result else text[:150]

def simplify_interactions(text):
    """精简药物相互作用"""
    if not text or "尚未" in text or "暂无" in text or "未发现" in text:
        return "暂未发现有临床意义的药物相互作用"
    return text[:150] if len(text) > 150 else text

def create_simplified_version(fields, dosage_form):
    """创建精简版内容"""
    simplified = {}

    simplified['indications'] = simplify_indications(fields.get('indications', ''))
    simplified['dosage'] = simplify_dosage(fields.get('dosage', ''), dosage_form)
    simplified['contraindications'] = simplify_contraindications(fields.get('contraindications', ''))
    simplified['adverse_reactions'] = simplify_adverse_reactions(fields.get('adverse_reactions', ''))
    simplified['precautions'] = simplify_precautions(fields.get('precautions', ''))
    simplified['pharmacokinetics'] = simplify_pharmacokinetics(fields.get('pharmacokinetics', ''))
    simplified['interactions'] = simplify_interactions(fields.get('interactions', ''))
    simplified['pregnancy_category'] = fields.get('pregnancy_category', '')

    return simplified

def load_drug_json(drug_id):
    """加载药品JSON文件"""
    json_file = DATA_DIR / f"{drug_id}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_drug_json(drug_id, data):
    """保存药品JSON文件"""
    json_file = DATA_DIR / f"{drug_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def process_drug(drug_info):
    """处理单个药品"""
    drug_id = drug_info['id']
    name = drug_info['name']
    url = drug_info['url']
    dosage_form = drug_info['dosage_form']

    print(f"处理药品: {name} (ID: {drug_id})")

    # 加载现有JSON
    drug_data = load_drug_json(drug_id)
    if not drug_data:
        print(f"  警告: 找不到药品JSON文件: {drug_id}.json")
        return False

    # 检查是否已有完整内容
    if drug_data.get('manual', {}).get('full_indications'):
        print(f"  已有详细内容，跳过")
        return True

    # 获取网页内容
    text = fetch_drug_content(url)
    if not text:
        print(f"  错误: 无法获取网页内容")
        return False

    # 提取字段
    fields = extract_fields(text, dosage_form)

    if not fields.get('indications'):
        print(f"  警告: 未提取到适应症，可能网页结构不同")
        return False

    # 创建精简版
    simplified = create_simplified_version(fields, dosage_form)

    # 更新JSON
    if 'manual' not in drug_data:
        drug_data['manual'] = {}

    manual = drug_data['manual']

    # 精简版
    manual['indications'] = simplified['indications']
    manual['dosage'] = simplified['dosage']
    manual['contraindications'] = simplified['contraindications']
    manual['adverse_reactions'] = simplified['adverse_reactions']
    manual['precautions'] = simplified['precautions']
    manual['pharmacokinetics'] = simplified['pharmacokinetics']
    manual['interactions'] = simplified['interactions']
    manual['pregnancy_category'] = simplified['pregnancy_category']

    # 详细版
    manual['full_indications'] = fields.get('indications', '')
    manual['full_dosage'] = fields.get('dosage', '')
    manual['full_contraindications'] = fields.get('contraindications', '')
    manual['full_adverse_reactions'] = fields.get('adverse_reactions', '')
    manual['full_precautions'] = fields.get('precautions', '')
    manual['full_pharmacokinetics'] = fields.get('pharmacokinetics', '')
    manual['full_interactions'] = fields.get('interactions', '')

    # 记录来源
    if 'url' not in drug_data:
        drug_data['url'] = {}
    drug_data['url']['hnysfww'] = url

    # 保存
    save_drug_json(drug_id, drug_data)

    print(f"  成功更新: {name}")
    return True

def main():
    print("=" * 80)
    print("处理仍缺少网址的药品清单")
    print("=" * 80)

    # 解析清单
    drugs_with_url, drugs_without_url = parse_missing_list()

    print(f"\n分析结果:")
    print(f"  - 有网址的药品: {len(drugs_with_url)}个")
    print(f"  - 无网址的药品: {len(drugs_without_url)}个")

    # 处理有网址的药品
    print(f"\n开始处理有网址的药品...")
    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, drug in enumerate(drugs_with_url, 1):  # 处理所有有网址的药品
        print(f"\n[{i}/{len(drugs_with_url)}] ", end="")

        # 检查是否已有内容
        drug_data = load_drug_json(drug['id'])
        if drug_data and drug_data.get('manual', {}).get('full_indications'):
            print(f"跳过 {drug['name']} (已有内容)")
            skip_count += 1
            continue

        if process_drug(drug):
            success_count += 1
        else:
            fail_count += 1

        time.sleep(0.5)  # 避免请求过快

    print(f"\n{'=' * 80}")
    print("处理完成!")
    print(f"  - 成功: {success_count}个")
    print(f"  - 失败: {fail_count}个")
    print(f"  - 跳过(已有内容): {skip_count}个")

if __name__ == "__main__":
    main()
