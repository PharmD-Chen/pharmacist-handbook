#!/usr/bin/env python3
"""更新 index.json 的门诊库位号"""

import json
import os

def main():
    drugs_dir = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    updated_count = 0
    
    for drug in drug_index:
        drug_id = drug['id']
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 更新 specs_with_location
        specs = drug.get('specs_with_location', [])
        has_outpatient = False
        
        for spec in specs:
            spec_name = spec.get('name', '')
            # 在 drug_data 中查找对应的规格
            for s in drug_data.get('specifications', []):
                if s.get('name') == spec_name:
                    outpatient_loc = s.get('outpatient_location', '')
                    if outpatient_loc:
                        spec['outpatient_location'] = outpatient_loc
                        has_outpatient = True
                    break
        
        if has_outpatient:
            updated_count += 1
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count} 个药品的门诊库位号")
    
    # 统计
    total_specs = 0
    with_inpatient = 0
    with_outpatient = 0
    with_both = 0
    
    for drug in drug_index:
        for spec in drug.get('specs_with_location', []):
            total_specs += 1
            has_in = bool(spec.get('inpatient_location'))
            has_out = bool(spec.get('outpatient_location'))
            
            if has_in:
                with_inpatient += 1
            if has_out:
                with_outpatient += 1
            if has_in and has_out:
                with_both += 1
    
    print(f"\n📊 统计:")
    print(f"   规格总数: {total_specs}")
    print(f"   有住院库位号: {with_inpatient}")
    print(f"   有门诊库位号: {with_outpatient}")
    print(f"   两者都有: {with_both}")

if __name__ == '__main__':
    main()
