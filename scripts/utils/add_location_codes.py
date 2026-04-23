#!/usr/bin/env python3
"""为药品添加住院药房库位号"""

import pandas as pd
import json
import re

def clean_name(name):
    """清理药品名称用于匹配"""
    if pd.isna(name):
        return ""
    # 去除特殊标记
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
    
    # 读取药品索引
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    print(f"✅ 药品索引数量: {len(drug_index)}")
    
    # 读取药品目录（包含药品代码）
    catalog_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drug_catalog.json'
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # 创建药品名称到代码的映射（从目录）
    name_to_code = {}
    for item in catalog:
        name = clean_name(item.get('name', ''))
        code = str(item.get('specifications', [{}])[0].get('code', '')).strip()
        if name and code:
            name_to_code[name] = code
    
    print(f"✅ 药品目录映射: {len(name_to_code)}")
    
    # 为每个药品添加库位号
    matched_count = 0
    unmatched_drugs = []
    
    for drug in drug_index:
        drug_name = clean_name(drug.get('name', ''))
        
        # 通过名称查找药品代码
        drug_code = name_to_code.get(drug_name)
        
        if drug_code and drug_code in location_map:
            drug['location'] = location_map[drug_code]['location']
            drug['drug_code'] = drug_code
            matched_count += 1
        else:
            # 尝试模糊匹配
            found = False
            for code, info in location_map.items():
                excel_name = clean_name(info['name'])
                if drug_name in excel_name or excel_name in drug_name:
                    drug['location'] = info['location']
                    drug['drug_code'] = code
                    matched_count += 1
                    found = True
                    break
            
            if not found:
                drug['location'] = ''
                unmatched_drugs.append(drug['name'])
    
    # 保存更新后的索引
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已更新 {matched_count} 个药品的库位号")
    print(f"❌ 未匹配: {len(unmatched_drugs)} 个")
    
    if unmatched_drugs:
        print(f"\n前10个未匹配药品:")
        for name in unmatched_drugs[:10]:
            print(f"  - {name}")
    
    # 统计
    with_location = sum(1 for d in drug_index if d.get('location'))
    print(f"\n📊 统计:")
    print(f"   有库位号: {with_location}")
    print(f"   无库位号: {len(drug_index) - with_location}")

if __name__ == '__main__':
    main()
