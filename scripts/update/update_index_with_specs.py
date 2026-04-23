#!/usr/bin/env python3
"""更新 index.json，添加品规和库位号信息"""

import json
import os

def main():
    # 读取药品索引
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    print(f"✅ 药品索引数量: {len(drug_index)}")
    
    drugs_dir = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
    updated_count = 0
    
    for drug in drug_index:
        drug_id = drug['id']
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        # 读取药品JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 收集所有规格及其库位号
        specs_with_location = []
        for spec in drug_data.get('specifications', []):
            spec_info = {
                'name': spec.get('name', ''),
                'location': spec.get('location', ''),
                'inpatient_location': spec.get('location', ''),  # 住院库位号
                'outpatient_location': ''  # 预留门诊库位号
            }
            specs_with_location.append(spec_info)
        
        # 保存到 index
        if specs_with_location:
            drug['specs_with_location'] = specs_with_location
            updated_count += 1
    
    # 保存更新后的索引
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count} 个药品的品规信息")

if __name__ == '__main__':
    main()
