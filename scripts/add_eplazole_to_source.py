#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将注射用艾普拉唑钠添加到数据源
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
    
    # 读取艾普拉唑数据
    with open('原始材料/注射用艾普拉唑钠_数据.json', 'r', encoding='utf-8') as f:
        eplazole_data = json.load(f)
    
    # 检查是否已存在
    exists = False
    for drug in drugs_data:
        if drug['name'] == '注射用艾普拉唑钠':
            exists = True
            print("注射用艾普拉唑钠已存在，更新数据...")
            # 更新数据
            manual = drug.get('manual', {})
            manual['indications'] = eplazole_data['indications'][:200] if len(eplazole_data['indications']) > 200 else eplazole_data['indications']
            manual['full_indications'] = eplazole_data['indications']
            manual['dosage'] = eplazole_data['dosage'][:200] if len(eplazole_data['dosage']) > 200 else eplazole_data['dosage']
            manual['full_dosage'] = eplazole_data['dosage']
            manual['contraindications'] = eplazole_data['contraindications'][:150] if len(eplazole_data['contraindications']) > 150 else eplazole_data['contraindications']
            manual['full_contraindications'] = eplazole_data['contraindications']
            manual['adverse_reactions'] = eplazole_data['adverse_reactions'][:200] if len(eplazole_data['adverse_reactions']) > 200 else eplazole_data['adverse_reactions']
            manual['full_adverse_reactions'] = eplazole_data['adverse_reactions']
            manual['pharmacokinetics'] = eplazole_data.get('pharmacokinetics', '')[:150]
            manual['full_pharmacokinetics'] = eplazole_data.get('pharmacokinetics', '')
            manual['precautions'] = eplazole_data.get('precautions', '')[:150]
            manual['full_precautions'] = eplazole_data.get('precautions', '')
            manual['interactions'] = eplazole_data.get('interactions', '')[:150]
            manual['full_interactions'] = eplazole_data.get('interactions', '')
            manual['source'] = '湖南药事服务网'
            drug['url'] = {'hnysfww': eplazole_data['url'], 'last_updated': '2026-03-24'}
            break
    
    if not exists:
        print("添加新的药品：注射用艾普拉唑钠")
        # 获取最大ID
        max_id = max(drug.get('id', 0) for drug in drugs_data)
        
        # 创建新药品条目
        new_drug = {
            "id": max_id + 1,
            "name": "注射用艾普拉唑钠",
            "full_name": "注射用艾普拉唑钠",
            "chemical_name": "注射用艾普拉唑钠",
            "dosage_form": "注射剂",
            "types": [],
            "manufacturers": [],
            "specifications": [],
            "pinyin": "",
            "pinyin_initials": "",
            "dosage_form_pinyin": "",
            "dosage_form_initials": "",
            "manual": {
                "indications": eplazole_data['indications'][:200] if len(eplazole_data['indications']) > 200 else eplazole_data['indications'],
                "full_indications": eplazole_data['indications'],
                "dosage": eplazole_data['dosage'][:200] if len(eplazole_data['dosage']) > 200 else eplazole_data['dosage'],
                "full_dosage": eplazole_data['dosage'],
                "contraindications": eplazole_data['contraindications'][:150] if len(eplazole_data['contraindications']) > 150 else eplazole_data['contraindications'],
                "full_contraindications": eplazole_data['contraindications'],
                "adverse_reactions": eplazole_data['adverse_reactions'][:200] if len(eplazole_data['adverse_reactions']) > 200 else eplazole_data['adverse_reactions'],
                "full_adverse_reactions": eplazole_data['adverse_reactions'],
                "pharmacokinetics": eplazole_data.get('pharmacokinetics', '')[:150],
                "full_pharmacokinetics": eplazole_data.get('pharmacokinetics', ''),
                "precautions": eplazole_data.get('precautions', '')[:150],
                "full_precautions": eplazole_data.get('precautions', ''),
                "interactions": eplazole_data.get('interactions', '')[:150],
                "full_interactions": eplazole_data.get('interactions', ''),
                "source": "湖南药事服务网"
            },
            "url": {
                "hnysfww": eplazole_data['url'],
                "last_updated": "2026-03-24"
            }
        }
        
        drugs_data.append(new_drug)
        print(f"已添加，新ID: {new_drug['id']}")
    
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
    print(f"当前药品总数: {len(drugs_data)}")

if __name__ == '__main__':
    main()
