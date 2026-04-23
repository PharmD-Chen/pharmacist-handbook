#!/usr/bin/env python3
"""修复 index.json 的门诊库位号"""

import json
import os

def main():
    drugs_dir = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    updated_count = 0
    total_outpatient = 0
    
    for drug in drug_index:
        drug_id = drug['id']
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 重新构建 specs_with_location
        specs_with_location = []
        has_outpatient = False
        
        for spec in drug_data.get('specifications', []):
            spec_info = {
                'name': spec.get('specification', ''),
                'inpatient_location': spec.get('location', ''),
                'outpatient_location': spec.get('outpatient_location', '')
            }
            specs_with_location.append(spec_info)
            if spec.get('outpatient_location'):
                has_outpatient = True
                total_outpatient += 1
        
        drug['specs_with_location'] = specs_with_location
        
        if has_outpatient:
            updated_count += 1
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count} 个药品")
    print(f"✅ 有门诊库位号的规格: {total_outpatient}")

if __name__ == '__main__':
    main()
