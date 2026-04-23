#!/usr/bin/env python3
"""
根据湖南药事服务网更新头孢哌酮钠舒巴坦钠/氯化钠的完整内容
网址: https://www.hnysfww.com/goods.php?id=1944
"""

import json
import re

# 根据网站内容更新的完整数据
CEFOPERAZONE_NACL_FULL = {
    "indications": "适用于对头孢哌酮耐药但对本品敏感的大肠埃希菌、柠檬酸杆菌属、克雷伯菌属、肠杆菌属、沙雷菌属、变形杆菌属、摩根菌、普罗维登菌属、铜绿假单胞菌、不动杆菌属、流感嗜血杆菌、葡萄球菌属和拟杆菌属所致的下列感染：<br>1）<strong>支气管扩张合并细菌感染、肺炎、肺脓肿、脓胸等下呼吸道感染</strong>；<br>2）<strong>肾盂肾炎及复杂性尿路感染</strong>；<br>3）<strong>胆囊炎、胆管炎、肝脓肿和腹膜炎（包括盆腔腹膜炎、直肠子宫陷凹脓肿）等腹腔感染</strong>；<br>4）<strong>败血症、感染性心内膜炎</strong>；<br>5）<strong>烧伤、创伤或外科伤口继发皮肤软组织感染</strong>；<br>6）<strong>骨、关节感染</strong>；<br>7）<strong>盆腔炎、子宫内膜炎等生殖道感染</strong>。",
    
    "dosage": "<strong>静脉滴注</strong>：直接静脉滴注，无需配制。<br><br><strong>成人</strong>：常用量一日2-4g（头孢哌酮/舒巴坦各1-2g），分等量每12小时静脉滴注1次。严重感染可增至一日8g（1:1头孢哌酮/舒巴坦，即各4g）。舒巴坦每日最高剂量不超过4g。<br><br><strong>儿童</strong>：常用量一日40-80mg/kg，等分2-4次滴注。严重感染可增至一日160mg/kg，等分2-4次滴注。新生儿出生第一周内，应每隔12小时给药1次。舒巴坦每日最高剂量不超过80mg/kg。<br><br><strong>肾功能不全患者</strong>：肌酐清除率15-30ml/min者，每日舒巴坦最高剂量为1g（即本品最大剂量为2.0g），分等量每12小时注射一次；肌酐清除率<15ml/min者，每日舒巴坦最高剂量为500mg（即本品1.0g），分等量每12小时注射一次。",
    
    "contraindications": "对本品任何组分或其他头孢菌素类过敏的患者禁用。以往发生过青霉素过敏性休克的患者，不可选用本品。",
    
    "adverse_reactions": "患者通常对头孢哌酮-舒巴坦耐受良好。多数不良反应为轻度或中度。<br><br><strong>常见不良反应</strong>：腹泻、稀便、ALT、AST、ALP和血胆红素一过性升高。<br><br><strong>较少见不良反应</strong>（<1%）：发热、寒战、头痛、恶心、呕吐、注射部位疼痛、静脉炎、斑丘疹、荨麻疹，中性粒细胞减少、血红蛋白降低、血小板减少、低凝血酶原血症、凝血障碍、出血、嗜酸性粒细胞增多。<br><br><strong>长期使用可发生可逆性中性粒细胞减少症</strong>。<br><br><strong>偶见</strong>：过敏性休克、Stevens-Johnson综合征。",
    
    "interactions": "①<strong>与乙醇</strong>：用药期间及停药后5天内饮酒，可引起双硫仑样反应（面部潮红、出汗、头痛、心动过速）。应避免饮用含酒精饮料及含酒精的高营养制剂。<br>②<strong>与抗凝药</strong>：合用增加出血风险，需监测凝血酶原时间。<br>③<strong>与氨基糖苷类</strong>：联合应用具有协同作用。<br>④<strong>与能产生低凝血酶原血症、血小板减少或胃肠道出血的药物</strong>：同时应用时出血危险性增加。",
    
    "pregnancy_category": "B级。孕妇患者有明确指征时应仔细权衡利弊后谨慎应用。头孢哌酮-舒巴坦可少量分泌至乳汁中，哺乳期妇女用药时宜暂停授乳。",
    
    "pharmacokinetics": "静脉注射2.0g头孢哌酮-舒巴坦（1g：1g）5分钟后，头孢哌酮和舒巴坦的平均血药峰浓度分别为236.8mg/L和130.3mg/L。肌内注射1.5g（头孢哌酮1.0g和舒巴坦0.5g）后，15分钟至2小时达峰，分别为64.2mg/L和19.0mg/L。<br><br>两者均能很好地分布到各组织和体液中，包括胆汁、皮肤、阑尾、子宫等。头孢哌酮消除半衰期为1.7小时，舒巴坦为1小时。给药后12小时内25%的头孢哌酮和72%的舒巴坦经尿排泄。",
    
    "precautions": "①<strong>过敏史询问</strong>：用药前必须详细询问患者对本品、其他头孢菌素类、青霉素类或其他药物的过敏史。青霉素类过敏患者中约5%～10%可对头孢菌素出现交叉过敏反应。<br>②<strong>过敏性休克处理</strong>：一旦发生，立即停药并就地抢救（注射肾上腺素、保持呼吸道通畅、吸氧、升压药、激素及抗组胺药等）。<br>③<strong>肝功能减退者</strong>：需调整给药方案。<br>④<strong>肾功能严重减退者</strong>：需调整用药剂量和给药间期。<br>⑤<strong>老年患者</strong>：伴有肾功能不全合并肝功能损害者半衰期延长，需调整剂量。<br>⑥<strong>早产儿和新生儿</strong>：宜慎用。<br>⑦<strong>维生素K缺乏</strong>：少数患者用药后出现，营养不良、吸收不良（如肺囊性纤维化）、长期静脉高营养及接受抗凝药治疗者需补充维生素K并监测凝血酶原时间。<br>⑧<strong>Coombs试验</strong>：可导致直接Coombs试验阳性。<br>⑨<strong>尿糖检查</strong>：用Benidict溶液或Fehling试剂检查可出现假阳性。",
    
    "black_box_warning": "<strong>严重出血风险（包括致死）</strong><br>已有含头孢哌酮药品有关的严重出血包括致死情况的报告。需监测出血、血小板减少和凝血障碍迹象。如果有不明原因的持续性出血，应立即停药。<br><br>少数患者使用本品治疗后出现了导致凝血障碍的维生素K缺乏，其机制与合成维生素的肠道菌群受到抑制有关。营养不良、吸收不良（如肺囊性纤维化患者）、酒精中毒患者和长期静脉输注高营养制剂的患者存在上述危险。有低凝血酶原血症（伴随出血或无出血）的报告。<br><br>应监测上述患者以及接受抗凝血药治疗患者的凝血酶原时间，需要时应另外补充维生素K。<br><br>出血的独立风险因素包括：近期脑梗塞、活动性消化性溃疡、止血平衡受损、伴随凝血障碍的肝脏疾病、合并使用影响止血的药物。"
}

