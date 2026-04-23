#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新奥美沙坦酯氨氯地平片信息
修正基本信息错误并补充详细内容
"""

import json
from pathlib import Path

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"

def update_drug():
    """更新奥美沙坦酯氨氯地平片"""
    drug_id = 349
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        print(f"❌ 药品文件不存在: {json_path}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    # 修正基本信息
    # 规格：每片含奥美沙坦酯20mg和苯磺酸氨氯地平5mg
    drug_data['specifications'][0]['specification'] = "奥美沙坦酯20mg+苯磺酸氨氯地平5mg/片"
    
    # 标记为临时采购药品
    drug_data['purchase_type'] = '临时采购'
    
    # 更新manual字段 - 精简版和详细版
    drug_data['manual'] = {
        # 精简版
        "indications": "用于原发性高血压。",
        
        "dosage": "口服：成人每日1次，每次1片，建议每日同一时间用水吞服。",
        
        "contraindications": "对本品过敏者禁用。孕妇、哺乳期妇女禁用。重度肾损伤、重度肝损伤者禁用。",
        
        "adverse_reactions": "常见：外周水肿、头痛、头晕。偶见：低血压、心悸、消化不良、肝酶升高、皮疹。",
        
        "interactions": "与利尿剂、其他降压药合用可能增强降压效果。与保钾利尿剂、补钾药合用可能增加高钾血症风险。",
        
        "pregnancy_category": "禁用（妊娠中晚期使用可导致胎儿损伤甚至死亡）",
        
        "pharmacokinetics": "奥美沙坦酯：口服后迅速水解为活性代谢物奥美沙坦，达峰时间1-2小时，半衰期约13小时。氨氯地平：达峰时间6-12小时，半衰期35-50小时。",
        
        "precautions": "用药期间监测血压、肾功能与电解质。轻中度肾损伤患者每日最大剂量20mg。中度肝损伤者起始剂量10mg/日。",
        
        # 详细版
        "full_indications": "本品适用于治疗原发性高血压。本品为复方制剂，包含血管紧张素Ⅱ受体拮抗剂（ARB）奥美沙坦酯和钙通道阻滞剂（CCB）氨氯地平两种降压成分，两种成分作用机制互补，可协同降压。",
        
        "full_dosage": "口服。成人推荐剂量为每日1次，每次1片（含奥美沙坦酯20mg和苯磺酸氨氯地平5mg），建议每日同一时间用水吞服。根据患者临床反应，剂量可增加至每日1次，每次2片。老年患者通常无需调整剂量，但剂量增加时需谨慎。轻中度肾损伤患者每日最大剂量为奥美沙坦酯20mg。中度肝损伤患者建议起始剂量为奥美沙坦酯10mg/日，最大不超过20mg/日。",
        
        "full_contraindications": "对奥美沙坦酯、氨氯地平或本品任何成分过敏者禁用。孕妇禁用（妊娠中晚期使用血管紧张素抑制剂可导致胎儿损伤甚至死亡）。哺乳期妇女禁用。重度肾损伤患者禁用。重度肝损伤患者禁用。",
        
        "full_adverse_reactions": "常见不良反应：外周水肿、头痛、头晕。偶见不良反应：低血压、心悸、消化不良、肝酶升高、皮疹、疲劳、恶心。罕见不良反应：血管性水肿、急性肾损伤、高钾血症。",
        
        "full_interactions": "与利尿剂或其他降压药合用可能增强降压效果，需监测血压。与保钾利尿剂、补钾药、含钾盐替代品合用可能增加高钾血症风险，需监测血钾。与锂剂合用可能增加锂中毒风险。与非甾体抗炎药合用可能减弱降压效果并增加肾功能损害风险。",
        
        "full_pharmacokinetics": "奥美沙坦酯：口服后迅速水解为活性代谢物奥美沙坦，绝对生物利用度约26%，达峰时间（Tmax）1-2小时，血浆蛋白结合率约99%，半衰期约13小时，主要经粪便（约50%）和尿液（约40%）排泄。氨氯地平：口服后缓慢吸收，绝对生物利用度约64-90%，达峰时间（Tmax）6-12小时，血浆蛋白结合率约93%，半衰期35-50小时，主要经肝脏代谢，经尿液排泄。",
        
        "full_precautions": "用药期间需定期监测血压、肾功能与电解质，注意高钾血症风险。轻中度肾损伤患者每日最大剂量为奥美沙坦酯20mg，重度肾损伤患者禁用。中度肝损伤患者建议起始剂量为奥美沙坦酯10mg/日，最大不超过20mg/日，重度肝损伤患者禁用。老年患者通常无需调整剂量，但剂量增加时需谨慎。血容量不足患者（如大剂量利尿剂治疗者）可能出现症状性低血压，需纠正血容量后再使用本品。主动脉瓣或二尖瓣狭窄、肥厚型心肌病患者慎用。",
        
        "source": "湖南药事服务网",
        "url_added": True
    }
    
    # 添加网址信息
    drug_data['url'] = {
        "hnysfww": "https://www.hnysfww.com/goods.php?id=280",
        "last_updated": "2026-03-20"
    }
    
    # 保存
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新奥美沙坦酯氨氯地平片 [ID: {drug_id}]")
    print(f"   - 规格已修正：奥美沙坦酯20mg+苯磺酸氨氯地平5mg/片")
    print(f"   - 已标记为临时采购药品")
    print(f"   - 已补充完整的手册信息（精简版+详细版）")
    print(f"   - 已添加湖南药事服务网网址")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("更新奥美沙坦酯氨氯地平片信息")
    print("=" * 60)
    update_drug()
    print("=" * 60)
