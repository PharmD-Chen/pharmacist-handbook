#!/usr/bin/env python3
"""根据Excel数据更新药品的临时采购状态"""

import json
import re

def clean_name(name):
    """清理药品名称，去除特殊标记和甲乙类前缀"""
    name = str(name).strip()
    # 去除开头的※▲标记
    name = re.sub(r'^[※▲]+', '', name)
    # 去除开头的(甲)、(乙10%)、(自)等标记
    name = re.sub(r'^\([^)]+\)', '', name)
    # 去除结尾的[国基]、[市基]等标记
    name = re.sub(r'\[[^\]]+\]$', '', name)
    return name.strip()

def main():
    # 读取药品目录JSON
    catalog_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drug_catalog.json'
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # 创建药品名称到采购类型的映射
    purchase_type_map = {}
    for item in catalog:
        name = clean_name(item.get('name', ''))
        if name:
            purchase_type_map[name] = item.get('purchase_type', '常规供应')
    
    print(f"✅ 已加载 {len(purchase_type_map)} 个药品的采购类型信息")
    
    # 读取药品索引
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    # 更新每个药品的采购类型
    updated_count = 0
    for drug in drug_index:
        drug_name = clean_name(drug.get('name', ''))
        
        # 在目录中查找匹配的药品
        if drug_name in purchase_type_map:
            new_type = purchase_type_map[drug_name]
            if drug.get('purchase_type') != new_type:
                drug['purchase_type'] = new_type
                updated_count += 1
    
    # 保存更新后的索引
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count} 个药品的采购类型")
    
    # 统计临时采购药品数量
    temp_count = sum(1 for drug in drug_index if drug.get('purchase_type') == '临时采购')
    print(f"临时采购药品: {temp_count} 个")
    print(f"常规供应药品: {len(drug_index) - temp_count} 个")

if __name__ == '__main__':
    main()
