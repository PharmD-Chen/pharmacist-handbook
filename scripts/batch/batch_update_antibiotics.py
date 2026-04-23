#!/usr/bin/env python3
"""
批量更新抗生素药品信息
"""

import json
from pathlib import Path

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 抗生素药品数据
ANTIBIOTICS_DATA = {
    439: {
        "name": "克林霉素磷酸酯",
        "indications": "适用于革兰阳性菌和厌氧菌引起的各种感染，如呼吸道感染、泌尿系统感染、腹腔感染、皮肤软组织感染、骨和关节感染、败血症、心内膜炎等。",
        "full_indications": "本品适用于革兰阳性菌和厌氧菌引起的各种感染性疾病：<br>1.呼吸道感染：急性支气管炎、慢性支气管炎急性发作、肺炎、肺脓肿等。<br>2.泌尿系统感染：急性尿道炎、急性肾盂肾炎、前列腺炎等。<br>3.腹腔感染：腹膜炎、腹腔脓肿等。<br>4.皮肤软组织感染：疖、痈、蜂窝织炎、创伤和手术后感染等。<br>5.骨和关节感染：骨髓炎、化脓性关节炎等。<br>6.败血症、心内膜炎等。<br>7.口腔感染：牙周炎、冠周炎等。<br>8.妇科感染：子宫内膜炎、盆腔炎等。",
        "dosage": "肌内注射或静脉滴注：成人0.6-1.2g/日，分2-4次给药。严重感染可增至1.2-2.4g/日。",
        "full_dosage": "肌内注射或静脉滴注：<br>⑴成人常用量：<br>①一般感染：0.6-1.2g/日，分2-4次给药。<br>②严重感染：1.2-2.4g/日，分2-4次给药。<br>③危及生命感染：可增至4.8g/日，分3-4次给药。<br><br>⑵儿童常用量：<br>①一般感染：15-25mg/kg/日，分3-4次给药。<br>②严重感染：25-40mg/kg/日，分3-4次给药。<br><br>⑶给药说明：<br>①肌内注射：每0.6g用注射用水或生理盐水3ml溶解，深部肌内注射。<br>②静脉滴注：每0.6g用生理盐水或5%葡萄糖注射液100ml稀释，滴注时间不少于20分钟。<br>③本品不能静脉推注。",
        "contraindications": "对克林霉素或林可霉素过敏者禁用。",
        "full_contraindications": "1.对克林霉素或林可霉素过敏者禁用。<br>2.对本品任何一种成分过敏者禁用。",
        "adverse_reactions": "胃肠道反应：恶心、呕吐、腹痛、腹泻，严重者可出现伪膜性肠炎。过敏反应：皮疹、瘙痒、药物热。肝功能异常：转氨酶升高。血液系统：白细胞减少、血小板减少。局部反应：注射部位疼痛、静脉炎。",
        "full_adverse_reactions": "1.胃肠道反应：最常见，包括恶心、呕吐、腹痛、腹泻，严重者可出现伪膜性肠炎（难辨梭菌相关性腹泻），表现为严重腹泻、腹痛、发热，可能危及生命。<br>2.过敏反应：皮疹、荨麻疹、瘙痒、药物热、嗜酸性粒细胞增多，罕见过敏性休克。<br>3.肝功能异常：转氨酶升高、黄疸，罕见肝衰竭。<br>4.血液系统：白细胞减少、中性粒细胞减少、血小板减少、再生障碍性贫血。<br>5.局部反应：注射部位疼痛、硬结、静脉炎。<br>6.其他：头晕、耳鸣、呼吸困难、心悸等。<br><br>严重不良反应：<br>1.伪膜性肠炎：可能危及生命。<br>2.过敏性休克：罕见但严重。<br>3.严重皮肤反应：Stevens-Johnson综合征、中毒性表皮坏死松解症。<br>4.肝衰竭。",
        "interactions": "与红霉素有拮抗作用，不宜合用。与神经肌肉阻滞剂合用可能增强神经肌肉阻滞作用。与阿片类镇痛药合用可能加重呼吸抑制。",
        "full_interactions": "1.红霉素：有拮抗作用，不宜合用。<br>2.神经肌肉阻滞剂：合用可能增强神经肌肉阻滞作用。<br>3.阿片类镇痛药：合用可能加重呼吸抑制。<br>4.抗腹泻药：止泻药可能延迟毒素排出，加重伪膜性肠炎。<br>5.肝药酶诱导剂（如苯巴比妥）：可能降低克林霉素血药浓度。<br>6.肝药酶抑制剂（如西咪替丁）：可能增加克林霉素血药浓度。<br>7.卡马西平：克林霉素可能抑制卡马西平代谢，增加其血药浓度。<br>8.华法林：可能增强华法林的抗凝作用。<br>9.氨基糖苷类抗生素：合用对某些革兰阳性菌有协同作用。",
        "pregnancy_category": "B级",
        "full_pregnancy_category": "B级。动物实验显示本品对胎儿无危害，但缺乏人类妊娠期使用的充分研究。妊娠期间仅在明确需要时使用。本品可分泌至乳汁中，哺乳期妇女使用时应暂停哺乳。",
        "pharmacokinetics": "肌内注射后血药浓度达峰时间为3小时左右，静脉滴注后即刻达峰。血浆蛋白结合率约90%。分布广泛，在骨组织、胆汁、尿液中浓度较高，可透过胎盘和血脑屏障（脑膜炎症时）。在肝脏代谢，主要经胆汁和粪便排泄，t1/2约2-3小时。",
        "full_pharmacokinetics": "肌内注射后血药浓度达峰时间为3小时左右，静脉滴注后即刻达峰。血浆蛋白结合率约90%。<br>分布广泛，在骨组织、胆汁、尿液、痰液、胸水、腹水、唾液、扁桃体中均可达到有效浓度，可透过胎盘，脑膜炎症时可透过血脑屏障。<br>代谢和排泄：在肝脏代谢为活性代谢物，主要经胆汁和粪便排泄（约70%），尿中排泄约10%。消除半衰期成人为2-3小时，肾功能减退时半衰期延长不明显，但肝功能减退时半衰期延长。血液透析和腹膜透析不能有效清除本品。",
        "precautions": "1.警惕伪膜性肠炎，出现严重腹泻应立即停药。2.肝功能减退者慎用。3.严重肾功能减退者慎用。4.孕妇慎用。5.哺乳期妇女慎用。6.新生儿慎用。7.不宜与红霉素合用。",
        "full_precautions": "1.警惕伪膜性肠炎：用药期间如出现严重腹泻、腹痛、发热等症状，应立即停药并就医。<br>2.肝功能减退者：慎用，需监测肝功能。<br>3.严重肾功能减退者：慎用，需调整剂量。<br>4.孕妇：慎用。<br>5.哺乳期妇女：慎用，使用时应暂停哺乳。<br>6.新生儿：慎用，因肝脏代谢功能不完善。<br>7.不宜与红霉素合用。<br>8.用药期间应定期监测血常规和肝功能。<br>9.本品不能静脉推注，只能肌内注射或静脉滴注。<br>10.静脉滴注速度不宜过快，以免引起低血压、心动过速等。"
    },
    658: {
        "name": "注射用头孢地嗪钠/5%葡萄糖",
        "indications": "适用于敏感菌引起的各种感染，如呼吸道感染、泌尿系统感染、胆道感染、腹腔感染、皮肤软组织感染、骨和关节感染、败血症、心内膜炎等。",
        "full_indications": "本品适用于敏感菌引起的各种感染性疾病：<br>1.呼吸道感染：急性支气管炎、慢性支气管炎急性发作、肺炎、肺脓肿、支气管扩张合并感染等。<br>2.泌尿系统感染：急性肾盂肾炎、膀胱炎、尿道炎、前列腺炎等。<br>3.胆道感染：胆囊炎、胆管炎等。<br>4.腹腔感染：腹膜炎、腹腔脓肿等。<br>5.皮肤软组织感染：蜂窝织炎、伤口感染、烧伤感染等。<br>6.骨和关节感染：骨髓炎、化脓性关节炎等。<br>7.败血症、感染性心内膜炎等。<br>8.其他感染：中耳炎、鼻窦炎、扁桃体炎等。",
        "dosage": "静脉滴注：成人1-2g/次，每12小时一次，严重感染可增至4g/次，每12小时一次。",
        "full_dosage": "静脉滴注：<br>⑴成人常用量：<br>①一般感染：1g/次，每12小时一次。<br>②中度感染：2g/次，每12小时一次。<br>③严重感染：4g/次，每12小时一次。<br><br>⑵儿童常用量：<br>①一般感染：60-80mg/kg/日，分2次给药。<br>②严重感染：100-120mg/kg/日，分2次给药。<br><br>⑶肾功能减退患者：根据肌酐清除率调整剂量和给药间隔。<br><br>⑷给药说明：<br>①本品为预混型制剂，直接使用，无需稀释。<br>②静脉滴注时间30-60分钟。<br>③本品仅供静脉滴注，不可静脉推注。",
        "contraindications": "对头孢地嗪或其他头孢菌素类过敏者禁用。",
        "full_contraindications": "1.对头孢地嗪或其他头孢菌素类过敏者禁用。<br>2.有青霉素过敏性休克史者禁用。<br>3.对本品任何一种成分过敏者禁用。",
        "adverse_reactions": "过敏反应：皮疹、瘙痒、药物热。胃肠道反应：恶心、腹泻、腹痛。肝功能异常：转氨酶升高。血液系统：白细胞减少、血小板减少。局部反应：注射部位疼痛、静脉炎。",
        "full_adverse_reactions": "1.过敏反应：皮疹、荨麻疹、瘙痒、药物热、嗜酸性粒细胞增多，罕见过敏性休克。<br>2.胃肠道反应：恶心、呕吐、腹泻、腹痛，罕见伪膜性肠炎。<br>3.肝功能异常：转氨酶升高、碱性磷酸酶升高、胆红素升高。<br>4.血液系统：白细胞减少、中性粒细胞减少、血小板减少、溶血性贫血。<br>5.局部反应：注射部位疼痛、硬结、静脉炎。<br>6.其他：头晕、头痛、味觉异常、二重感染等。<br><br>严重不良反应：<br>1.过敏性休克：罕见但严重。<br>2.严重皮肤反应：Stevens-Johnson综合征、中毒性表皮坏死松解症。<br>3.急性肾衰竭。<br>4.溶血性贫血。<br>5.伪膜性肠炎。",
        "interactions": "与氨基糖苷类抗生素合用可能增加肾毒性。与强效利尿剂合用可能增加肾毒性。与抗凝药合用可能增加出血风险。",
        "full_interactions": "1.氨基糖苷类抗生素：合用可能增加肾毒性，需监测肾功能。<br>2.强效利尿剂（如呋塞米）：合用可能增加肾毒性。<br>3.抗凝药（如华法林）：合用可能增加出血风险，需监测凝血功能。<br>4.丙磺舒：合用可延长头孢地嗪的半衰期，增加血药浓度。<br>5.含铝或镁的抗酸药：可能减少头孢地嗪的吸收。<br>6.氯霉素：合用可能有拮抗作用。<br>7.酒精：用药期间饮酒可能引起双硫仑样反应。",
        "pregnancy_category": "B级",
        "full_pregnancy_category": "B级。动物实验显示本品对胎儿无危害，但缺乏人类妊娠期使用的充分研究。妊娠期间仅在明确需要时使用。本品可分泌至乳汁中，哺乳期妇女使用时应谨慎。",
        "pharmacokinetics": "静脉滴注后血药浓度迅速达峰。血浆蛋白结合率约80%。分布广泛，在组织液、痰液、腹水、胆汁、尿液中浓度较高，可透过胎盘和血脑屏障（脑膜炎症时）。主要以原形经肾脏排泄，t1/2约2-3小时。",
        "full_pharmacokinetics": "静脉滴注后血药浓度迅速达峰。血浆蛋白结合率约80%。<br>分布广泛，在组织液、痰液、腹水、胆汁、尿液、骨组织、子宫组织、脐带血、羊水中均可达到有效浓度，可透过胎盘，脑膜炎症时可透过血脑屏障。<br>代谢和排泄：在体内几乎不代谢，主要以原形经肾小球滤过和肾小管分泌排泄，尿中浓度高。消除半衰期成人为2-3小时，肾功能减退时半衰期延长。血液透析可清除部分药物。",
        "precautions": "1.青霉素过敏者慎用。2.肾功能减退者需调整剂量。3.用药期间监测肾功能。4.长期用药需监测血常规。5.孕妇慎用。6.哺乳期妇女慎用。7.用药期间避免饮酒。",
        "full_precautions": "1.青霉素过敏者：慎用，因头孢菌素与青霉素有交叉过敏反应。<br>2.肾功能减退者：需调整剂量和给药间隔，并监测肾功能。<br>3.用药期间监测肾功能：定期检查尿常规、血肌酐、血尿素氮。<br>4.长期用药：需定期监测血常规和肝功能。<br>5.孕妇：慎用。<br>6.哺乳期妇女：慎用。<br>7.用药期间避免饮酒：可能引起双硫仑样反应。<br>8.本品可能引起二重感染，长期用药需警惕。<br>9.本品仅供静脉滴注，不可静脉推注。"
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
    print("批量更新抗生素药品信息")
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
