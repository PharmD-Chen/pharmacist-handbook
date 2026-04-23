#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从湖南药事服务网获取甲磺酸酚妥拉明注射液信息
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

def extract_section(text, section_name, next_sections=None):
    """提取特定章节内容"""
    if not next_sections:
        next_sections = ['适应证', '适应症', '用法', '禁忌', '不良', '药物相互作用', '药理作用', '贮藏']
    
    pattern = rf'{section_name}[：:]?(.*?)(?={"|".join(next_sections)}|$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        # 清理HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        return clean_text(content)
    return ""

try:
    print(f"正在获取: {url}")
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取页面文本
    text = soup.get_text()
    
    print("\n页面内容预览（前1000字符）:")
    print(text[:1000])
    print("\n" + "="*60)
    
    # 提取关键信息
    drug_info = {
        'indications': '',
        'dosage': '',
        'contraindications': '',
        'adverse_reactions': '',
        'interactions': '',
        'pregnancy_category': '',
        'pharmacokinetics': '',
        'precautions': ''
    }
    
    # 尝试提取适应症
    if '适应证' in text or '适应症' in text:
        indications = extract_section(text, '适应证|适应症', ['用法', '禁忌', '不良'])
        if indications:
            drug_info['indications'] = indications
            print(f"\n适应症: {indications[:200]}...")
    
    # 尝试提取用法用量
    if '用法与用量' in text or '用法用量' in text:
        dosage = extract_section(text, '用法与用量|用法用量', ['禁忌', '不良', '药物相互作用'])
        if dosage:
            drug_info['dosage'] = dosage
            print(f"\n用法用量: {dosage[:200]}...")
    
    # 尝试提取禁忌
    if '禁忌' in text:
        contraindications = extract_section(text, '禁忌', ['不良', '药物相互作用', '注意事项'])
        if contraindications:
            drug_info['contraindications'] = contraindications
            print(f"\n禁忌: {contraindications[:200]}...")
    
    # 尝试提取不良反应
    if '不良反应' in text:
        adverse = extract_section(text, '不良反应', ['药物相互作用', '注意事项', '贮藏'])
        if adverse:
            drug_info['adverse_reactions'] = adverse
            print(f"\n不良反应: {adverse[:200]}...")
    
    # 保存提取的信息
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/phentolamine_info.json', 'w', encoding='utf-8') as f:
        json.dump(drug_info, f, ensure_ascii=False, indent=2)
    
    print("\n信息已保存到 phentolamine_info.json")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
