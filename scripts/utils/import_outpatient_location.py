#!/usr/bin/env python3
"""导入门诊药房货位号，并与住院药房数据验证"""

import pandas as pd
import json
import os

def main():
    # 读取门诊药房Excel
    excel_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/门诊药房 货位号.xls'
    print(f"正在读取门诊药房Excel: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path)
        print(f"✅ 成功读取，共 {len(df)} 行数据")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据:")
        print(df.head())
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    
    # 创建门诊库位号映射
    outpatient_map = {}
    for idx, row in df.iterrows():
        drug_code = str(row.get('药品代码', '')).strip()
        location = str(row.get('存放位置', '')).strip() if '存放位置' in df.columns else ''
        
        if drug_code and location and location.lower() != 'nan':
            outpatient_map[drug_code] = location
    
    print(f"\n✅ 有效门诊库位号: {len(outpatient_map)}")
    
    # 读取住院药房数据用于验证
    inpatient_excel = '/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/住院药房 货位号.xlsx'
    inpatient_df = pd.read_excel(inpatient_excel)
    
    inpatient_map = {}
    for idx, row in inpatient_df.iterrows():
        drug_code = str(row.get('药品代码', '')).strip()
        if drug_code:
            inpatient_map[drug_code] = str(row.get('存放位置', '')).strip()
    
    print(f"✅ 住院药房库位号: {len(inpatient_map)}")
    
    # 验证：检查门诊代码是否在住院中存在
    common_codes = set(outpatient_map.keys()) & set(inpatient_map.keys())
    only_outpatient = set(outpatient_map.keys()) - set(inpatient_map.keys())
    
    print(f"\n📊 数据验证:")
    print(f"   共同药品代码: {len(common_codes)}")
    print(f"   仅门诊有: {len(only_outpatient)}")
    
    if len(only_outpatient) > 0:
        print(f"\n⚠️ 以下药品代码仅在门诊药房存在（前10个）:")
        for code in list(only_outpatient)[:10]:
            print(f"   - {code}: {outpatient_map[code]}")
    
    # 更新药品JSON文件
    drugs_dir = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    updated_count = 0
    mismatch_count = 0
    
    for drug in drug_index:
        drug_id = drug['id']
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        has_update = False
        for spec in drug_data.get('specifications', []):
            spec_code = str(spec.get('code', '')).strip()
            
            if spec_code in outpatient_map:
                # 验证：检查是否与住院库位号冲突
                if spec_code in inpatient_map:
                    if spec.get('location') and spec.get('location') != inpatient_map[spec_code]:
                        print(f"⚠️ 库位号不一致: {spec_code}")
                        print(f"   住院: {inpatient_map[spec_code]}")
                        print(f"   当前JSON: {spec.get('location')}")
                        mismatch_count += 1
                
                # 更新门诊库位号
                spec['outpatient_location'] = outpatient_map[spec_code]
                has_update = True
        
        if has_update:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(drug_data, f, ensure_ascii=False, indent=2)
            updated_count += 1
    
    print(f"\n✅ 已更新 {updated_count} 个药品的门诊库位号")
    if mismatch_count > 0:
        print(f"⚠️ 发现 {mismatch_count} 个库位号不一致")
    
    # 更新index.json
    for drug in drug_index:
        drug_id = drug['id']
        json_path = os.path.join(drugs_dir, f'{drug_id}.json')
        
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        specs = drug.get('specs_with_location', [])
        for spec in specs:
            spec_code = ''
            # 查找对应的规格代码
            for s in drug_data.get('specifications', []):
                if s.get('name') == spec.get('name'):
                    spec_code = str(s.get('code', '')).strip()
                    break
            
            if spec_code in outpatient_map:
                spec['outpatient_location'] = outpatient_map[spec_code]
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 index.json")
    
    # 统计
    with_outpatient = sum(1 for d in drug_index 
                         for s in d.get('specs_with_location', []) 
                         if s.get('outpatient_location'))
    print(f"\n📊 最终统计:")
    print(f"   有门诊库位号的规格: {with_outpatient}")

if __name__ == '__main__':
    main()
