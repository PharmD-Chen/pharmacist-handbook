#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动补充11个药品的详细内容
"""

import json
import re
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"

# 11个需要手动补充的药品信息
DRUGS_TO_UPDATE = [
    {
        'id': 938,
        'name': '吡仑帕奈',
        'url': 'https://www.hnysfww.com/goods.php?id=863',
        'spec': '(乙10%)吡仑帕奈片'
    },
    {
        'id': 784,
        'name': '咪唑立宾',
        'url': 'https://www.hnysfww.com/goods.php?id=1811',
        'spec': '(乙10%)咪唑立宾片'
    },
    {
        'id': 707,
        'name': '海曲泊帕乙醇胺',
        'url': 'https://www.hnysfww.com/goods.php?id=13188',
        'spec': '(乙10%)海曲泊帕乙醇胺片'
    },
    {
        'id': 790,
        'name': '琥珀酸瑞波西利',
        'url': 'https://www.hnysfww.com/goods.php?id=13306',
        'spec': '(乙10%)琥珀酸瑞波西利片'
    },
    {
        'id': 713,
        'name': '瑞戈非尼',
        'url': 'https://www.hnysfww.com/goods.php?id=9014',
        'spec': '(乙10%)瑞戈非尼片'
    },
    {
        'id': 1016,
        'name': '金水宝',
        'url': 'https://www.hnysfww.com/goods.php?id=6851',
        'spec': '(甲)金水宝片[国基]'
    },
    {
        'id': 843,
        'name': '丹参',
        'url': 'https://www.hnysfww.com/goods.php?id=5150',
        'spec': '(甲)丹参片[市基]'
    },
    {
        'id': 686,
        'name': '养血安神',
        'url': 'https://www.hnysfww.com/goods.php?id=7513',
        'spec': '(甲)养血安神片[市基]'
    },
    {
        'id': 615,
        'name': '双环醇',
        'url': 'https://www.hnysfww.com/goods.php?id=620',
        'spec': '(乙10%)双环醇片'
    },
    {
        'id': 855,
        'name': '喷托维林氯化铵',
        'url': 'https://www.hnysfww.com/goods.php?id=1549',
        'spec': '(甲)喷托维林氯化铵片'
    },
    {
        'id': 220,
        'name': '地屈孕酮',
        'url': 'https://www.hnysfww.com/goods.php?id=1423',
        'spec': '(乙10%)地屈孕酮片'
    }
]

def fetch_webpage_content(url):
    """抓取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        return None

def parse_drug_manual(html_content, drug_name):
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
    
    # 查找包含说明书的table
    content_table = None
    for table in soup.find_all('table'):
        text = table.get_text(strip=True)
        if '适应证' in text or '适应症' in text or '用法与用量' in text or '药理作用' in text:
            content_table = table
            break
    
    if not content_table:
        return None
    
    # 获取表格文本
    text = content_table.get_text(separator='\n', strip=True)
    
    # 1. 适应证/适应症
    for pattern in [
        r'适应证\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)',
        r'适应症\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)'
    ]:
        match = re.search(pattern, text)
        if match:
            manual['full_indications'] = match.group(1).strip()
            manual['indications'] = condense_indications(manual['full_indications'])
            break
    
    # 2. 用法与用量
    match = re.search(r'用法与用量\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)', text)
    if match:
        manual['full_dosage'] = match.group(1).strip()
        manual['dosage'] = condense_dosage(manual['full_dosage'])
    
    # 3. 禁忌/禁忌症
    match = re.search(r'禁忌(?:症)?\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)', text)
    if match:
        manual['full_contraindications'] = match.group(1).strip()
        manual['contraindications'] = condense_contraindications(manual['full_contraindications'])
    
    # 4. 不良反应
    match = re.search(r'不良反应\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)', text)
    if match:
        manual['full_adverse_reactions'] = match.group(1).strip()
        manual['adverse_reactions'] = condense_adverse_reactions(manual['full_adverse_reactions'])
    
    # 5. 药物相互作用
    match = re.search(r'药物相互作用\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)', text)
    if match:
        manual['full_interactions'] = match.group(1).strip()
        manual['interactions'] = condense_interactions(manual['full_interactions'])
    
    # 6. FDA妊娠分级
    match = re.search(r'FDA妊娠分级\s*([^\n]+)', text)
    if match:
        manual['pregnancy_category'] = match.group(1).strip()
    
    # 7. 药理作用（用于提取药代动力学）
    match = re.search(r'药理作用\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)', text)
    if match:
        manual['full_pharmacokinetics'] = match.group(1).strip()
        manual['pharmacokinetics'] = extract_pharmacokinetics(manual['full_pharmacokinetics'])
    
    # 8. 注意事项
    match = re.search(r'注意事项\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]{2,8}[:：])[^\n]+)*)', text)
    if match:
        manual['full_precautions'] = match.group(1).strip()
        manual['precautions'] = condense_precautions(manual['full_precautions'])
    
    # 如果没有找到适应症，返回None
    if not manual['indications']:
        return None
    
    return manual

