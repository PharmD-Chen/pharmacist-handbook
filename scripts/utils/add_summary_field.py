#!/usr/bin/env python3
"""
为药品手册添加精简版内容（summary字段）
主界面显示summary，详细页面显示完整内容
"""

import json
import re

# 头孢哌酮钠舒巴坦钠的精简版内容
CEFOPERAZONE_SUMMARY = {
    "indications": "敏感菌所致感染：<strong>呼吸道感染、泌尿道感染、腹腔感染</strong>（腹膜炎、胆囊炎、胆管炎）、<strong>败血症、脑膜炎</strong>、皮肤软组织感染、骨骼关节感染、生殖系统感染（盆腔炎、子宫内膜炎、淋病）。",
    "dosage": "<strong>静脉滴注</strong>：5%葡萄糖或氯化钠注射液溶解，稀释至50-100ml，滴注30-60分钟。<br><strong>成人</strong>：2-4g/日，严重感染可增至8g，分2次（每12小时）。<br><strong>儿童</strong>：40-80mg/kg/日，分2-4次；严重感染160mg/kg/日。<br><strong>肾功能不全</strong>：肌酐清除率15-30ml/min者，舒巴坦≤1g/日；<15ml/min者，舒巴坦≤500mg/日。",
    "contraindications": "对头孢菌素类过敏者禁用；青霉素过敏性休克史者禁用。",
    "adverse_reactions": "常见：<strong>腹泻、稀便</strong>、转氨酶升高；少见：发热、皮疹、静脉炎、血小板减少、出血倾向；偶见过敏性休克。",
    "interactions": "与<strong>氨基糖苷类</strong>联用有协同作用；与<strong>乙醇</strong>同用可致双硫仑样反应（用药期间及停药后5天内禁酒）；与抗凝药合用增加出血风险。",
    "pregnancy_category": "B级",
    "pharmacokinetics": "静脉给药后广泛分布于各组织，主要经肾排泄（舒巴坦84%，头孢哌酮25%），半衰期约1-1.7小时。",
    "precautions": "①青霉素过敏者慎用（交叉过敏率5-10%）；②用药前询问过敏史；③肝功能减退者调整剂量；④长期用药补充维生素K；⑤用药期间禁酒；⑥与氨基糖苷类联用需监测肾功能。",
    "black_box_warning": "<strong>严重过敏反应</strong>：可能发生致命性过敏，需立即停药抢救；<strong>出血风险</strong>：含NMTT侧链可抑制凝血因子，营养不良/长期静脉营养/抗凝治疗者需补充维生素K并监测凝血酶原时间。"
}

def load_drugs():
    """加载药品数据"""
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
        # 提取JSON部分
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

def save_drugs(drugs):
    """保存药品数据"""
    js_content = 'const DRUGS_DATA = ' + json.dumps(drugs, ensure_ascii=False, indent=2) + ';'
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

def add_summary_to_cephalosporin(drugs):
    """为头孢哌酮钠舒巴坦钠添加精简版内容"""
    updated_count = 0
    
    for drug in drugs:
        name = drug.get('name', '')
        chemical_name = drug.get('chemical_name', '')
        
        # 匹配头孢哌酮钠舒巴坦钠（不包括带※的）
        if ('头孢哌酮' in name or '头孢哌酮' in chemical_name) and '舒巴坦' in name:
            manual = drug.get('manual', {})
            
            # 为每个字段添加精简版（保留原内容作为完整版）
            for key, summary_value in CEFOPERAZONE_SUMMARY.items():
                if key in manual and manual[key]:
                    # 保存完整内容到 full_xxx 字段
                    full_key = f'full_{key}'
                    if full_key not in manual:
                        manual[full_key] = manual[key]
                    # 设置精简内容
                    manual[key] = summary_value
            
            drug['manual'] = manual
            updated_count += 1
            print(f"✓ 已为 {name} 添加精简版内容")
    
    return drugs, updated_count

def main():
    print("=" * 60)
    print("为头孢哌酮钠舒巴坦钠添加精简版内容")
    print("=" * 60)
    
    # 加载数据
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    # 添加精简版内容
    drugs, updated_count = add_summary_to_cephalosporin(drugs)
    
    print(f"\n共更新 {updated_count} 个条目")
    
    # 保存数据
    save_drugs(drugs)
    print(f"✅ 数据已保存")
    
    print("\n说明：")
    print("- 精简版内容显示在主界面")
    print("- 完整内容保存在 full_xxx 字段，点击箭头查看")

if __name__ == '__main__':
    main()
