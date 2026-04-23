#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为Excel文件中的药品添加用法用量栏 - 版本3
读取正确的工作表"新药信息总表"
"""

import pandas as pd
import json
import re

def main():
    # 读取正确的工作表，跳过前两行标题行，第3行是表头
    excel_path = '原始材料/2026年第一次药事会过会药品信息.xlsx'
    df = pd.read_excel(excel_path, sheet_name='新药信息总表', header=2)
    
    # 删除表头后的空行
    df = df.dropna(subset=[df.columns[0]])
    
    print(f"原始Excel文件信息:")
    print(f"- 行数: {len(df)}")
    print(f"- 列数: {len(df.columns)}")
    print(f"- 原始列名: {df.columns.tolist()}")
    
    # 重命名列以便更清晰
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
    
    print(f"\n重命名后的列名: {df.columns.tolist()}")
    
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
        drug_name = str(row['通用名']) if pd.notna(row['通用名']) else ''
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
    
    print(f"\n成功匹配: {matched_count}/{len(df)}")
    
    # 在"药理作用与适应症"列后插入"用法用量"列
    target_idx = df.columns.get_loc('药理作用与适应症')
    df.insert(target_idx + 1, '用法用量', usage_list)
    
    print(f"\n添加后的列名: {df.columns.tolist()}")
    print(f"添加后的列数: {len(df.columns)}")
    
    # 保存到新的Excel文件
    output_path = '原始材料/2026年第一次药事会过会药品信息_含用法用量.xlsx'
    df.to_excel(output_path, index=False)
    
    print(f"\n已保存到: {output_path}")
    
    # 显示前5行数据预览
    print("\n前5行数据预览:")
    print(df[['序号', '通用名', '规格', '剂型', '用法用量', '生产企业', '单价（元）']].head())

if __name__ == '__main__':
    main()