def condense_indications(text):
    """精简适应症"""
    if not text:
        return ""
    text = re.sub(r'本品适用于治疗', '用于', text)
    text = re.sub(r'本品用于', '用于', text)
    text = re.sub(r'请?', '', text)
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def condense_dosage(text):
    """精简用法用量"""
    if not text:
        return ""
    lines = text.split('\n')
    condensed = []
    for line in lines:
        line = line.strip()
        if any(kw in line for kw in ['口服', '一次', '一日', 'mg', 'g', 'ml', '静脉', '皮下', '肌内']):
            condensed.append(line)
    result = ' '.join(condensed[:2])
    if len(result) > 150:
        result = result[:147] + "..."
    return result if result else text[:150]

def condense_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    text = re.sub(r'因为.*?(?=。|；|$)', '', text)
    text = re.sub(r'由于.*?(?=。|；|$)', '', text)
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def condense_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    lines = text.split('\n')
    condensed = []
    for line in lines:
        line = line.strip()
        if any(kw in line for kw in ['常见', '偶见', '罕见', '十分罕见']):
            condensed.append(line)
    result = ' '.join(condensed[:3])
    if len(result) > 150:
        result = result[:147] + "..."
    return result if result else text[:150]

def condense_interactions(text):
    """精简药物相互作用"""
    if not text or '尚未' in text or '暂无' in text or '不明确' in text:
        return "暂未发现有临床意义的药物相互作用。"
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def extract_pharmacokinetics(text):
    """提取药代动力学关键参数"""
    if not text:
        return ""
    
    params = []
    
    tmax_match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', text)
    if tmax_match:
        params.append(f"达峰时间{tmax_match.group(1)}h")
    
    half_life_match = re.search(r'半衰期.*?([\d\.]+)\s*小时', text)
    if half_life_match:
        params.append(f"半衰期{half_life_match.group(1)}h")
    
    bio_match = re.search(r'生物利用度.*?([\d\.]+)%', text)
    if bio_match:
        params.append(f"生物利用度{bio_match.group(1)}%")
    
    return '，'.join(params) if params else ""

def condense_precautions(text):
    """精简注意事项"""
    if not text:
        return ""
    text = re.sub(r'建议.*?(?=。|；|$)', '', text)
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def update_drug_json(drug_id, manual, url):
    """更新药品JSON文件"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    drug_data['manual'] = manual
    
    if 'url' not in drug_data:
        drug_data['url'] = {}
    drug_data['url']['hnysfww'] = url
    drug_data['url']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    print("=" * 70)
    print("手动补充11个药品的详细内容")
    print("=" * 70)
    
    success_count = 0
    failed_count = 0
    failed_drugs = []
    
    for i, drug in enumerate(DRUGS_TO_UPDATE, 1):
        print(f"\n[{i}/11] 处理药品 ID: {drug['id']}")
        print(f"  📄 {drug['name']}")
        print(f"  🔗 {drug['url']}")
        
        # 抓取网页
        html_content = fetch_webpage_content(drug['url'])
        if not html_content:
            print(f"  ❌ 抓取失败")
            failed_count += 1
            failed_drugs.append(drug)
            continue
        
        # 解析内容
        manual = parse_drug_manual(html_content, drug['name'])
        if not manual:
            print(f"  ❌ 未找到说明书内容")
            failed_count += 1
            failed_drugs.append(drug)
            continue
        
        # 显示提取的内容摘要
        print(f"  ✓ 适应症: {manual['indications'][:50]}...")
        print(f"  ✓ 用法用量: {manual['dosage'][:50]}...")
        
        # 更新JSON
        if update_drug_json(drug['id'], manual, drug['url']):
            print(f"  ✅ 更新成功")
            success_count += 1
        else:
            print(f"  ❌ 更新失败")
            failed_count += 1
            failed_drugs.append(drug)
    
    # 生成报告
    print("\n" + "=" * 70)
    print("📊 处理结果汇总")
    print("=" * 70)
    print(f"总药品数: 11")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    
    if failed_drugs:
        print(f"\n❌ 失败的药品:")
        for drug in failed_drugs:
            print(f"   - [{drug['id']}] {drug['name']}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
