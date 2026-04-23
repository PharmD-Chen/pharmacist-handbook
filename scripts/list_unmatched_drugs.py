#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出无源数据的药品列表
"""

import pandas as pd
import json
import re

def main():
    # 读取正确的工作表
    excel_path = '原始材料/2026年第一次药事会过会药品信息.xlsx'
    df = pd.read_excel(excel_path, sheet_name='新药信息总表', header=2)
    df = df.dropna(subset=[df.columns[0]])

    # 重命名列
    column_mapping = {
        '松江区公立医疗机构新药信息总表': '序号',
        'Unnamed: 1': '通用名',
        'Unnamed: 2': '规格',
        'Unnamed: 3': '剂型',
        'Unnamed: 4': '药理作用与适应症',
        'Unnamed: 5': '生产企业',
        'Unnamed: 6': '单价（元）',
        'Unnamed: 7': '医保类型',
        'Unnamed: 8': '基药类别',
        'Unnamed: 9': '备注'
    }
    df = df.rename(columns=column_mapping)

    # 读取药品数据源
    with open('pharmacist-handbook/data/drugs/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()

    drugs_data = json.loads(re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL).group(1))

    # 创建药品名称集合
    drug_names_in_source = set()
    for drug in drugs_data:
        name = drug.get('name', '')
        if name:
            drug_names_in_source.add(name)

    # 找出未匹配的药品
    unmatched_drugs = []
    for idx, row in df.iterrows():
        drug_name = str(row['通用名']) if pd.notna(row['通用名']) else ''
        if not drug_name or drug_name == 'nan':
            continue

        # 检查是否匹配
        matched = False
        if drug_name in drug_names_in_source:
            matched = True
        else:
            for source_name in drug_names_in_source:
                if drug_name in source_name or source_name in drug_name:
                    matched = True
                    break

        if not matched:
            unmatched_drugs.append({
                '序号': row['序号'],
                '通用名': drug_name,
                '规格': row['规格'],
                '剂型': row['剂型'],
                '生产企业': row['生产企业']
            })

    print('=' * 80)
    print('无源数据的药品列表（共 {} 个）'.format(len(unmatched_drugs)))
    print('=' * 80)
    print()

    for i, drug in enumerate(unmatched_drugs, 1):
        print('{}. {}'.format(i, drug['通用名']))
        print('   规格：{}'.format(drug['规格']))
        print('   剂型：{}'.format(drug['剂型']))
        print('   生产企业：{}'.format(drug['生产企业']))
        print('   湖南药事服务网URL：待补充')
        print()

    # 生成Markdown表格
    print('\n' + '=' * 80)
    print('Markdown表格格式（供您填写URL）')
    print('=' * 80)
    print('| 序号 | 通用名 | 规格 | 剂型 | 湖南药事服务网URL |')
    print('|------|--------|------|------|------------------|')
    for drug in unmatched_drugs:
        seq = int(drug['序号']) if pd.notna(drug['序号']) else ''
        print('| {} | {} | {} | {} | 待补充 |'.format(
            seq,
            drug['通用名'],
            drug['规格'],
            drug['剂型']
        ))

    # 保存到文件
    output_file = '原始材料/无源数据药品列表.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# 无源数据的药品列表\n\n')
        f.write('共 {} 个药品需要补充数据源\n\n'.format(len(unmatched_drugs)))
        f.write('## 药品清单\n\n')
        f.write('| 序号 | 通用名 | 规格 | 剂型 | 湖南药事服务网URL |\n')
        f.write('|------|--------|------|------|------------------|\n')
        for drug in unmatched_drugs:
            seq = int(drug['序号']) if pd.notna(drug['序号']) else ''
            f.write('| {} | {} | {} | {} | 待补充 |\n'.format(
                seq,
                drug['通用名'],
                drug['规格'],
                drug['剂型']
            ))

        f.write('\n## 详细说明\n\n')
        for i, drug in enumerate(unmatched_drugs, 1):
            f.write('### {}. {}\n'.format(i, drug['通用名']))
            f.write('- 规格：{}\n'.format(drug['规格']))
            f.write('- 剂型：{}\n'.format(drug['剂型']))
            f.write('- 生产企业：{}\n'.format(drug['生产企业']))
            f.write('- 湖南药事服务网URL：待补充\n\n')

    print('\n' + '=' * 80)
    print('已保存到文件：{}'.format(output_file))
    print('=' * 80)

if __name__ == '__main__':
    main()
