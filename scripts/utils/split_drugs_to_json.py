#!/usr/bin/env python3
"""将drugs.js拆分为单个JSON文件"""

import json
import re
import os

def split_drugs():
    print("正在读取drugs.js...")
    
    # 读取drugs.js
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取JSON部分
    match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("❌ 无法解析drugs.js")
        return
    
    json_str = match.group(1)
    
    # 解析JSON
    try:
        drugs = json.loads(json_str)
        print(f"✅ 成功解析，共 {len(drugs)} 个药品")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return
    
    # 创建输出目录
    output_dir = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建索引
    index = []
    
    for drug in drugs:
        drug_id = drug['id']
        drug_name = drug['name']
        
        # 创建简化版索引条目
        index_entry = {
            'id': drug_id,
            'name': drug_name,
            'dosage_form': drug.get('dosage_form', ''),
            'full_name': drug.get('full_name', ''),
            'types': drug.get('types', []),
            'manufacturers': drug.get('manufacturers', []),
            'spec_count': drug.get('spec_count', 0),
            'purchase_type': drug.get('purchase_type', '常规供应'),
            'pinyin': drug.get('pinyin', ''),
            'pinyin_initials': drug.get('pinyin_initials', ''),
            'has_manual': bool(drug.get('manual', {}).get('indications', ''))
        }
        index.append(index_entry)
        
        # 保存单个药品JSON文件
        drug_file = os.path.join(output_dir, f'{drug_id}.json')
        with open(drug_file, 'w', encoding='utf-8') as f:
            json.dump(drug, f, ensure_ascii=False, indent=2)
        
        if drug_id % 100 == 0:
            print(f"  已处理 {drug_id}/{len(drugs)} 个药品...")
    
    # 保存索引文件
    index_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成！")
    print(f"  - 索引文件: {index_file}")
    print(f"  - 药品文件: {output_dir}/[id].json")
    print(f"  - 共 {len(drugs)} 个药品")

if __name__ == '__main__':
    split_drugs()
