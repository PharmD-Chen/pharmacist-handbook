#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查药品数据问题
"""

import pandas as pd
import json
import re

def main():
    # 读取Excel文件
    output_path = '原始材料/2026年第一次药事会过会药品信息_含用法用量.xlsx'
    df = pd.read_excel(output_path)
    
    # 检查问题药品
    problem_drugs = ['阿利沙坦酯吲达帕胺缓释片', '注射用美罗培南氯化钠注射液', '利鲁唑口服混悬液']
    
    print('检查问题药品的用法用量：')
    print('=' * 80)
    
    for drug_name in problem_drugs:
        row = df[df['通用名'] == drug_name]
        if not row.empty:
            print(f"\n药品：{drug_name}")
            print(f"规格：{row.iloc[0]['规格']}")
            print(f"剂型：{row.iloc[0]['剂型']}")
            dosage = row.iloc[0]['用法用量']
            print(f"用法用量：{dosage if pd.notna(dosage) else 'N/A'}")
            print('-' * 80)
    
    # 读取数据源检查原始数据
    print('\n\n检查数据源中的原始数据：')
    print('=' * 80)
    
    with open('pharmacist-handbook/data/drugs/drugs.js', 'r') as f:
        content = f.read()
    
    drugs_data = json.loads(re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL).group(1))
    
    for drug in drugs_data:
        if drug['name'] in problem_drugs:
            print(f"\n药品：{drug['name']}")
            manual = drug.get('manual', {})
            dosage = manual.get('dosage', 'N/A')
            full_dosage = manual.get('full_dosage', 'N/A')
            print(f"精简版用法用量：{dosage[:200] if dosage != 'N/A' else 'N/A'}...")
            print(f"详细版用法用量：{full_dosage[:200] if full_dosage != 'N/A' else 'N/A'}...")
            print(f"数据来源：{manual.get('source', 'N/A')}")
            print('-' * 80)
    
    # 检查提取结果文件
    print('\n\n检查提取结果文件：')
    print('=' * 80)
    
    with open('原始材料/新药品信息提取结果.json', 'r') as f:
        extraction_results = json.load(f)
    
    for result in extraction_results:
        if result['通用名'] in problem_drugs:
            print(f"\n药品：{result['通用名']}")
            print(f"提取成功：{result['提取成功']}")
            if result['提取成功'] and result['data']:
                data = result['data']
                print(f"原始适应症：{data.get('indications', 'N/A')[:100]}...")
                print(f"原始用法用量：{data.get('dosage', 'N/A')[:100]}...")
            print('-' * 80)

if __name__ == '__main__':
    main()
