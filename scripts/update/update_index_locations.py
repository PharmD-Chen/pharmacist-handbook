#!/usr/bin/env python3
"""更新 index.json，将每个药品的所有规格库位号汇总到 locations 数组"""

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
        
        # 收集所有规格的库位号
        locations = []
        for spec in drug_data.get('specifications', []):
            location = spec.get('location')
            if location:
                locations.append(location)
        
        # 去重并保存
        if locations:
            drug['locations'] = list(dict.fromkeys(locations))  # 保持顺序去重
            updated_count += 1
        else:
            drug['locations'] = []
    
    # 保存更新后的索引
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count} 个药品的库位号列表")
    
    # 统计
    with_locations = sum(1 for d in drug_index if d.get('locations'))
    print(f"\n📊 统计:")
    print(f"   有库位号: {with_locations}")
    print(f"   无库位号: {len(drug_index) - with_locations}")

if __name__ == '__main__':
    main()
