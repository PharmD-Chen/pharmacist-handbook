#!/usr/bin/env python3
"""将库位号添加到每个药品规格的 JSON 文件中"""

import pandas as pd
import json
import os
import re

def clean_name(name):
    """清理药品名称用于匹配"""
    if pd.isna(name):
        return ""
    name = re.sub(r'^[※▲]+', '', str(name))
    name = re.sub(r'^\([^)]+\)', '', name)
    name = re.sub(r'\[[^\]]+\]', '', name)
    return name.strip()

def main():
    # 读取Excel
    excel_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/住院药房 货位号.xlsx'
    print(f"正在读取Excel文件: {excel_path}")
    df = pd.read_excel(excel_path)
    print(f"✅ 成功读取，共 {len(df)} 行数据")
    
    # 创建药品代码到库位号的映射
    location_map = {}
    for idx, row in df.iterrows():
        drug_code = str(row.get('药品代码', '')).strip()
        drug_name = str(row.get('药品名称', '')).strip()
        location = str(row.get('存放位置', '')).strip()
        
        if drug_code and location and location.lower() != 'nan':
            location_map[drug_code] = {
                'name': drug_name,
                'location': location
            }
    
    print(f"✅ 有效库位号记录: {len(location_map)}")
    
    # 读取药品目录
    catalog_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drug_catalog.json'
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # 创建药品名称到代码的映射
    name_to_code = {}
    for item in catalog:
        name = clean_name(item.get('name', ''))
        for spec in item.get('specifications', []):
            code = str(spec.get('code', '')).strip()
            if name and code:
                name_to_code[name] = code
    
    print(f"✅ 药品目录映射: {len(name_to_code)}")
    
    # 读取药品索引
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    # 为每个药品的每个规格添加库位号
    updated_count = 0
    drugs_dir = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
    
    for drug in drug_index:
        drug_id = drug['id']
        drug_name = clean_name(drug.get('name', ''))
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        # 读取药品JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 为每个规格添加库位号
        has_update = False
        for spec in drug_data.get('specifications', []):
            spec_code = str(spec.get('code', '')).strip()
            
            if spec_code and spec_code in location_map:
                spec['location'] = location_map[spec_code]['location']
                has_update = True
            else:
                # 尝试通过药品名称匹配
                if drug_name in name_to_code:
                    matched_code = name_to_code[drug_name]
                    if matched_code in location_map:
                        spec['location'] = location_map[matched_code]['location']
                        has_update = True
        
        # 保存更新
        if has_update:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(drug_data, f, ensure_ascii=False, indent=2)
            updated_count += 1
    
    print(f"\n✅ 已更新 {updated_count} 个药品的规格库位号")
    
    # 统计
    total_specs = 0
    specs_with_location = 0
    
    for drug in drug_index:
        drug_id = drug['id']
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        for spec in drug_data.get('specifications', []):
            total_specs += 1
            if spec.get('location'):
                specs_with_location += 1
    
    print(f"\n📊 统计:")
    print(f"   规格总数: {total_specs}")
    print(f"   有库位号: {specs_with_location}")
    print(f"   覆盖率: {specs_with_location/total_specs*100:.1f}%")

if __name__ == '__main__':
    main()
