#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新药物相互作用描述
"""

import os
import json
import glob

# 药品数据目录
DRUGS_DIR = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'

# 旧描述 -> 新描述
OLD_TEXT = "如与其他药物同时使用可能会发生药物相互作用，详情请咨询药师或医师。"
NEW_TEXT = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用，使用过程中注意观察不良反应。"

def update_interactions():
    """更新所有药品的药物相互作用描述"""
    updated_count = 0
    
    # 获取所有药品JSON文件
    json_files = glob.glob(os.path.join(DRUGS_DIR, '*.json'))
    
    for json_path in json_files:
        # 跳过index.json
        if 'index.json' in json_path:
            continue
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            has_update = False
            manual = drug_data.get('manual', {})
            
            # 更新 interactions
            if manual.get('interactions') == OLD_TEXT:
                manual['interactions'] = NEW_TEXT
                has_update = True
            
            # 更新 full_interactions
            if manual.get('full_interactions') == OLD_TEXT:
                manual['full_interactions'] = NEW_TEXT
                has_update = True
            
            if has_update:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(drug_data, f, ensure_ascii=False, indent=2)
                updated_count += 1
                print(f"✅ 已更新: {os.path.basename(json_path)}")
        
        except Exception as e:
            print(f"❌ 更新失败 {json_path}: {e}")
    
    print(f"\n{'='*60}")
    print(f"更新完成！共更新 {updated_count} 个药品文件")
    print(f"{'='*60}")

if __name__ == '__main__':
    update_interactions()
