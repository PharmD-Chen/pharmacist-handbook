#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补充头孢哌酮舒巴坦的黑框警示和缺失数据
"""

import json
import re
from pathlib import Path

DRUGS_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js")

# 头孢哌酮舒巴坦的完整数据（含黑框警示）
CEPHALOSPORIN_COMPLETE = {
    "black_box_warning": "<strong>严重过敏反应和 Stevens-Johnson 综合征</strong><br>使用头孢哌酮钠舒巴坦钠可能发生严重的、偶可致命的过敏反应。一旦发生过敏反应，应立即停药并给予适当的治疗。包括使用肾上腺素、保持呼吸道通畅、吸氧、静脉给予糖皮质激素、抗组胺药等紧急措施。<br><br><strong>出血风险</strong><br>头孢哌酮分子中含有N-甲基硫四氮唑（NMTT）侧链，可抑制维生素K依赖性凝血因子的合成，导致低凝血酶原血症和出血倾向。营养不良、吸收不良（如囊性纤维化患者）和长期静脉注射高营养制剂的患者及接受抗凝血药治疗的患者应用本品时宜补充维生素K，并监测凝血酶原时间。",
    "indications": "本品用于治疗由敏感菌所引起的下列感染：<br>1）<strong>上、下呼吸道感染</strong>；<br>2）<strong>上、下泌尿道感染</strong>；<br>3）<strong>腹膜炎、胆囊炎、胆管炎和其他腹腔内感染</strong>；<br>4）<strong>败血症</strong>；<br>5）<strong>脑膜炎</strong>；<br>6）<strong>皮肤软组织感染</strong>；<br>7）<strong>骨骼及关节感染</strong>；<br>8）<strong>盆腔炎、子宫内膜炎、淋病及其他生殖系统感染</strong>。<br><br>由于头孢哌酮/舒巴坦具有广谱抗菌活性，因此单用本品就能治疗大多数感染，但有时也需与其他抗生素联合应用。",
    "dosage": "<strong>静脉滴注</strong>：先用5%葡萄糖注射液或氯化钠注射液适量溶解，然后再用同一溶媒稀释至50-100ml供静脉滴注，滴注时间为30-60分钟。<br><br><strong>成人</strong>：常用量一日2-4g（头孢哌酮/舒巴坦各1-2g），分等量每12小时静脉滴注1次。在严重感染或难治性感染时，头孢哌酮/舒巴坦的每日剂量可增加到8g（1:1头孢哌酮/舒巴坦，即头孢哌酮和舒巴坦各4g）。舒巴坦每日最高剂量不超过4g。<br><br><strong>儿童</strong>：常用量一日40-80mg/kg，等分2-4次滴注。严重或难治性感染可增至一日160mg/kg。等分2-4次滴注。新生儿出生第一周内，应每隔12小时给药1次。舒巴坦每日最高剂量不超过80mg/kg。<br><br><strong>肾功能不全患者</strong>：肌酐清除率15-30ml/min的患者每日舒巴坦的最高剂量为1g（即本品最大剂量为2.0g），分等量，每12小时注射一次。肌酐清除率<15ml/min的患者每日舒巴坦的最高剂量为500mg（即本品1.0g），分等量，每12小时注射一次。遇严重感染，必要时可单独增加头孢哌酮的用量。",
    "contraindications": "对本品任何组分或其他头孢菌素过敏的患者禁用。以往发生过青霉素过敏性休克的患者，则不可选用本品。",
    "adverse_reactions": "患者通常对头孢哌酮-舒巴坦耐受良好。多数不良反应为轻度或中度，可以耐受，不影响继续治疗。<br><br><strong>常见的不良反应</strong>：腹泻、稀便、ALT、AST、ALP和血胆红素一过性升高。<br><br><strong>较少见的不良反应</strong>（＜1％）：发热、寒战、头痛、恶心、呕吐、注射部位出现一过性疼痛、静脉炎、斑丘疹、荨麻疹，中性粒细胞减低、血红蛋白降低、血小板减少、低凝血酶原血症、凝血障碍、出血、嗜酸性粒细胞增多。<br><br><strong>长期使用本品可发生可逆性中性粒细胞减少症</strong>。<br><br><strong>偶见</strong>：过敏性休克、Stevens-Johnson综合征。",
    "interactions": "⑴<strong>本品与乙醇</strong>：用药期间及用药后5天内饮酒，可引起面部潮红、出汗、头痛和心动过速等双硫仑样反应。患者在应用本品时应避免饮用含酒精的饮料，也应避免肠道外给予含酒精成分的高营养制剂。<br>⑵<strong>本品与能产生低凝血酶原血症、血小板减少或胃肠道出血的药物</strong>同时应用时，要考虑这些药物对凝血功能以及出血危险性增加的影响。<br>⑶<strong>本品与氨基糖苷类药物</strong>联合应用具有协同作用。<br>⑷其余参阅头孢哌酮和舒巴坦钠。",
    "pregnancy_category": "B级",
    "pharmacokinetics": "静脉注射本品（1g头孢哌酮，1g舒巴坦）5分钟后，头孢哌酮和舒巴坦的平均血药峰浓度（Cmax）分别为236.8mg/L和130.2mg/L，蛋白结合率分别为70%～93%和38%，血消除半衰期（t1/2β）分别为1.7小时和1小时。广泛分布于体内各组织体液中，包括胆汁、皮肤、阑尾、输卵管、卵巢、子宫等。该药主要经肾排泄，所给剂量的约25%头孢哌酮和84%舒巴坦随尿排泄，余下的大部分头孢哌酮经胆汁排泄。",
    "precautions": "⑴<strong>应用本品前必须详细询问患者有否对本品、其他头孢菌素类、青霉素类或其他药物的过敏史</strong>，因为青霉素类和头孢菌素类等β内酰胺类抗生素之间可能存在交叉过敏反应。在青霉素类抗生素过敏患者中约5％～10％可对头孢菌素出现交叉过敏反应。因此有青霉素类过敏史的患者，有指征应用本品时，必须充分权衡利弊后在严密观察下慎用，应用本品时一旦发生过敏性休克，需立即停药。并立即就地抢救，给予注射肾上腺素、保持呼吸道通畅、吸氧、并用升压药、激素及抗组胺药等紧急措施。<br>⑵<strong>本品属妊娠期用药Ｂ类</strong>，孕妇患者有明确指征时应仔细权衡利弊后谨慎应用。<br>⑶<strong>头孢哌酮-舒巴坦均可少量分泌至乳汁中</strong>，因此哺乳期妇女用药时宜暂停授乳。<br>⑷<strong>头孢哌酮大部分经肝胆系统排泄</strong>，因此肝功能严重减退的患者，使用本品时需调整给药方案。<br>⑸<strong>肾功能严重减退的患者</strong>，使用头孢哌酮-舒巴坦时需调整用药剂量和给药间期。<br>⑹<strong>本品在伴有肾功能不全合并肝功能损害的老年人群中的半衰期延长</strong>，药物清除减少和表观分布容积增加。其中有肾功能不全和/或肝功能受损者需调整剂量。<br>⑺<strong>早产儿和新生儿宜慎用本品</strong>。<br>⑻<strong>少数患者在使用头孢哌酮-舒巴坦治疗后出现维生素Ｋ缺乏</strong>，其机制很可能与肠道菌群受到抑制有关。营养不良、吸收不良（如囊性纤维化患者）和长期静脉注射高营养制剂的患者及接受抗凝血药治疗的患者应用本品时宜补充维生素Ｋ，并监测凝血酶原时间。<br>⑼<strong>头孢哌酮-舒巴坦可导致直接Coombs试验阳性</strong>。<br>⑽<strong>采用头孢哌酮-舒巴坦时，用Benidict溶液或Fehling试剂检查尿糖可出现假阳性反应</strong>。"
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
    print("补充头孢哌酮舒巴坦黑框警示和完整数据")
    print("=" * 60)
    
    # 加载数据
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    # 查找并更新所有头孢哌酮舒巴坦
    updated_count = 0
    target_names = [
        "注射用头孢哌酮钠舒巴坦钠",
        "※注射用头孢哌酮钠舒巴坦钠",
        "注射用头孢哌酮钠舒巴坦钠/氯化钠"
    ]
    
    for drug in drugs:
        name = drug.get('name', '')
        chemical_name = drug.get('chemical_name', '')
        
        # 检查是否是头孢哌酮舒巴坦
        is_target = False
        for target in target_names:
            if target in name or target in chemical_name:
                is_target = True
                break
        
        if is_target:
            manual = drug.get('manual', {})
            
            # 添加/更新所有字段
            manual['black_box_warning'] = CEPHALOSPORIN_COMPLETE['black_box_warning']
            manual['indications'] = CEPHALOSPORIN_COMPLETE['indications']
            manual['dosage'] = CEPHALOSPORIN_COMPLETE['dosage']
            manual['contraindications'] = CEPHALOSPORIN_COMPLETE['contraindications']
            manual['adverse_reactions'] = CEPHALOSPORIN_COMPLETE['adverse_reactions']
            manual['interactions'] = CEPHALOSPORIN_COMPLETE['interactions']
            manual['pregnancy_category'] = CEPHALOSPORIN_COMPLETE['pregnancy_category']
            manual['pharmacokinetics'] = CEPHALOSPORIN_COMPLETE['pharmacokinetics']
            manual['precautions'] = CEPHALOSPORIN_COMPLETE['precautions']
            
            drug['manual'] = manual
            updated_count += 1
            spec = drug['specifications'][0]['specification'] if drug.get('specifications') else '未知规格'
            print(f"  ✓ 已更新: {name} - {spec}")
    
    print(f"\n共更新 {updated_count} 个条目")
    
    # 保存数据
    save_drugs(drugs)
    print(f"✅ 数据已保存")

if __name__ == '__main__':
    main()
