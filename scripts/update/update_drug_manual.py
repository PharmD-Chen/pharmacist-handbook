#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动更新药品详细信息工具
"""

import os
import json

DRUGS_DIR = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'

def update_drug_manual(drug_id, manual_data):
    """更新药品manual字段"""
    json_path = os.path.join(DRUGS_DIR, f'{drug_id}.json')
    
    if not os.path.exists(json_path):
        print(f"❌ 药品文件不存在: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 确保manual字段存在
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        # 更新数据
        drug_data['manual'].update(manual_data)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 药品 {drug_id} 更新成功")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

# 示例：更新非那雄胺的信息
def update_finasteride():
    """更新非那雄胺"""
    manual_data = {
        "indications": "1. 治疗和控制良性前列腺增生以及预防泌尿系统事件；2. 治疗男性秃发（雄激素性秃发），能促进头发生长并防止继续脱发。",
        "full_indications": "1. 本品适用于治疗和控制良性前列腺增生（BPH）以及预防泌尿系统事件：降低发生急性尿潴留的危险性；降低需进行经尿道切除前列腺（TURP）和前列腺切除术的危险性。\n2. 本品可使肥大的前列腺缩小，改善尿流及改善前列腺增生有关的症状。前列腺肥大患者适用于本品治疗。\n3. 治疗男性秃发（雄激素性秃发），能促进头发生长并防止继续脱发。",
        "dosage": "口服。建议每次5毫克（1片），每天1次，空腹服用或与食物同时服用均可。",
        "full_dosage": "口服。\n\n良性前列腺增生：\n建议每次5毫克（1片），每天1次，空腹服用或与食物同时服用均可。\n\n男性秃发：\n建议每次1毫克（1片），每天1次，空腹服用或与食物同时服用均可。",
        "contraindications": "本品不适用于妇女和儿童。对本品任何成分过敏者禁用。妊娠妇女不得触摸本品的碎片和裂片。",
        "full_contraindications": "1. 本品不适用于妇女和儿童。\n2. 对本品任何成分过敏者禁用。\n3. 妊娠妇女不得触摸本品的碎片和裂片，否则可能引起男性胎儿外生殖器异常。",
        "adverse_reactions": "主要有性功能受影响（阳痿、性欲减退、射精障碍）、乳腺不适（乳腺增大、乳腺疼痛）和皮疹。",
        "full_adverse_reactions": "1. 性功能受影响：阳痿、性欲减退、射精障碍、射精量减少。\n2. 乳腺不适：乳腺增大、乳腺疼痛。\n3. 过敏反应：皮疹、瘙痒、荨麻疹和口唇肿胀。\n4. 睾丸疼痛。\n5. 上述不良反应在停止治疗后通常会消失。",
        "interactions": "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用，使用过程中注意观察不良反应。",
        "full_interactions": "1. 尚未确定具有临床重要意义的药物相互作用。\n2. 本品对细胞色素P450相关的药物代谢酶系统没有明显影响。\n3. 在男性中已被检测的化合物有普萘洛尔、地高辛、格列本脲、华法林、茶碱和安替比林，它们均未发现与本品有临床意义的相互作用。",
        "pregnancy_category": "X级（妊娠妇女禁用）",
        "precautions": "1. 使用本品前应排除其他类似良性前列腺增生（BPH）的疾病；2. 本品主要在肝脏代谢，肝功能不全者慎用；3. 治疗前期可能会出现症状加重；4. 建议在治疗前后定期评估前列腺状况。",
        "full_precautions": "1. 使用本品前应排除其他类似良性前列腺增生（BPH）的疾病，如感染、前列腺癌、尿道狭窄、膀胱低张力、神经源性紊乱等。\n2. 本品主要在肝脏代谢，肝功能不全者慎用。\n3. 治疗前期可能会出现症状加重，如排尿困难加重。\n4. 建议在治疗前后定期评估前列腺状况，包括直肠指检和前列腺特异性抗原（PSA）检测。\n5. 对于有大量残留尿和/或严重尿流减少的患者，应该密切监测其堵塞性尿道疾病。\n6. 本品可能影响PSA水平，医生应了解这一点。",
        "source": "湖南药事服务网"
    }
    
    return update_drug_manual(811, manual_data)

if __name__ == '__main__':
    # 可以在这里添加更多药品的更新
    update_finasteride()
