#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新抗生素药品信息 - 第四批（特殊标记药品）
"""

import json
from pathlib import Path

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 第四批抗生素药品数据（特殊标记药品）
ANTIBIOTICS_DATA = {
    757: {
        "name": "※▲盐酸莫西沙星氯化钠",
        "indications": "适用于敏感细菌引起的感染，如急性细菌性鼻窦炎、慢性支气管炎急性细菌性感染、社区获得性肺炎、非复杂性皮肤和皮肤软组织感染、复杂性皮肤和皮肤软组织感染、复杂性腹腔内感染、鼠疫、不伴有输卵管-卵巢或盆腔脓肿的轻至中度盆腔炎性疾病等。",
        "full_indications": "本品适用于敏感细菌引起的下列感染：<br>1.急性细菌性鼻窦炎。<br>2.慢性支气管炎急性细菌性感染。<br>3.社区获得性肺炎（包括由多重耐药菌株引起的社区获得性肺炎）。<br>4.非复杂性皮肤和皮肤软组织感染。<br>5.复杂性皮肤和皮肤软组织感染。<br>6.复杂性腹腔内感染。<br>7.鼠疫（包括肺炎型和腺鼠疫）。<br>8.不伴有输卵管-卵巢或盆腔脓肿的轻至中度盆腔炎性疾病。",
        "dosage": "静脉滴注：成人400mg/日，一次给药。疗程根据感染类型而定。",
        "full_dosage": "静脉滴注：<br>⑴成人常用量：<br>①一般感染：400mg/日，一次给药。<br>②急性细菌性鼻窦炎：400mg/日，一次给药，疗程10-14天。<br>③慢性支气管炎急性细菌性感染：400mg/日，一次给药，疗程5天。<br>④社区获得性肺炎：400mg/日，一次给药，疗程7-14天。<br>⑤非复杂性皮肤和皮肤软组织感染：400mg/日，一次给药，疗程7-10天。<br>⑥复杂性皮肤和皮肤软组织感染：400mg/日，一次给药，疗程7-21天。<br>⑦复杂性腹腔内感染：400mg/日，一次给药，疗程5-14天。<br>⑧鼠疫：400mg/日，一次给药，疗程10-14天。<br>⑨盆腔炎性疾病：400mg/日，一次给药，疗程14天。<br><br>⑵肾功能减退患者：肌酐清除率≤30ml/min时，剂量调整为400mg/次，每24小时一次。<br><br>⑶给药说明：<br>①静脉滴注时间不少于60分钟。<br>②本品可直接静脉滴注，无需稀释。<br>③本品仅供静脉滴注，不可静脉推注。<br>④可转换为口服莫西沙星片继续治疗。",
        "contraindications": "对莫西沙星或其他喹诺酮类过敏者禁用。妊娠及哺乳期妇女禁用。18岁以下青少年儿童禁用。",
        "full_contraindications": "1.对莫西沙星或其他喹诺酮类过敏者禁用。<br>2.妊娠及哺乳期妇女禁用。<br>3.18岁以下青少年儿童禁用。<br>4.有肌腱疾病史或发生过肌腱断裂的患者禁用。<br>5.有周围神经病变史的患者禁用。<br>6.有重症肌无力史的患者禁用。<br>7.有QT间期延长或合用可延长QT间期药物的患者禁用。<br>8.对本品任何一种成分过敏者禁用。",
        "adverse_reactions": "胃肠道反应：恶心、腹泻、腹痛。中枢神经系统反应：头痛、头晕、失眠。过敏反应：皮疹、瘙痒。肌腱炎和肌腱断裂。周围神经病变。QT间期延长。肝功能异常。主动脉瘤和主动脉夹层的风险。",
        "full_adverse_reactions": "1.胃肠道反应：恶心、腹泻、腹痛、呕吐、消化不良、便秘。<br>2.中枢神经系统反应：头痛、头晕、失眠、嗜睡、焦虑、震颤、精神错乱、幻觉、抽搐。<br>3.过敏反应：皮疹、荨麻疹、瘙痒、药物热、血管性水肿、过敏性休克。<br>4.肌腱炎和肌腱断裂：疼痛、肿胀、炎症、断裂，尤其见于老年人、合用糖皮质激素者、肾移植患者。<br>5.周围神经病变：感觉异常、麻木、刺痛、烧灼感、无力。<br>6.QT间期延长：可能导致心律失常。<br>7.肝功能异常：转氨酶升高、胆红素升高、肝衰竭。<br>8.血液系统：白细胞减少、血小板减少、贫血。<br>9.其他：光敏反应、血糖紊乱、肾功能异常、二重感染等。<br>10.主动脉瘤和主动脉夹层的风险。<br><br>严重不良反应：<br>1.肌腱断裂：可能致残。<br>2.周围神经病变：可能不可逆。<br>3.严重心律失常：QT间期延长所致。<br>4.过敏性休克。<br>5.肝衰竭。<br>6.严重皮肤反应：Stevens-Johnson综合征、中毒性表皮坏死松解症。<br>7.中枢神经系统效应：抽搐、颅内压升高。<br>8.主动脉瘤和主动脉夹层。",
        "interactions": "与抗酸药、铁剂、锌剂合用可减少吸收。与华法林合用可能增加出血风险。与非甾体抗炎药合用可能增加中枢神经系统刺激和惊厥风险。与延长QT间期药物合用可能增加心律失常风险。",
        "full_interactions": "1.抗酸药、铁剂、锌剂：合用可减少莫西沙星吸收，应间隔至少4小时服用。<br>2.华法林：合用可能增加出血风险，需监测凝血功能。<br>3.非甾体抗炎药：合用可能增加中枢神经系统刺激和惊厥风险。<br>4.延长QT间期药物（如胺碘酮、索他洛尔、红霉素等）：合用可能增加QT间期延长和心律失常风险。<br>5.茶碱：合用可能使茶碱血药浓度升高。<br>6.降糖药：合用可能引起血糖紊乱（高血糖或低血糖）。<br>7.糖皮质激素：合用可能增加肌腱炎和肌腱断裂风险。<br>8.丙磺舒：合用可能增加莫西沙星血药浓度。<br>9.环孢素：合用可能增加环孢素血药浓度。",
        "pregnancy_category": "C级",
        "full_pregnancy_category": "C级。动物实验显示本品对胎儿有不良影响。妊娠期间禁用。本品可分泌至乳汁中，哺乳期妇女禁用。",
        "pharmacokinetics": "静脉滴注后血药浓度迅速达峰。血浆蛋白结合率约50%。分布广泛，在肺组织、上皮衬液、皮肤、软组织、骨骼、关节液中浓度较高，可透过胎盘和血脑屏障。主要以原形经肝脏代谢和肾脏排泄，t1/2约12小时。",
        "full_pharmacokinetics": "静脉滴注后血药浓度迅速达峰，峰浓度约为4.5mg/L（剂量400mg时）。血浆蛋白结合率约50%。<br>分布广泛，在肺组织、上皮衬液、皮肤、软组织、骨骼、关节液、前列腺、扁桃体、子宫、输卵管、卵巢、胆汁、唾液中均可达到有效浓度，可透过胎盘，脑膜炎症时可透过血脑屏障。<br>代谢和排泄：在肝脏部分代谢，主要经肾脏排泄（约45%原形，约25%代谢物），以及经胆汁和粪便排泄（约25%）。消除半衰期成人为12小时，肾功能减退时半衰期延长，肝功能减退时半衰期无明显变化。血液透析可清除部分药物。",
        "precautions": "1.警告：全身用氟喹诺酮类药品的严重不良反应。2.有中枢神经系统疾病史者慎用。3.肾功能减退者需调整剂量。4.肝功能减退者慎用。5.用药期间避免过度日晒。6.糖尿病患者使用时需注意血糖监测。7.老年患者使用时应监测肾功能。8.运动员慎用。9.用药期间避免驾驶和操作机器。10.主动脉瘤和主动脉夹层的风险。",
        "full_precautions": "1.警告：全身用氟喹诺酮类药品的严重不良反应，包括肌腱炎和肌腱断裂、周围神经病变、中枢神经系统的影响和重症肌无力加剧。<br>2.有中枢神经系统疾病史者：慎用，因可能降低惊厥阈值。<br>3.肾功能减退者：需调整剂量，并监测肾功能。<br>4.肝功能减退者：慎用，需监测肝功能。<br>5.用药期间避免过度日晒：可能引起光敏反应。<br>6.糖尿病患者：使用时需注意血糖监测，可能出现血糖紊乱。<br>7.老年患者：使用时应监测肾功能，老年人更易发生肌腱炎和肌腱断裂。<br>8.运动员：慎用。<br>9.用药期间避免驾驶和操作机器：可能出现头晕、嗜睡等。<br>10.有QT间期延长风险因素者：慎用，需监测心电图。<br>11.本品可能引起二重感染，长期用药需警惕。<br>12.本品仅供静脉滴注，不可静脉推注。<br>13.主动脉瘤和主动脉夹层的风险：有主动脉瘤或主动脉夹层病史者慎用。"
    }
}

def update_drug(drug_id, data):
    """更新单个药品"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {drug_id}.json")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 更新manual字段
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        manual = drug_data['manual']
        manual['indications'] = data['indications']
        manual['full_indications'] = data['full_indications']
        manual['dosage'] = data['dosage']
        manual['full_dosage'] = data['full_dosage']
        manual['contraindications'] = data['contraindications']
        manual['full_contraindications'] = data['full_contraindications']
        manual['adverse_reactions'] = data['adverse_reactions']
        manual['full_adverse_reactions'] = data['full_adverse_reactions']
        manual['interactions'] = data['interactions']
        manual['full_interactions'] = data['full_interactions']
        manual['pregnancy_category'] = data['pregnancy_category']
        manual['full_pregnancy_category'] = data['full_pregnancy_category']
        manual['pharmacokinetics'] = data['pharmacokinetics']
        manual['full_pharmacokinetics'] = data['full_pharmacokinetics']
        manual['precautions'] = data['precautions']
        manual['full_precautions'] = data['full_precautions']
        manual['source'] = "湖南药事服务网"
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ ID {drug_id} ({data['name']}) 更新成功")
        return True
        
    except Exception as e:
        print(f"❌ ID {drug_id}: 错误 - {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("批量更新抗生素药品信息 - 第四批（特殊标记药品）")
    print("=" * 80)
    
    success_count = 0
    
    for drug_id, data in ANTIBIOTICS_DATA.items():
        if update_drug(drug_id, data):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"处理完成: 成功 {success_count}/{len(ANTIBIOTICS_DATA)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
