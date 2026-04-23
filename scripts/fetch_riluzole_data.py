#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取利鲁唑口服混悬液的正确数据
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def main():
    # 获取利鲁唑口服混悬液的数据
    url = "https://www.hnysfww.com/goods.php?id=919"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    print(f"正在获取: {url}")
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找包含药品信息的table
    tables = soup.find_all('table')
    if tables:
        text = tables[0].get_text()
        
        print("\n原始文本前1500字符:")
        print("=" * 80)
        print(text[:1500])
        print("=" * 80)
        
        # 提取适应症
        indications = ""
        match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            indications = clean_text(match.group(1))
        
        # 提取用法用量
        dosage = ""
        match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            dosage = clean_text(match.group(1))
        
        # 提取禁忌
        contraindications = ""
        match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            contraindications = clean_text(match.group(1))
        
        # 提取不良反应
        adverse_reactions = ""
        match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            adverse_reactions = clean_text(match.group(1))
        
        print("\n提取的数据:")
        print("=" * 80)
        print(f"适应症: {indications[:200] if indications else 'N/A'}")
        print(f"\n用法用量: {dosage[:300] if dosage else 'N/A'}")
        print(f"\n禁忌: {contraindications[:200] if contraindications else 'N/A'}")
        print(f"\n不良反应: {adverse_reactions[:200] if adverse_reactions else 'N/A'}")
        
        # 保存结果
        result = {
            'drug_name': '利鲁唑口服混悬液',
            'url': url,
            'indications': indications,
            'dosage': dosage,
            'contraindications': contraindications,
            'adverse_reactions': adverse_reactions,
            'source_text': text[:1000]
        }
        
        with open('原始材料/利鲁唑口服混悬液_正确数据.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print("\n已保存到: 原始材料/利鲁唑口服混悬液_正确数据.json")

if __name__ == '__main__':
    main()