# 精简版内容
CEFOPERAZONE_NACL_SUMMARY = {
    "indications": "敏感菌所致感染：<strong>下呼吸道感染</strong>（支气管扩张合并感染、肺炎、肺脓肿）、<strong>复杂性尿路感染</strong>、<strong>腹腔感染</strong>（胆囊炎、胆管炎、腹膜炎）、<strong>败血症、感染性心内膜炎</strong>、皮肤软组织感染、骨关节感染、生殖道感染（盆腔炎、子宫内膜炎）。",
    
    "dosage": "<strong>静脉滴注</strong>：直接滴注，无需配制。<br><strong>成人</strong>：2-4g/日，分2次；严重感染8g/日。<br><strong>儿童</strong>：40-80mg/kg/日，分2-4次。<br><strong>肾功能不全</strong>：肌酐清除率15-30ml/min者舒巴坦≤1g/日；<15ml/min者≤500mg/日。",
    
    "contraindications": "对头孢菌素类过敏者禁用；青霉素过敏性休克史者禁用。",
    
    "adverse_reactions": "常见：腹泻、稀便、转氨酶升高；少见：发热、皮疹、静脉炎、血小板减少、出血倾向；偶见过敏性休克、Stevens-Johnson综合征。",
    
    "interactions": "与<strong>乙醇</strong>同用可致双硫仑样反应（用药期间及停药后5天内禁酒）；与<strong>抗凝药</strong>合用增加出血风险；与<strong>氨基糖苷类</strong>联用有协同作用。",
    
    "pregnancy_category": "B级。孕妇慎用，哺乳期妇女宜暂停授乳。",
    
    "pharmacokinetics": "静脉给药后广泛分布于各组织，主要经肾排泄（舒巴坦72%，头孢哌酮25%），半衰期头孢哌酮1.7小时、舒巴坦1小时。",
    
    "precautions": "①青霉素过敏者慎用（交叉过敏率5-10%）；②用药前询问过敏史；③肝肾功能减退者调整剂量；④长期用药补充维生素K并监测凝血酶原时间；⑤用药期间禁酒；⑥可导致Coombs试验阳性及尿糖假阳性。",
    
    "black_box_warning": "<strong>严重出血风险</strong>：可致致死性出血，需监测出血、血小板减少和凝血障碍，不明原因持续出血应立即停药。营养不良、吸收不良、长期静脉营养及抗凝治疗者需补充维生素K。"
}

def load_drugs():
    """加载药品数据"""
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

def save_drugs(drugs):
    """保存药品数据"""
    js_content = 'const DRUGS_DATA = ' + json.dumps(drugs, ensure_ascii=False, indent=2) + ';'
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

def update_cefoperazone_nacl(drugs):
    """更新头孢哌酮钠舒巴坦钠/氯化钠的内容"""
    updated_count = 0
    
    for drug in drugs:
        name = drug.get('name', '')
        
        # 匹配头孢哌酮钠舒巴坦钠/氯化钠
        if '头孢哌酮' in name and '舒巴坦' in name and '氯化钠' in name:
            manual = drug.get('manual', {})
            
            # 更新精简版内容
            for key, value in CEFOPERAZONE_NACL_SUMMARY.items():
                manual[key] = value
            
            # 更新完整版内容
            for key, value in CEFOPERAZONE_NACL_FULL.items():
                full_key = f'full_{key}'
                manual[full_key] = value
            
            drug['manual'] = manual
            updated_count += 1
            print(f"✓ 已更新: {name}")
    
    return drugs, updated_count

def main():
    print("=" * 60)
    print("更新头孢哌酮钠舒巴坦钠/氯化钠的内容")
    print("数据来源: https://www.hnysfww.com/goods.php?id=1944")
    print("=" * 60)
    
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    drugs, updated_count = update_cefoperazone_nacl(drugs)
    
    print(f"\n共更新 {updated_count} 个条目")
    
    save_drugs(drugs)
    print(f"✅ 数据已保存")

if __name__ == '__main__':
    main()
