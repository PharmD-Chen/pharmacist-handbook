#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为Excel文件中的药品添加用法用量栏 - 版本2
只添加用法用量列，保留所有原有列
"""

import pandas as pd
import json
import re

def main():
    # 读取Excel文件
    excel_path = '原始材料/2026年第一次药事会过会药品信息.xlsx'
    df = pd.read_excel(excel_path)
    
    print(f"原始Excel文件信息:")
    print(f"- 行数: {len(df)}")
    print(f"- 列数: {len(df.columns)}")
    print(f"- 原始列名: {df.columns.tolist()}")
    
    # 读取药品数据源
    with open('pharmacist-handbook/data/drugs/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取JSON数据
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("无法解析药品数据源")
        return
    
    drugs_data = json.loads(match.group(1))
    print(f"\n数据源中共有 {len(drugs_data)} 个药品")
    
    # 创建药品名称到用法用量的映射
    drug_usage_map = {}
    for drug in drugs_data:
        name = drug.get('name', '')
        manual = drug.get('manual', {})
        dosage = manual.get('dosage', '')
        if name and dosage:
            drug_usage_map[name] = dosage
    
    print(f"数据源中有用法用量的药品: {len(drug_usage_map)} 个")
    
    # 尝试匹配Excel中的药品并获取用法用量
    print("\n匹配结果:")
    matched_count = 0
    usage_list = []
    
    for idx, row in df.iterrows():
        drug_name = str(row['药物名称']) if pd.notna(row['药物名称']) else ''
        if not drug_name or drug_name == 'nan':
            usage_list.append('')
            continue
        
        # 尝试精确匹配
        if drug_name in drug_usage_map:
            print(f"✓ {drug_name}: 精确匹配成功")
            usage_list.append(drug_usage_map[drug_name])
            matched_count += 1
        else:
            # 尝试部分匹配
            found = False
            for source_name in drug_usage_map.keys():
                if drug_name in source_name or source_name in drug_name:
                    print(f"~ {drug_name}: 部分匹配 -> {source_name}")
                    usage_list.append(drug_usage_map[source_name])
                    matched_count += 1
                    found = True
                    break
            if not found:
                print(f"✗ {drug_name}: 未找到匹配")
                usage_list.append('')
    
    print(f"\n成功匹配: {matched_count}/{len(df[df['药物名称'].notna()])}")
    
    # 在原有DataFrame基础上添加"用法用量"列
    # 插入到"规格"列之后
    spec_idx = df.columns.get_loc('规格')
    df.insert(spec_idx + 1, '用法用量', usage_list)
    
    print(f"\n添加后的列名: {df.columns.tolist()}")
    print(f"添加后的列数: {len(df.columns)}")
    
    # 保存到新的Excel文件
    output_path = '原始材料/2026年第一次药事会过会药品信息_含用法用量.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\n已保存到: {output_path}")
    
    # 显示前5行数据预览
    print("\n前5行数据预览(关键列):")
    preview_cols = ['编号', '申请科室', '药物名称', '规格', '用法用量', '是否国谈', '申请人']
    print(df[preview_cols].head())

if __name__ == '__main__':
    main()
