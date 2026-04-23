#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正药品手册精简版内容
确保不良反应和注意事项按要求精简
"""

import json
from pathlib import Path

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"

def fix_tenofovir():
    """修正富马酸替诺福韦二吡呋酯的精简内容"""
    drug_id = 257
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        print(f"❌ 药品文件不存在: {json_path}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    # 修正不良反应精简版
    # 原始：包含过多描述性文字
    # 修正：只保留反应名称和发生率
    drug_data['manual']['adverse_reactions'] = "常见：恶心、腹泻、呕吐、胃肠胀气。偶见：肌酸磷酸激酶及转氨酶升高、全身无力、头晕、头痛、呼吸困难、皮肤药疹。罕见：乳酸中毒、肝肿大。"
    
    # 修正注意事项精简版
    # 原始：包含"因此治疗乙肝还要结合患者自身病情..."等说明性文字
    # 修正：只保留关键警告信息
    drug_data['manual']['precautions'] = "对乙肝治疗不彻底，需结合其他方法。"
    
    # 保存
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已修正药品 {drug_id} (富马酸替诺福韦二吡呋酯)")
    print(f"   - 不良反应精简版已更新")
    print(f"   - 注意事项精简版已更新")
    return True

def check_and_fix_all_drugs():
    """检查并修正所有药品的精简内容"""
    fixed_count = 0
    
    # 遍历所有药品JSON文件
    for json_file in DRUGS_DIR.glob('*.json'):
        if json_file.name == 'index.json':
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            if 'manual' not in drug_data:
                continue
            
            manual = drug_data['manual']
            needs_update = False
            
            # 检查不良反应是否需要精简
            if 'adverse_reactions' in manual and manual['adverse_reactions']:
                ar = manual['adverse_reactions']
                # 如果包含"患者一般耐受良好"、"通常在运动后发生"等描述性文字，需要精简
                if any(phrase in ar for phrase in ['患者一般耐受良好', '通常在', '缓解迅速', '引起']):
                    # 这里只做标记，实际精简需要人工审核
                    print(f"⚠️  药品 {drug_data.get('name', 'Unknown')} [ID: {drug_data.get('id')}] 不良反应可能需要精简")
                    needs_update = True
            
            # 检查注意事项是否需要精简
            if 'precautions' in manual and manual['precautions']:
                pre = manual['precautions']
                # 如果包含"因此"、"还要结合"等说明性文字，需要精简
                if any(phrase in pre for phrase in ['因此', '还要结合', '建议', '应该']):
                    print(f"⚠️  药品 {drug_data.get('name', 'Unknown')} [ID: {drug_data.get('id')}] 注意事项可能需要精简")
                    needs_update = True
            
            if needs_update:
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ 处理文件 {json_file.name} 时出错: {e}")
    
    return fixed_count

def main():
    print("=" * 60)
    print("修正药品手册精简版内容")
    print("=" * 60)
    
    # 1. 修正富马酸替诺福韦二吡呋酯
    print("\n📋 步骤1: 修正富马酸替诺福韦二吡呋酯...")
    fix_tenofovir()
    
    # 2. 检查其他药品
    print("\n📋 步骤2: 检查其他药品的精简内容...")
    count = check_and_fix_all_drugs()
    
    print(f"\n   发现 {count} 个药品可能需要精简")
    
    print("\n" + "=" * 60)
    print("检查完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
