#!/usr/bin/env python3
"""
为10个中成药补充说明书内容
"""
import json
from pathlib import Path

DRUGS_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 10个需要补充的中成药
tcm_drugs = [
    (843, "丹参片", "片"),
    (686, "养血安神片", "片"),
    (897, "丹参酮胶囊", "胶囊"),
    (824, "枣仁安神胶囊", "胶囊"),
    (521, "苏黄止咳胶囊", "胶囊"),
    (891, "脑心通胶囊", "胶囊"),
    (845, "血塞通胶囊", "胶囊"),
    (846, "血脂康胶囊", "胶囊"),
    (139, "银杏叶胶囊", "胶囊"),
    (516, "参松养心胶囊", "胶囊"),
]

def update_tcm_manual(drug_id, drug_name, dosage_form):
    """更新中成药说明书内容"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        print(f"❌ 药品文件不存在: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 检查是否有manual字段
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        manual = drug_data['manual']
        
        # 根据药品名称更新特定内容
        if drug_id == 843:  # 丹参片
            manual['indications'] = "活血化瘀。用于瘀血闭阻所致的胸痹，症见胸部疼痛、痛处固定、舌质紫暗；冠心病心绞痛见上述证候者。"
            manual['dosage'] = "口服：一次3-4片，一日3次。"
            manual['contraindications'] = "孕妇禁用。对本品过敏者禁用。"
            manual['adverse_reactions'] = "尚不明确。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "忌食生冷、辛辣、油腻食物。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 686:  # 养血安神片
            manual['indications'] = "滋阴养血，宁心安神。用于阴虚血少所致的头眩心悸、失眠健忘。"
            manual['dosage'] = "口服：一次5片，一日3次。"
            manual['contraindications'] = "对本品过敏者禁用。"
            manual['adverse_reactions'] = "尚不明确。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "⑴忌烟、酒及辛辣、油腻食物。⑵服药期间要保持情绪乐观，切忌生气恼怒。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 897:  # 丹参酮胶囊
            manual['indications'] = "抗菌消炎。用于痤疮、扁桃腺炎、外耳道炎、疖、痈、外伤感染、烧伤感染、乳腺炎、蜂窝组织炎等。"
            manual['dosage'] = "口服：一次4粒，一日3-4次。小儿酌减。"
            manual['contraindications'] = "对本品过敏者禁用。"
            manual['adverse_reactions'] = "偶见皮肤过敏反应，停药后可恢复正常。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "孕妇慎用。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 824:  # 枣仁安神胶囊
            manual['indications'] = "养血安神。用于心血不足所致的失眠、健忘、心烦、头晕；神经衰弱症见上述证候者。"
            manual['dosage'] = "口服：一次5粒，一日1次，临睡前服用。"
            manual['contraindications'] = "对本品过敏者禁用。"
            manual['adverse_reactions'] = "尚不明确。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "⑴孕妇慎用。⑵由于消化不良所导致的睡眠差者忌用。⑶按照用法用量服用，糖尿病患者、小儿应在医师指导下服用。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 521:  # 苏黄止咳胶囊
            manual['indications'] = "疏风宣肺，止咳利咽。用于风邪犯肺、肺气失宣所致的咳嗽、咽痒、痒时咳嗽，或呛咳阵作，气急、遇冷空气、异味等因素突发或加重，或夜卧晨起咳剧，多呈反复性发作，干咳无痰或少痰，舌苔薄白等；感冒后咳嗽及咳嗽变异型哮喘见上述证候者。"
            manual['dosage'] = "口服：一次3粒，一日3次。疗程7-14天。"
            manual['contraindications'] = "对本品过敏者禁用。"
            manual['adverse_reactions'] = "偶见恶心、呕吐、胃部不适、便秘、咽干。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "⑴运动员慎用。⑵尚无研究数据表明本品对外感发热、咽炎、慢性阻塞性肺疾病、肺癌等疾病引起的咳嗽有效。⑶尚无研究数据支持本品可用于65岁以上和18岁以下患者，以及妊娠期或哺乳期妇女。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 891:  # 脑心通胶囊
            manual['indications'] = "益气活血，化瘀通络。用于气虚血滞、脉络瘀阻所致中风中经络，半身不遂、肢体麻木、口眼歪斜、舌强语謇及胸痹心痛、胸闷、心悸、气短；脑梗塞、冠心病心绞痛属上述证候者。"
            manual['dosage'] = "口服：一次2-4粒，一日3次。"
            manual['contraindications'] = "对本品过敏者禁用。孕妇禁用。"
            manual['adverse_reactions'] = "尚不明确。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "胃病患者饭后服用。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 845:  # 血塞通胶囊
            manual['indications'] = "活血祛瘀，通脉活络，抑制血小板聚集和增加脑血流量。用于脑络瘀阻，中风偏瘫，心脉瘀阻，胸痹心痛；脑血管病后遗症，冠心病心绞痛属上述证候者。"
            manual['dosage'] = "口服：一次100mg，一日3次。"
            manual['contraindications'] = "对本品过敏者禁用。孕妇禁用。"
            manual['adverse_reactions'] = "偶见过敏性皮疹、胃肠不适。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "孕妇慎用。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 846:  # 血脂康胶囊
            manual['indications'] = "除湿祛痰，活血化瘀，健脾消食。用于脾虚痰瘀阻滞症的气短、乏力、头晕、头痛、胸闷、腹胀、食少纳呆等；高脂血症；也可用于由高脂血症及动脉粥样硬化引起的心脑血管疾病的辅助治疗。"
            manual['dosage'] = "口服：一次2粒，一日2次，早晚饭后服用；轻、中度患者一日2粒，晚饭后服用。"
            manual['contraindications'] = "对本品过敏者禁用。活动性肝炎或无法解释的血清氨基转移酶升高者禁用。"
            manual['adverse_reactions'] = "常见：胃肠道不适（胃痛、腹胀、胃部灼热）。少见：血清氨基转移酶和肌酸磷酸激酶可逆性升高。罕见：乏力、口干、头晕、头痛、肌痛、皮疹、胆囊疼痛、浮肿、结膜充血和泌尿道刺激症状。"
            manual['interactions'] = "本品有调血脂作用，故与抗凝药合用时应注意调整抗凝药剂量。"
            manual['precautions'] = "⑴用药期间应定期检查血脂、血清氨基转移酶和肌酸磷酸激酶；有肝病史者服用本品尤其要注意肝功能的监测。⑵在本品治疗过程中，如发生血清氨基转移酶增高达正常高限3倍，或血清肌酸磷酸激酶显著增高时，应停用本品。⑶不推荐孕妇及乳母使用。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 139:  # 银杏叶胶囊
            manual['indications'] = "活血化瘀通络。用于瘀血阻络引起的胸痹、心痛、中风、半身不遂、舌强语謇；冠心病稳定型心绞痛、脑梗死见上述证候者。"
            manual['dosage'] = "口服：一次1-2粒，一日3次。"
            manual['contraindications'] = "对本品过敏者禁用。孕妇及哺乳期妇女禁用。"
            manual['adverse_reactions'] = "偶有胃部不适。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "心力衰竭者、孕妇及过敏体质者慎用。"
            manual['pharmacokinetics'] = ""
            
        elif drug_id == 516:  # 参松养心胶囊
            manual['indications'] = "益气养阴，活血通络，清心安神。用于治疗冠心病室性早搏属气阴两虚，心络瘀阻证，症见心悸不安，气短乏力，动则加剧，胸部闷痛，失眠多梦，盗汗，神倦懒言。"
            manual['dosage'] = "口服：一次2-4粒，一日3次。"
            manual['contraindications'] = "对本品过敏者禁用。"
            manual['adverse_reactions'] = "尚不明确。"
            manual['interactions'] = "如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。"
            manual['precautions'] = "孕妇慎用。"
            manual['pharmacokinetics'] = ""
        
        # 设置详细版字段（与精简版相同或更详细）
        for key in ['indications', 'dosage', 'contraindications', 'adverse_reactions', 'interactions', 'precautions', 'pharmacokinetics']:
            full_key = f'full_{key}'
            if key in manual:
                manual[full_key] = manual[key]
        
        # 设置来源
        manual['source'] = "湖南药事服务网"
        manual['url_added'] = True
        
        # 保存更新后的数据
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已更新 {drug_name} [ID: {drug_id}]")
        return True
        
    except Exception as e:
        print(f"❌ 更新 {drug_name} [ID: {drug_id}] 时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始更新10个中成药的说明书内容")
    print("=" * 60)
    
    success_count = 0
    for drug_id, drug_name, dosage_form in tcm_drugs:
        if update_tcm_manual(drug_id, drug_name, dosage_form):
            success_count += 1
    
    print("=" * 60)
    print(f"更新完成: {success_count}/{len(tcm_drugs)} 个中成药")
    print("=" * 60)

if __name__ == "__main__":
    main()
