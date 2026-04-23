#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压缩头孢哌酮舒巴坦的内容
"""

import json
import re
from pathlib import Path

DRUGS_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js")

# 压缩后的数据
COMPRESSED_DATA = {
    "indications": "敏感菌所致感染：<strong>呼吸道感染、泌尿道感染、腹腔感染</strong>（腹膜炎、胆囊炎、胆管炎）、<strong>败血症、脑膜炎</strong>、皮肤软组织感染、骨骼关节感染、生殖系统感染（盆腔炎、子宫内膜炎、淋病）。",
    "dosage": "<strong>静脉滴注</strong>：5%葡萄糖或氯化钠注射液溶解，稀释至50-100ml，滴注30-60分钟。<br><strong>成人</strong>：2-4g/日，严重感染可增至8g，分2次（每12小时）。<br><strong>儿童</strong>：40-80mg/kg/日，分2-4次；严重感染160mg/kg/日。<br><strong>肾功能不全</strong>：肌酐清除率15-30ml/min者，舒巴坦≤1g/日；<15ml/min者，舒巴坦≤500mg/日。",
    "contraindications": "对头孢菌素类过敏者禁用；青霉素过敏性休克史者禁用。",
    "adverse_reactions": "常见：<strong>腹泻、稀便</strong>、转氨酶升高；少见：发热、皮疹、静脉炎、血小板减少、出血倾向；偶见过敏性休克。",
    "interactions": "与<strong>氨基糖苷类</strong>联用有协同作用；与<strong>乙醇</strong>同用可致双硫仑样反应（用药期间及停药后5天内禁酒）；与抗凝药合用增加出血风险。",
    "pregnancy_category": "B级",
    "pharmacokinetics": "静脉给药后广泛分布于各组织，主要经肾排泄（舒巴坦84%，头孢哌酮25%），半衰期约1-1.7小时。",
    "precautions": "①青霉素过敏者慎用（交叉过敏率5-10%）；②用药前询问过敏史；③肝功能减退者调整剂量；④长期用药补充维生素K；⑤用药期间禁酒；⑥与氨基糖苷类联用需监测肾功能。"
}

def load_drugs():
    """加载药品数据"""
    with open(DRUGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    return []

def save_drugs(drugs):
    """保存药品数据"""
    content = f"""// 药品数据文件
// 生成时间: 2026-03-19
// 药品数量: {len(drugs)}

const DRUGS_DATA = {json.dumps(drugs, ensure_ascii=False, indent=2)};
"""
    with open(DRUGS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("=" * 60)
    print("压缩头孢哌酮舒巴坦内容")
    print("=" * 60)
    
    # 加载数据
    drugs = load_drugs()
    
    # 查找并更新头孢哌酮舒巴坦
    updated_count = 0
    target_names = ["注射用头孢哌酮钠舒巴坦钠", "※注射用头孢哌酮钠舒巴坦钠"]
    
    for drug in drugs:
        if drug.get('name') in target_names or drug.get('chemical_name') == "注射用头孢哌酮钠舒巴坦钠":
            manual = drug.get('manual', {})
            
            # 更新所有字段为压缩版本
            manual['indications'] = COMPRESSED_DATA['indications']
            manual['dosage'] = COMPRESSED_DATA['dosage']
            manual['contraindications'] = COMPRESSED_DATA['contraindications']
            manual['adverse_reactions'] = COMPRESSED_DATA['adverse_reactions']
            manual['interactions'] = COMPRESSED_DATA['interactions']
            manual['pregnancy_category'] = COMPRESSED_DATA['pregnancy_category']
            manual['pharmacokinetics'] = COMPRESSED_DATA['pharmacokinetics']
            manual['precautions'] = COMPRESSED_DATA['precautions']
            
            drug['manual'] = manual
            updated_count += 1
            print(f"  ✓ 已压缩: {drug['name']} - {drug['specifications'][0]['specification']}")
    
    print(f"\n共更新 {updated_count} 个条目")
    
    # 保存数据
    save_drugs(drugs)
    print(f"✅ 数据已保存")

if __name__ == '__main__':
    main()
