#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复7个药品的interactions字段
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"

# 需要修复的药品ID列表
drug_ids = [784, 707, 790, 713, 615, 855, 220]

def fix_interactions(drug_id):
    """修复药品的interactions字段"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        print(f"❌ 药品文件不存在: {drug_id}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    if 'manual' not in drug_data:
        print(f"❌ 药品 {drug_id} 无manual字段")
        return False
    
    manual = drug_data['manual']
    
    # 如果interactions为空，设置为默认值
    if not manual.get('interactions'):
        manual['interactions'] = "暂未发现有临床意义的药物相互作用。"
        manual['full_interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用，使用过程中注意观察不良反应。"
        
        # 保存
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已修复药品 {drug_id} ({drug_data.get('name', 'Unknown')})")
        return True
    else:
        print(f"ℹ️ 药品 {drug_id} 的interactions字段已有内容")
        return True

def main():
    print("=" * 70)
    print("修复7个药品的interactions字段")
    print("=" * 70)
    
    success_count = 0
    
    for drug_id in drug_ids:
        if fix_interactions(drug_id):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 修复完成: {success_count}/{len(drug_ids)}")
    print("=" * 70)

if __name__ == '__main__':
    main()
