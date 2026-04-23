#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复结果
"""

import pandas as pd

def main():
    # 读取Excel文件
    output_path = '原始材料/2026年第一次药事会过会药品信息_含用法用量.xlsx'
    df = pd.read_excel(output_path)
    
    # 检查问题药品
    problem_drugs = ['阿利沙坦酯吲达帕胺缓释片', '注射用美罗培南氯化钠注射液', '利鲁唑口服混悬液']
    
    print('修复后的问题药品数据：')
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
    
    # 统计
    has_dosage = df['用法用量'].notna() & (df['用法用量'] != '')
    print(f'\n有用法用量的药品: {has_dosage.sum()}/{len(df)}')
    
    print('\n无用法用量的药品:')
    no_dosage = df[~has_dosage]
    for _, row in no_dosage.iterrows():
        print(f"  - {row['通用名']}")

if __name__ == '__main__':
    main()
