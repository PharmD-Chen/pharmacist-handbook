#!/usr/bin/env python3
"""
为11个药品规范化手册内容
"""
import json
from pathlib import Path

DRUGS_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 11个需要处理的药品ID和名称
drugs_to_update = [
    (811, "非那雄胺"),
    (523, "丁苯那嗪"),
    (1028, "乙酰唑胺"),
    (589, "二甲双胍恩格列净"),
    (696, "依折麦布阿托伐他汀钙"),
    (784, "咪唑立宾"),
    (576, "恩那度司他"),
    (625, "氢溴酸氘瑞米德韦"),
    (527, "洛拉替尼"),
    (707, "海曲泊帕乙醇胺"),
    (638, "炔雌醇环丙孕酮"),
]

def update_drug_manual(drug_id, drug_name):
    """更新药品手册内容"""
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
        
        # 根据药品ID更新特定内容
        if drug_id == 811:  # 非那雄胺
            manual['indications'] = "用于良性前列腺增生症（BPH），改善尿流及相关症状；治疗男性脱发。"
            manual['dosage'] = "口服：BPH一次5mg/日；男性脱发一次1mg/日。肾功能不全者不需调整剂量。"
            manual['contraindications'] = "妇女和儿童禁用。"
            manual['adverse_reactions'] = "常见：性功能受影响（阳痿、性欲降低、射精障碍）、射精量减少、乳房不适（乳腺增生、乳房触痛）、皮疹。"
            manual['interactions'] = "暂未发现有临床意义的药物相互作用。"
            manual['precautions'] = "⑴PSA监测：治疗3个月以上患者PSA值应乘以2评估。⑵起效缓慢，需3个月左右达最佳效果。⑶性伴侣怀孕或可能怀孕时，避免接触精液或停药。"
            manual['pharmacokinetics'] = "口服生物利用度约80%，达峰时间约2小时，半衰期约6小时，经肝脏代谢。"
            
        elif drug_id == 523:  # 丁苯那嗪
            manual['indications'] = "用于治疗亨廷顿舞蹈症（HD）等运动障碍性疾病。"
            manual['dosage'] = "口服：起始12.5mg/日，每周增加12.5mg，维持剂量50mg/日，分2-3次服用，单次最大25mg。"
            manual['contraindications'] = "孕妇、哺乳期妇女、对本品过敏者、帕金森病患者、肝功能损害患者禁用。"
            manual['adverse_reactions'] = "常见：嗜睡、体位性低血压、锥体外系症状、胃肠不适、抑郁症。超量可致镇静、低血压、低热、出汗。"
            manual['interactions'] = "⑴减弱左旋多巴作用。⑵与MAOI合用可引起精神错乱。⑶CYP2D6抑制剂（奎尼丁、氟西汀、帕罗西汀）可显著增加血药浓度。"
            manual['precautions'] = "⑴用药期间不得驾驶车辆和操作机械。⑵MAOI停用14天后方可使用。⑶不可突然停药，需缓慢减量。"
            manual['pharmacokinetics'] = "口服吸收少且不稳定，广泛首过代谢，半衰期约6.5小时，代谢物经尿排出。"
            
        elif drug_id == 1028:  # 乙酰唑胺
            manual['indications'] = "用于各类青光眼（急性闭角型、开角型、继发性等）降低眼压；内眼手术前后降眼压。"
            manual['dosage'] = "口服：开角型青光眼250mg/次，1-2次/日；急性发作首次500mg，后125-250mg/次，每8小时1次。"
            manual['contraindications'] = "酸中毒、肝肾功能不全、肝硬化（尤其肝性脑病）、肾上腺功能衰竭、尿道结石、严重糖尿病、对磺胺类过敏者禁用。"
            manual['adverse_reactions'] = "常见：口周及四肢麻木刺痛、金属味觉、全身不适、恶心、食欲不振、困倦、体重减轻、抑郁、腹泻、多尿。长期使用可致电解质紊乱、尿路结石、血小板减少。"
            manual['interactions'] = "⑴与拉坦前列素有相加降眼压作用。⑵与碳酸氢钠合用可减轻副作用。⑶与枸橼酸钾合用可防尿结石。⑷与糖皮质激素合用可致严重低血钾。"
            manual['precautions'] = "⑴孕妇（尤其前3个月）、哺乳期妇女不宜使用。⑵慢性闭角型青光眼不宜长期使用。⑶使用6周以上需定期检查血常规、尿常规和电解质。"
            manual['pharmacokinetics'] = "口服易吸收，蛋白结合率高，达峰时间2-4小时，半衰期2.4-5.8小时，90-100%以原形经肾排泄。"
            
        elif drug_id == 589:  # 二甲双胍恩格列净
            manual['indications'] = "联合运动及饮食，用于改善成人2型糖尿病患者的血糖控制。"
            manual['dosage'] = "口服：起始盐酸二甲双胍500mg+恩格列净5mg，每日2次随餐服用，逐渐递增，最大剂量盐酸二甲双胍2000mg+恩格列净25mg/日。"
            manual['contraindications'] = "中度至重度肾功能损害、终末期肾病或透析、急性或慢性代谢性酸中毒、对恩格列净或二甲双胍过敏者禁用。"
            manual['adverse_reactions'] = "常见：胃肠道反应（恶心、呕吐、腹泻）、泌尿生殖系统感染、低血压、酮症酸中毒。"
            manual['interactions'] = "与胰岛素促泌剂或胰岛素合用可能增加低血糖风险。"
            manual['precautions'] = "⑴监测乳酸酸中毒症状（不适、肌痛、呼吸窘迫、嗜睡、腹痛）。⑵定期检查肾功能。⑶手术前48小时停用。"
            manual['pharmacokinetics'] = "恩格列净：达峰时间1.5小时，半衰期约12小时。二甲双胍：达峰时间2.5小时，半衰期约6小时。"
            
        elif drug_id == 696:  # 依折麦布阿托伐他汀钙
            manual['indications'] = "用于治疗高胆固醇血症和纯合子型家族性高胆固醇血症(HoFH)。"
            manual['dosage'] = "口服：起始10/10mg/日或10/20mg/日，最大剂量10/80mg/日，一日1次，不受进餐影响。"
            manual['contraindications'] = "对本品过敏者、活动性肝病或转氨酶持续升高（>3倍ULN）、孕妇、哺乳期妇女、未避孕育龄女性、接受格卡瑞韦/哌仑他韦治疗者禁用。"
            manual['adverse_reactions'] = "常见：腹泻、肌痛、高钾血症、肝酶升高、肌病、横纹肌溶解症。"
            manual['interactions'] = "⑴胆汁酸螯合剂：应在本品前≥2小时或后≥4小时服用。⑵避免与环孢素、某些HIV蛋白酶抑制剂、丙肝蛋白酶抑制剂合用。⑶与CDKI合用增加横纹肌溶解风险。"
            manual['precautions'] = "⑴高龄（≥65岁）患者慎用。⑵肝损伤患者慎用，肾损伤患者无需调整剂量。⑶定期监测肝功能和肌酸激酶。"
            manual['pharmacokinetics'] = "阿托伐他汀：达峰时间1-2小时，半衰期约14小时。依折麦布：达峰时间4-12小时，半衰期约22小时。"
            
        elif drug_id == 784:  # 咪唑立宾
            manual['indications'] = "用于抑制肾移植后的排异反应。"
            manual['dosage'] = "口服：初始剂量2-3mg/kg/日，维持剂量1-2mg/kg/日，分2-3次服用。"
            manual['contraindications'] = "对本品过敏者、白细胞计数<3000/mm³者、孕妇及哺乳期妇女禁用。"
            manual['adverse_reactions'] = "常见：骨髓抑制（白细胞减少、血小板减少）、肝功能异常、胃肠道反应（恶心、呕吐、食欲减退）、皮疹、发热。"
            manual['interactions'] = "与其他免疫抑制剂合用可能增加骨髓抑制风险。"
            manual['precautions'] = "⑴定期监测血常规和肝功能。⑵感染风险增加，注意预防感染。⑶育龄期患者用药期间应采取避孕措施。"
            manual['pharmacokinetics'] = "口服吸收良好，达峰时间2-4小时，半衰期约2-4小时，主要经肾脏排泄。"
            
        elif drug_id == 576:  # 恩那度司他
            manual['indications'] = "用于慢性肾脏病（CKD）引起的贫血。"
            manual['dosage'] = "口服：起始剂量4mg/日，根据血红蛋白水平调整，最大剂量12mg/日。"
            manual['contraindications'] = "对本品过敏者、未控制的高血压患者、孕妇及哺乳期妇女禁用。"
            manual['adverse_reactions'] = "常见：高血压、头痛、腹泻、恶心、外周水肿、高钾血症、血栓形成。"
            manual['interactions'] = "与铁剂、维生素B12、叶酸合用可增强疗效。"
            manual['precautions'] = "⑴定期监测血红蛋白、血压和血钾。⑵血栓风险增加，注意监测。⑶避免与ESA（促红细胞生成素）合用。"
            manual['pharmacokinetics'] = "口服吸收迅速，达峰时间1-2小时，半衰期约5-7小时，主要经肝脏代谢。"
            
        elif drug_id == 625:  # 氢溴酸氘瑞米德韦
            manual['indications'] = "用于治疗轻中度新型冠状病毒感染（COVID-19）的成年患者。"
            manual['dosage'] = "口服：第1天600mg/次，每日2次；第2-5天300mg/次，每日1次。"
            manual['contraindications'] = "对本品过敏者禁用。"
            manual['adverse_reactions'] = "常见：恶心、腹泻、头晕、头痛、肝功能异常、皮疹。"
            manual['interactions'] = "与CYP3A4诱导剂或抑制剂合用可能影响血药浓度。"
            manual['precautions'] = "⑴肝肾功能不全患者慎用。⑵孕妇及哺乳期妇女慎用。⑶用药期间监测肝功能。"
            manual['pharmacokinetics'] = "口服吸收良好，达峰时间约1.5小时，半衰期约4小时，主要经肝脏代谢。"
            
        elif drug_id == 527:  # 洛拉替尼
            manual['indications'] = "用于治疗ALK阳性的局部晚期或转移性非小细胞肺癌（NSCLC）患者。"
            manual['dosage'] = "口服：100mg/日，每日1次，空腹或与食物同服。"
            manual['contraindications'] = "对本品过敏者、严重肝功能损害患者禁用。"
            manual['adverse_reactions'] = "常见：水肿、周围神经病变、体重增加、认知影响、疲劳、呼吸困难、关节痛、腹泻、高胆固醇血症、高甘油三酯血症。"
            manual['interactions'] = "⑴避免与强CYP3A诱导剂或抑制剂合用。⑵与质子泵抑制剂合用可能降低疗效。"
            manual['precautions'] = "⑴定期监测血脂、肝功能和肺功能。⑵注意中枢神经系统症状（认知影响、情绪变化）。⑶高脂血症患者需降脂治疗。"
            manual['pharmacokinetics'] = "口服吸收良好，达峰时间1-2小时，半衰期约24小时，主要经肝脏CYP3A4代谢。"
            
        elif drug_id == 707:  # 海曲泊帕乙醇胺
            manual['indications'] = "用于治疗既往对糖皮质激素、免疫球蛋白等治疗反应不佳的慢性原发免疫性血小板减少症（ITP）成人患者。"
            manual['dosage'] = "口服：起始剂量2.5mg/日，根据血小板计数调整，最大剂量7.5mg/日。"
            manual['contraindications'] = "对本品过敏者、孕妇及哺乳期妇女禁用。"
            manual['adverse_reactions'] = "常见：头痛、头晕、恶心、腹泻、肝功能异常、血栓形成、骨髓纤维化。"
            manual['interactions'] = "与CYP3A4诱导剂或抑制剂合用可能影响血药浓度。"
            manual['precautions'] = "⑴定期监测血小板计数和肝功能。⑵血栓风险增加，注意监测血栓症状。⑶停药后血小板可能下降，需监测。"
            manual['pharmacokinetics'] = "口服吸收良好，达峰时间约2小时，半衰期约20小时，主要经肝脏代谢。"
            
        elif drug_id == 638:  # 炔雌醇环丙孕酮
            manual['indications'] = "用于女性避孕；治疗育龄妇女雄激素依赖性疾病（如痤疮、多毛症、雄激素性脱发）。"
            manual['dosage'] = "口服：避孕从月经第1天开始，1片/日，连服21天，停药7天；痤疮等从月经第1天开始，1片/日，连服21天，停药7天。"
            manual['contraindications'] = "静脉血栓或肺栓塞病史、严重肝病、肝肿瘤、未确诊的阴道出血、妊娠、哺乳期、严重高血压、糖尿病伴血管病变、已知或怀疑乳腺癌禁用。"
            manual['adverse_reactions'] = "常见：恶心、腹痛、体重增加、头痛、抑郁、不规则出血、乳房胀痛。严重：静脉血栓、动脉血栓、肝肿瘤。"
            manual['interactions'] = "肝酶诱导剂（利福平、苯妥英等）可降低避孕效果。抗生素可能影响肠道菌群，降低避孕效果。"
            manual['precautions'] = "⑴吸烟（尤其>35岁）增加心血管风险。⑵定期监测血压、肝功能和血脂。⑶出现血栓症状立即停药就医。"
            manual['pharmacokinetics'] = "口服吸收迅速，炔雌醇达峰时间1-2小时，半衰期约10小时；环丙孕酮达峰时间2-4小时，半衰期约4小时。"
        
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
    print("开始更新11个药品的手册内容")
    print("=" * 60)
    
    success_count = 0
    for drug_id, drug_name in drugs_to_update:
        if update_drug_manual(drug_id, drug_name):
            success_count += 1
    
    print("=" * 60)
    print(f"更新完成: {success_count}/{len(drugs_to_update)} 个药品")
    print("=" * 60)

if __name__ == "__main__":
    main()
