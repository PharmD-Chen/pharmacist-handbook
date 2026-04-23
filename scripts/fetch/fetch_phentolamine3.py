#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从湖南药事服务网获取甲磺酸酚妥拉明注射液信息 - 完整版
"""

import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://www.hnysfww.com/goods.php?id=153"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

try:
    print(f"正在获取: {url}")
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找包含药品信息的table
    tables = soup.find_all('table')
    
    drug_info = {
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
        'full_pregnancy_category': '',
        'pharmacokinetics': '',
        'full_pharmacokinetics': '',
        'precautions': '',
        'full_precautions': '',
        'source': '湖南药事服务网'
    }
    
    if tables:
        # 第一个table包含主要信息
        main_table = tables[0]
        text = main_table.get_text()
        
        print("\n提取药品信息...")
        
        # 提取适应证
        if '适应证' in text:
            match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
            if match:
                indications = clean_text(match.group(1))
                drug_info['indications'] = indications[:200] + '...' if len(indications) > 200 else indications
                drug_info['full_indications'] = indications
                print(f"✓ 适应证: {drug_info['indications'][:100]}...")
        
        # 提取药理作用
        if '药理作用' in text:
            match = re.search(r'药理作用(.+?)(?:用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
            if match:
                pharmacology = clean_text(match.group(1))
                drug_info['pharmacokinetics'] = pharmacology[:200] + '...' if len(pharmacology) > 200 else pharmacology
                drug_info['full_pharmacokinetics'] = pharmacology
                print(f"✓ 药理作用: {drug_info['pharmacokinetics'][:100]}...")
        
        # 尝试从其他部分提取更多信息
        # 查找所有行
        rows = main_table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                
                if '用法用量' in label or '用法与用量' in label:
                    drug_info['dosage'] = value[:200] + '...' if len(value) > 200 else value
                    drug_info['full_dosage'] = value
                    print(f"✓ 用法用量: {drug_info['dosage'][:100]}...")
                elif '禁忌' in label:
                    drug_info['contraindications'] = value[:200] + '...' if len(value) > 200 else value
                    drug_info['full_contraindications'] = value
                    print(f"✓ 禁忌: {drug_info['contraindications'][:100]}...")
                elif '不良反应' in label:
                    drug_info['adverse_reactions'] = value[:200] + '...' if len(value) > 200 else value
                    drug_info['full_adverse_reactions'] = value
                    print(f"✓ 不良反应: {drug_info['adverse_reactions'][:100]}...")
                elif '药物相互作用' in label:
                    drug_info['interactions'] = value[:200] + '...' if len(value) > 200 else value
                    drug_info['full_interactions'] = value
                    print(f"✓ 药物相互作用: {drug_info['interactions'][:100]}...")
                elif '注意事项' in label:
                    drug_info['precautions'] = value[:200] + '...' if len(value) > 200 else value
                    drug_info['full_precautions'] = value
                    print(f"✓ 注意事项: {drug_info['precautions'][:100]}...")
                elif '妊娠' in label or '孕妇' in label:
                    drug_info['pregnancy_category'] = value[:100] + '...' if len(value) > 100 else value
                    drug_info['full_pregnancy_category'] = value
                    print(f"✓ 妊娠分级: {drug_info['pregnancy_category'][:100]}...")
    
    # 保存提取的信息
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/phentolamine_complete.json', 'w', encoding='utf-8') as f:
        json.dump(drug_info, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("提取完成！")
    print(f"适应症: {'✓' if drug_info['indications'] else '✗'}")
    print(f"用法用量: {'✓' if drug_info['dosage'] else '✗'}")
    print(f"禁忌: {'✓' if drug_info['contraindications'] else '✗'}")
    print(f"不良反应: {'✓' if drug_info['adverse_reactions'] else '✗'}")
    print(f"药物相互作用: {'✓' if drug_info['interactions'] else '✗'}")
    print(f"妊娠分级: {'✓' if drug_info['pregnancy_category'] else '✗'}")
    print(f"药理作用: {'✓' if drug_info['pharmacokinetics'] else '✗'}")
    print(f"注意事项: {'✓' if drug_info['precautions'] else '✗'}")
    print("="*60)
    print("\n完整信息已保存到 phentolamine_complete.json")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
