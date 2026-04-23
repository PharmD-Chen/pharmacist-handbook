#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新利鲁唑口服混悬液的正确数据
"""

import json
import re

def main():
    # 读取现有数据源
    drugs_js_path = 'pharmacist-handbook/data/drugs/drugs.js'
    with open(drugs_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取现有数据
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    drugs_data = json.loads(match.group(1))
    
    # 读取利鲁唑的正确数据
    with open('原始材料/利鲁唑口服混悬液_正确数据.json', 'r', encoding='utf-8') as f:
        correct_data = json.load(f)
    
    # 更新利鲁唑的数据
    for drug in drugs_data:
        if drug['name'] == '利鲁唑口服混悬液':
            print("更新利鲁唑口服混悬液的数据...")
            
            # 更新适应症
            drug['manual']['indications'] = correct_data['indications'][:200] if len(correct_data['indications']) > 200 else correct_data['indications']
            drug['manual']['full_indications'] = correct_data['indications']
            
            # 更新用法用量
            dosage = correct_data['dosage']
            drug['manual']['dosage'] = dosage[:200] if len(dosage) > 200 else dosage
            drug['manual']['full_dosage'] = dosage
            
            # 更新禁忌
            drug['manual']['contraindications'] = correct_data['contraindications'][:150] if len(correct_data['contraindications']) > 150 else correct_data['contraindications']
            drug['manual']['full_contraindications'] = correct_data['contraindications']
            
            # 更新不良反应
            drug['manual']['adverse_reactions'] = correct_data['adverse_reactions'][:200] if len(correct_data['adverse_reactions']) > 200 else correct_data['adverse_reactions']
            drug['manual']['full_adverse_reactions'] = correct_data['adverse_reactions']
            
            # 移除标记
            if 'needs_update' in drug['manual']:
                del drug['manual']['needs_update']
            if 'issue' in drug['manual']:
                del drug['manual']['issue']
            
            print(f"  ✓ 适应症: {drug['manual']['indications'][:50]}...")
            print(f"  ✓ 用法用量: {drug['manual']['dosage'][:50]}...")
            print(f"  ✓ 禁忌: {drug['manual']['contraindications'][:50]}...")
    
    # 保存更新后的数据
    output_content = f"""// 药品手册数据 - 更新于 2026-03-24
// 共 {len(drugs_data)} 个药品

const drugIndex = {json.dumps(drugs_data, ensure_ascii=False, indent=2)};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndex }};
}}
"""
    
    with open(drugs_js_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\n已保存更新后的数据到: {drugs_js_path}")

if __name__ == '__main__':
    main()
