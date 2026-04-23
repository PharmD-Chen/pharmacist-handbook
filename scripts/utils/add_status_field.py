#!/usr/bin/env python3
"""为所有药品添加 status 字段，默认在架"""

import json

def main():
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    
    # 读取索引
    with open(index_path, 'r', encoding='utf-8') as f:
        drug_index = json.load(f)
    
    print(f"共 {len(drug_index)} 个药品")
    
    # 添加 status 字段，默认在架
    updated_count = 0
    for drug in drug_index:
        if 'status' not in drug:
            drug['status'] = '在架'
            updated_count += 1
    
    # 保存
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {updated_count} 个药品")
    print(f"✅ 所有药品默认状态: 在架")
    
    # 统计
    on_shelf = sum(1 for d in drug_index if d.get('status') == '在架')
    off_shelf = sum(1 for d in drug_index if d.get('status') == '已下架')
    print(f"\n📊 统计:")
    print(f"   在架: {on_shelf}")
    print(f"   已下架: {off_shelf}")

if __name__ == '__main__':
    main()
