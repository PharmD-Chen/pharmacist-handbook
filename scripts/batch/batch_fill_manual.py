#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量补充药品手册信息
"""

import json
import re
from pathlib import Path

DRUGS_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js")

# 常见药品的手册数据模板
DRUG_MANUALS = {
    # 降压药
    "马来酸依那普利": {
        "indications": "原发性高血压；肾血管性高血压；心力衰竭。",
        "dosage": "口服。初始剂量5-10mg/日，分1-2次服用。维持剂量10-20mg/日，最大剂量40mg/日。肾功能不全者需调整剂量。",
        "contraindications": "对本品过敏者；双侧肾动脉狭窄患者；妊娠期妇女。",
        "adverse_reactions": "常见：干咳、头晕、头痛、疲劳；少见：皮疹、血管性水肿、高血钾、肾功能损害。",
        "interactions": "与保钾利尿剂合用可致高血钾；与非甾体抗炎药合用减弱降压效果；与锂剂合用增加锂中毒风险。",
        "pregnancy_category": "D级",
        "pharmacokinetics": "口服吸收约60%，1小时起效，4-6小时达峰，作用持续24小时。主要经肾排泄。",
        "precautions": "用药初期需监测血压；定期监测肾功能和血钾；出现血管性水肿立即停药；手术前应告知医生正在服用本品。"
    },
    "卡托普利": {
        "indications": "高血压；心力衰竭；心肌梗死后左室功能不全；糖尿病肾病。",
        "dosage": "口服。高血压：初始12.5-25mg/次，2-3次/日，可逐渐增至50mg/次，3次/日。心力衰竭：初始6.25-12.5mg/次，3次/日。",
        "contraindications": "对ACE抑制剂过敏者；双侧肾动脉狭窄；妊娠期妇女。",
        "adverse_reactions": "常见：干咳、皮疹、味觉异常；少见：血管性水肿、高血钾、粒细胞减少、蛋白尿。",
        "interactions": "与保钾利尿剂合用可致高血钾；与非甾体抗炎药合用减弱降压效果。",
        "pregnancy_category": "D级",
        "pharmacokinetics": "口服吸收75%，15分钟起效，1-1.5小时达峰，作用持续6-12小时。半衰期约2小时。",
        "precautions": "用药初期需监测血压；定期监测血常规、肾功能和血钾；肾功能不全者减量。"
    },
    "拉西地平": {
        "indications": "高血压。可单独使用或与其他降压药合用。",
        "dosage": "口服。初始剂量4mg/日，早晨服用。必要时可增至6mg/日。肝功能不全者减量。",
        "contraindications": "对本品过敏者；严重主动脉瓣狭窄患者。",
        "adverse_reactions": "常见：头痛、面部潮红、水肿、头晕、心悸；少见：皮疹、牙龈增生、乏力。",
        "interactions": "与CYP3A4抑制剂（如酮康唑）合用增加血药浓度；与β受体阻滞剂合用需谨慎停药。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收完全，7-8小时达峰，半衰期12-15小时。主要经肝代谢。",
        "precautions": "肝功能不全者慎用；用药初期需监测血压；避免与葡萄柚汁同服。"
    },
    "替米沙坦氢氯噻嗪": {
        "indications": "原发性高血压。用于单用替米沙坦或氢氯噻嗪血压控制不佳的患者。",
        "dosage": "口服。1片/次，1次/日。可在4-8周内逐渐调整剂量。",
        "contraindications": "对本品过敏者；严重肝功能损害；严重肾功能损害；无尿；妊娠期妇女。",
        "adverse_reactions": "常见：头晕、疲劳、上呼吸道感染；少见：高血钾、低血钾、低血糖、肾功能异常。",
        "interactions": "与锂剂合用增加锂中毒风险；与降糖药合用可能需调整剂量；与非甾体抗炎药合用减弱降压效果。",
        "pregnancy_category": "D级",
        "pharmacokinetics": "替米沙坦口服吸收迅速，0.5-1小时达峰，半衰期24小时；氢氯噻嗪2-5小时达峰，半衰期6-15小时。",
        "precautions": "定期监测电解质、肾功能和血糖；避免与保钾利尿剂合用；严重肾功能损害者禁用。"
    },
    "匹伐他汀钙": {
        "indications": "高胆固醇血症；家族性高胆固醇血症。",
        "dosage": "口服。常规剂量1-2mg/日，晚上服用。最大剂量4mg/日。",
        "contraindications": "对本品过敏者；活动性肝病；不明原因肝酶持续升高；妊娠期及哺乳期妇女。",
        "adverse_reactions": "常见：肌痛、便秘、腹痛；少见：横纹肌溶解、肝酶升高、血糖升高。",
        "interactions": "与环孢素合用增加肌病风险；与贝特类合用增加横纹肌溶解风险；避免与葡萄柚汁同服。",
        "pregnancy_category": "X级",
        "pharmacokinetics": "口服吸收率80%，0.5小时达峰，半衰期11小时。主要经肝代谢。",
        "precautions": "用药前及用药期间定期监测肝功能；出现肌痛、肌无力立即停药；避免饮酒。"
    },
    # 降糖药
    "西格列汀二甲双胍": {
        "indications": "2型糖尿病。用于单用二甲双胍或西格列汀血糖控制不佳的患者。",
        "dosage": "口服。通常1片/次，2次/日，餐中服用。根据血糖调整剂量。",
        "contraindications": "严重肾功能不全；急性或慢性代谢性酸中毒；严重感染；妊娠期妇女。",
        "adverse_reactions": "常见：腹泻、恶心、上呼吸道感染、头痛；少见：低血糖、胰腺炎、维生素B12缺乏。",
        "interactions": "与碘造影剂合用增加乳酸酸中毒风险；与CYP3A4抑制剂合用增加西格列汀血药浓度。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "西格列汀口服吸收87%，1-4小时达峰，半衰期12.4小时；二甲双胍2.5小时达峰，半衰期6.2小时。",
        "precautions": "定期监测肾功能；手术前48小时停药；避免饮酒；老年患者减量。"
    },
    "吡格列酮二甲双胍": {
        "indications": "2型糖尿病。用于单用吡格列酮或二甲双胍血糖控制不佳的患者。",
        "dosage": "口服。通常1片/次，2次/日，餐中服用。最大剂量：吡格列酮45mg/日，二甲双胍2550mg/日。",
        "contraindications": "严重肾功能不全；急性或慢性代谢性酸中毒；心力衰竭；活动性肝病。",
        "adverse_reactions": "常见：水肿、体重增加、腹泻、上呼吸道感染；少见：心力衰竭、肝酶升高、骨折风险增加。",
        "interactions": "与CYP2C8抑制剂合用增加吡格列酮血药浓度；与碘造影剂合用增加乳酸酸中毒风险。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "吡格列酮2小时达峰，半衰期3-7小时；二甲双胍2.5小时达峰，半衰期6.2小时。",
        "precautions": "定期监测肝功能、心功能；心衰患者慎用；绝经前妇女注意避孕。"
    },
    "磷酸西格列汀": {
        "indications": "2型糖尿病。可单用或与二甲双胍、磺脲类合用。",
        "dosage": "口服。100mg/次，1次/日。肾功能不全者需减量。",
        "contraindications": "对本品过敏者；严重肾功能不全未调整剂量者。",
        "adverse_reactions": "常见：上呼吸道感染、头痛、鼻咽炎；少见：胰腺炎、过敏反应、 Stevens-Johnson综合征。",
        "interactions": "与CYP3A4抑制剂（如酮康唑）合用增加血药浓度；与磺脲类合用增加低血糖风险。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收87%，1-4小时达峰，半衰期12.4小时。主要经肾排泄。",
        "precautions": "定期监测肾功能；出现腹痛、呕吐等胰腺炎症状立即停药；肾功能不全者减量。"
    },
    # 抗癫痫药
    "吡仑帕奈": {
        "indications": "成人和12岁及以上儿童癫痫部分性发作的辅助治疗；原发性全面强直-阵挛发作。",
        "dosage": "口服。初始2mg/日，睡前服用。每1-2周增加2mg，推荐剂量4-8mg/日，最大12mg/日。",
        "contraindications": "对本品过敏者；严重肝功能损害。",
        "adverse_reactions": "常见：头晕、嗜睡、头痛、体重增加、共济失调；少见：攻击行为、自杀意念、严重皮肤反应。",
        "interactions": "与CYP3A4酶诱导剂（如卡马西平、苯妥英）合用降低本品疗效；与避孕药合用降低避孕效果。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收完全，0.5-2.5小时达峰，半衰期105小时。主要经肝代谢。",
        "precautions": "逐渐调整剂量；监测情绪变化；避免突然停药；服药期间避免从事需高度警觉的活动。"
    },
    "加巴喷丁": {
        "indications": "带状疱疹后神经痛；成人和12岁以上儿童癫痫部分性发作的辅助治疗。",
        "dosage": "口服。癫痫：初始300mg/日，逐渐增加至900-1800mg/日，分3次服用。神经痛：初始300mg/日，最大1800mg/日。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：头晕、嗜睡、外周水肿、共济失调；少见：体重增加、视力模糊、口干。",
        "interactions": "与抗酸药合用降低本品吸收；与吗啡类合用增加中枢神经系统抑制；与避孕药无显著相互作用。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收不完全，2-3小时达峰，半衰期5-7小时。不经肝代谢，以原型经肾排泄。",
        "precautions": "肾功能不全者需减量；逐渐停药；老年患者需调整剂量；监测情绪变化。"
    },
    # 抗菌药
    "诺氟沙星": {
        "indications": "尿路感染、前列腺炎、肠道感染、伤寒及其他沙门菌感染。",
        "dosage": "口服。一般感染：0.4g/次，2次/日。单纯性尿路感染：0.4g/次，1次/日，疗程3日。",
        "contraindications": "对喹诺酮类过敏者；18岁以下青少年及儿童；妊娠期及哺乳期妇女。",
        "adverse_reactions": "常见：胃肠道反应、头晕、失眠；少见：肌腱炎、周围神经病变、光敏反应、QT间期延长。",
        "interactions": "与含铝、镁抗酸药合用减少吸收；与茶碱合用增加茶碱毒性；与华法林合用增加出血风险。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收30-40%，1-2小时达峰，半衰期3-4小时。主要经肾排泄。",
        "precautions": "避免与抗酸药同服；多饮水；避免过度日晒；监测血糖（糖尿病患者）；18岁以下禁用。"
    },
    "头孢拉定": {
        "indications": "敏感菌所致的呼吸道感染、尿路感染、皮肤软组织感染。",
        "dosage": "口服。成人0.25-0.5g/次，每6小时1次，一日最高4g。儿童25-50mg/kg/日，分4次服用。",
        "contraindications": "对头孢菌素类过敏者；青霉素过敏性休克史者慎用。",
        "adverse_reactions": "常见：胃肠道反应、皮疹；少见：嗜酸性粒细胞增多、肝酶升高、假膜性肠炎。",
        "interactions": "与丙磺舒合用增加血药浓度；与氨基糖苷类合用增加肾毒性。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收90%，1小时达峰，半衰期1小时。主要经肾排泄。",
        "precautions": "青霉素过敏者慎用；肾功能不全者减量；用药期间监测肾功能；长期使用需监测血象。"
    },
    "头孢克洛": {
        "indications": "敏感菌所致的呼吸道感染、中耳炎、鼻窦炎、尿路感染、皮肤软组织感染。",
        "dosage": "口服。成人0.25g/次，每8小时1次，严重感染可增至0.5g/次。儿童20-40mg/kg/日，分3次服用。",
        "contraindications": "对头孢菌素类过敏者；青霉素过敏性休克史者禁用。",
        "adverse_reactions": "常见：腹泻、恶心、皮疹、嗜酸性粒细胞增多；少见：血清病样反应、肝酶升高、血小板减少。",
        "interactions": "与丙磺舒合用增加血药浓度；与抗酸药合用减少吸收。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收50%，0.5-1小时达峰，半衰期0.5-1小时。主要经肾排泄。",
        "precautions": "青霉素过敏者慎用；肾功能不全者减量；空腹服用吸收更好；出现严重腹泻立即停药。"
    },
    # 抗病毒药
    "盐酸伐昔洛韦": {
        "indications": "带状疱疹；单纯疱疹病毒感染（包括生殖器疱疹）的初发和复发。",
        "dosage": "口服。带状疱疹：1g/次，3次/日，疗程7日。单纯疱疹：500mg/次，2次/日，疗程3-5日。",
        "contraindications": "对阿昔洛韦或伐昔洛韦过敏者。",
        "adverse_reactions": "常见：头痛、恶心、腹泻；少见：肾功能损害、神经系统症状（意识模糊、震颤）、皮疹。",
        "interactions": "与丙磺舒合用增加血药浓度；与肾毒性药物合用增加肾损害风险。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收迅速，在体内转化为阿昔洛韦，1.5-2小时达峰，半衰期2.5-3.3小时。主要经肾排泄。",
        "precautions": "肾功能不全者需减量；多饮水；监测肾功能；HIV患者需延长疗程。"
    },
    "富马酸丙酚替诺福韦": {
        "indications": "成人和青少年（12岁及以上）慢性乙型肝炎。",
        "dosage": "口服。25mg/次，1次/日，随食物服用。",
        "contraindications": "对替诺福韦过敏者。",
        "adverse_reactions": "常见：头痛、恶心、疲劳；少见：肾功能损害、骨密度降低、乳酸酸中毒、肝肿大伴脂肪变性。",
        "interactions": "与P-gp诱导剂（如利福平）合用降低本品疗效；与P-gp抑制剂合用增加血药浓度。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收迅速，0.5小时达峰，半衰期0.51小时。主要经肾排泄。",
        "precautions": "定期监测肾功能和骨密度；HIV患者需联合其他抗病毒药；停药后需监测肝功能。"
    },
    # 其他
    "维生素B1": {
        "indications": "维生素B1缺乏症（脚气病）、周围神经炎、消化不良的辅助治疗。",
        "dosage": "口服。成人5-10mg/次，3次/日。严重缺乏：100mg/日，分3次服用。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "罕见过敏反应。大剂量静脉注射可能引起过敏反应。",
        "interactions": "与碱性药物合用易分解失效。",
        "pregnancy_category": "A级",
        "pharmacokinetics": "口服吸收迅速，主要分布在心脏、肝脏、肾脏、脑组织。",
        "precautions": "不宜静脉注射（可能引起过敏性休克）；与碱性药物避免合用。"
    },
    "甲钴胺": {
        "indications": "周围神经病变；巨幼红细胞性贫血。",
        "dosage": "口服。成人0.5mg/次，3次/日。肌注或静注：0.5mg/次，每周3次。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "少见：食欲不振、恶心、腹泻、皮疹；偶见血压下降、呼吸困难等过敏反应。",
        "interactions": "与氯霉素合用降低疗效；与考来烯胺合用减少吸收。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收迅速，3小时达峰，半衰期约12.5小时。主要经肾排泄。",
        "precautions": "长期用药需监测血象；从事汞及其化合物工作者不宜长期大量服用。"
    },
    "消旋山莨菪碱": {
        "indications": "解除平滑肌痉挛、胃肠绞痛、胆道痉挛；有机磷中毒；感染性休克。",
        "dosage": "口服。成人5-10mg/次，3次/日。肌注或静注：5-10mg/次，1-2次/日。",
        "contraindications": "颅内压增高、脑出血急性期、青光眼、幽门梗阻、前列腺肥大、尿潴留患者。",
        "adverse_reactions": "常见：口干、面红、视物模糊、心率加快、排尿困难；少见：谵妄、高热、皮肤过敏。",
        "interactions": "与金刚烷胺、吩噻嗪类、三环类抗抑郁药合用增加不良反应；与甲氧氯普胺合用降低后者疗效。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收较差，肌注后15-20分钟起效，作用持续3-4小时。",
        "precautions": "夏季用药时，因其闭汗作用，可使体温升高；急腹症诊断未明确时，不宜轻易使用。"
    },
    "磷酸可待因": {
        "indications": "镇咳，用于较剧烈的频繁干咳；镇痛，用于中度以上疼痛。",
        "dosage": "口服。成人15-30mg/次，3次/日。最大剂量90mg/日。",
        "contraindications": "对本品过敏者；多痰患者（抑制咳嗽反射，使痰液阻塞）；呼吸抑制患者。",
        "adverse_reactions": "常见：便秘、嗜睡、恶心、呕吐；少见：呼吸抑制、依赖性、过敏反应。",
        "interactions": "与中枢抑制剂合用增强抑制作用；与抗胆碱药合用加重便秘和尿潴留。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收迅速，0.75-1小时达峰，半衰期2.5-4小时。主要经肝代谢。",
        "precautions": "痰多患者慎用；长期使用可产生依赖性；肝肾功能不全者减量；哺乳期妇女禁用。"
    },
    "萘普生钠": {
        "indications": "缓解轻至中度疼痛，如关节痛、神经痛、肌肉痛、偏头痛、痛经、牙痛；也用于普通感冒或流行性感冒引起的发热。",
        "dosage": "口服。首次0.5g，以后必要时0.25g/次，每6-8小时1次。每日不超过1.25g。",
        "contraindications": "对本品或其他非甾体抗炎药过敏者；活动性消化性溃疡；严重肝肾功能不全；妊娠晚期。",
        "adverse_reactions": "常见：胃肠道不适、头晕、头痛；少见：消化道出血、肾功能损害、皮疹、哮喘。",
        "interactions": "与抗凝药合用增加出血风险；与利尿剂合用降低利尿效果；与甲氨蝶呤合用增加毒性。",
        "pregnancy_category": "C级（早期），D级（晚期）",
        "pharmacokinetics": "口服吸收完全，2-4小时达峰，半衰期12-15小时。主要经肝代谢。",
        "precautions": "饭后服用；避免饮酒；长期用药需监测肝肾功能和血象；心血管疾病患者慎用。"
    },
    "醋酸去氨加压素": {
        "indications": "中枢性尿崩症；夜间遗尿症（5岁及以上）；血友病A及血管性血友病。",
        "dosage": "口服。尿崩症：0.1-0.2mg/次，3次/日。遗尿症：睡前0.2-0.4mg。",
        "contraindications": "对本品过敏者；习惯性或精神性烦渴症患者；心功能不全者；不稳定型心绞痛。",
        "adverse_reactions": "常见：头痛、恶心、胃痛；少见：低钠血症、水潴留、体重增加、过敏反应。",
        "interactions": "与利尿剂合用增加低钠血症风险；与三环类抗抑郁药、氯丙嗪合用增加水潴留风险。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收迅速，0.5-1小时达峰，半衰期3-4小时。抗利尿作用持续8-12小时。",
        "precautions": "治疗期间限制饮水；监测血钠水平；出现低钠血症症状（头痛、恶心、抽搐）立即停药。"
    },
    "复方嗜酸乳杆菌": {
        "indications": "肠道菌群失调引起的肠功能紊乱，如急性腹泻、慢性腹泻、便秘、腹胀、肠炎。",
        "dosage": "口服。成人1-2g/次，3次/日。儿童酌减。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "罕见不良反应。",
        "interactions": "与抗生素合用需间隔2-3小时；与铋剂、鞣酸、药用炭合用降低疗效。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服后定植于肠道，调节肠道菌群平衡。",
        "precautions": "与抗生素间隔2-3小时服用；溶解时水温不宜超过40℃；避光保存。"
    },
    "艾地苯醌": {
        "indications": "慢性脑血管病及脑外伤等所引起的脑功能损害；改善主观症状、语言、焦虑、抑郁、记忆减退、智能下降等精神行为障碍。",
        "dosage": "口服。成人30mg/次，3次/日，饭后服用。",
        "contraindications": "对本品过敏者；孕妇及哺乳期妇女。",
        "adverse_reactions": "常见：过敏反应、皮疹、恶心、食欲不振、腹泻；少见：兴奋、失眠、头晕。",
        "interactions": "尚不明确。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收良好，3小时达峰，半衰期约12小时。主要经肝代谢。",
        "precautions": "孕妇及哺乳期妇女禁用；长期用药需监测肝功能。"
    },
    "爱普列特": {
        "indications": "良性前列腺增生症。",
        "dosage": "口服。5mg/次，早晚各1次，饭前服用，疗程4个月。",
        "contraindications": "对本品过敏者；孕妇及哺乳期妇女；儿童。",
        "adverse_reactions": "常见：恶心、食欲减退、腹胀、腹泻、口干、头晕、失眠；少见：性功能减退、皮疹、EPS升高。",
        "interactions": "尚不明确。",
        "pregnancy_category": "X级",
        "pharmacokinetics": "口服吸收迅速，4小时达峰，半衰期约7.5小时。主要经肝代谢。",
        "precautions": "孕妇及哺乳期妇女禁用；儿童禁用；用药期间定期监测肝功能。"
    },
    "普适泰": {
        "indications": "良性前列腺增生，慢性、非细菌性前列腺炎。",
        "dosage": "口服。1片/次，2次/日，疗程3-6个月。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "少数患者有轻度胃肠道反应。",
        "interactions": "尚不明确。",
        "pregnancy_category": "未明确",
        "pharmacokinetics": "口服吸收良好，主要在前列腺组织分布。",
        "precautions": "需长期服用才见效；饭前服用效果更佳。"
    },
    "孟鲁司特钠": {
        "indications": "哮喘的预防和长期治疗；过敏性鼻炎。",
        "dosage": "口服。15岁及以上：10mg/次，1次/日，睡前服用。6-14岁：5mg/次。2-5岁：4mg/次。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：头痛、腹痛、口渴、腹泻；少见：兴奋、焦虑、抑郁、自杀意念、Churg-Strauss综合征。",
        "interactions": "与苯巴比妥、利福平合用降低本品疗效。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收迅速，3-4小时达峰，半衰期2.7-5.5小时。主要经肝代谢。",
        "precautions": "不能用于急性哮喘发作；突然停药不会引起反跳；监测情绪变化；与糖皮质激素合用时不可突然停用激素。"
    },
    "己酮可可碱": {
        "indications": "脑部血循环障碍如暂时性脑缺血发作、中风后遗症、脑缺血引起的脑功能障碍；外周血循环障碍性疾病如血栓栓塞性脉管炎、腹部动脉阻塞。",
        "dosage": "口服。0.1-0.4g/次，3次/日。缓释片：0.4g/次，1-2次/日。",
        "contraindications": "对本品过敏者；急性心肌梗死；严重冠状动脉硬化；脑出血；严重心律失常；妊娠期。",
        "adverse_reactions": "常见：恶心、头晕、头痛；少见：血压下降、心悸、皮疹、肝功能异常。",
        "interactions": "与抗血小板药、抗凝药合用增加出血风险；与茶碱合用增加茶碱毒性。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收迅速，1小时达峰，半衰期0.4-0.8小时。主要经肝代谢。",
        "precautions": "有出血倾向者慎用；定期监测血压和肝功能；与茶碱合用需监测茶碱血药浓度。"
    },
    "兰索拉唑肠溶": {
        "indications": "胃溃疡、十二指肠溃疡、反流性食管炎、卓-艾综合征。",
        "dosage": "口服。成人30mg/次，1次/日，早餐前服用。十二指肠溃疡疗程2-4周，胃溃疡疗程4-6周。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：腹泻、口干、恶心、头痛；少见：皮疹、肝功能异常、白细胞减少、间质性肾炎。",
        "interactions": "与克拉霉素合用增加血药浓度；与地高辛合用增加地高辛吸收；与甲氨蝶呤合用增加甲氨蝶呤毒性。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收迅速，1.5-2.2小时达峰，半衰期1.3-1.7小时。主要经肝代谢。",
        "precautions": "肝功能障碍者慎用；定期监测肝功能；长期使用需监测维生素B12水平；肠溶片不可咀嚼。"
    },
    "达比加群酯": {
        "indications": "预防成人非瓣膜性房颤患者的卒中和全身性栓塞；治疗深静脉血栓形成和肺栓塞，预防复发。",
        "dosage": "口服。150mg/次，2次/日，餐中服用。肾功能不全者110mg/次，2次/日。",
        "contraindications": "活动性出血；严重肝功能损害；合用环孢素、全身性酮康唑、伊曲康唑；机械人工心脏瓣膜。",
        "adverse_reactions": "常见：出血（鼻出血、牙龈出血、消化道出血、血尿）；少见：胃肠道不适、贫血、肝功能异常。",
        "interactions": "与P-gp诱导剂（如利福平）合用降低疗效；与P-gp抑制剂（如胺碘酮、维拉帕米）合用增加出血风险。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收6.5%，2小时达峰，半衰期12-17小时。主要经肾排泄。",
        "precautions": "定期监测肾功能；出血风险高者减量；与阿司匹林合用增加出血风险；无特效拮抗剂。"
    },
    "碳酸锂": {
        "indications": "躁狂症；双相情感障碍的躁狂和抑郁交替发作；预防躁狂或抑郁复发。",
        "dosage": "口服。急性躁狂：0.25-0.5g/次，3次/日，逐渐增至0.9-1.5g/日。维持量0.6-0.9g/日。",
        "contraindications": "严重心肾疾病；电解质紊乱；低钠饮食；妊娠期。",
        "adverse_reactions": "常见：恶心、呕吐、腹泻、手颤、多尿、烦渴；少见：甲状腺功能减退、体重增加、认知迟钝、心律失常。",
        "interactions": "与利尿剂合用增加锂中毒风险；与NSAIDs合用增加锂血药浓度；与卡马西平合用增加神经毒性。",
        "pregnancy_category": "D级",
        "pharmacokinetics": "口服吸收完全，2-4小时达峰，半衰期18-36小时。主要经肾排泄。",
        "precautions": "定期监测血锂浓度（治疗窗0.6-1.2mmol/L）；监测甲状腺功能和肾功能；保持正常钠摄入；避免脱水。"
    },
    "丙戊酸镁": {
        "indications": "癫痫全身性强直-阵挛发作、失神发作、肌阵挛发作；双相情感障碍的躁狂发作。",
        "dosage": "口服。初始200-400mg/日，逐渐增加至600-1200mg/日，分2-3次服用。",
        "contraindications": "肝病或明显肝功能损害；尿素循环障碍；妊娠期（致畸风险）。",
        "adverse_reactions": "常见：胃肠道反应、体重增加、脱发、手颤；少见：肝毒性、胰腺炎、血小板减少、高血氨。",
        "interactions": "与卡马西平合用降低本品血药浓度；与拉莫三嗪合用增加后者血药浓度；与阿司匹林合用增加本品游离浓度。",
        "pregnancy_category": "D级",
        "pharmacokinetics": "口服吸收迅速，1-4小时达峰，半衰期8-20小时。主要经肝代谢。",
        "precautions": "定期监测肝功能、血常规、血药浓度；育龄妇女需避孕；出现腹痛、呕吐、意识改变立即停药。"
    },
    "硫酸吗啡": {
        "indications": "重度癌痛；急性心肌梗死；急性肺水肿。",
        "dosage": "口服。初始10-30mg/次，每4小时1次，根据疼痛调整剂量。缓释片：10-30mg/次，每12小时1次。",
        "contraindications": "呼吸抑制；支气管哮喘；麻痹性肠梗阻；颅脑损伤；严重肝功能损害；妊娠期。",
        "adverse_reactions": "常见：便秘、恶心、呕吐、嗜睡、头晕；少见：呼吸抑制、低血压、尿潴留、依赖性、成瘾。",
        "interactions": "与中枢抑制剂合用增强抑制作用；与抗胆碱药合用加重便秘和尿潴留。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收20-30%，缓释片2-3小时达峰，半衰期2-4小时。主要经肝代谢。",
        "precautions": "长期使用可产生耐受性和依赖性；逐渐减量停药；便秘需预防性使用泻药；呼吸抑制时可用纳洛酮拮抗。"
    },
    "天麻素": {
        "indications": "神经衰弱、头痛、偏头痛、眩晕；脑外伤性眩晕、眩晕症。",
        "dosage": "口服。50-100mg/次，3次/日。肌注：200mg/次，1-2次/日。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "少见：口干、头晕、胃部不适、皮疹。",
        "interactions": "尚不明确。",
        "pregnancy_category": "未明确",
        "pharmacokinetics": "口服吸收迅速，1小时达峰，半衰期约4小时。主要经肾排泄。",
        "precautions": "出现不良反应需减量或停药；孕妇及哺乳期妇女慎用。"
    },
    "莫匹罗星": {
        "indications": "革兰阳性球菌引起的皮肤感染，如脓疱疮、毛囊炎、疖肿。",
        "dosage": "外用。涂于患处，3次/日，疗程5-10日。",
        "contraindications": "对本品过敏者；大面积皮肤破损。",
        "adverse_reactions": "少见：局部烧灼感、刺痛、瘙痒、皮疹。",
        "interactions": "尚不明确。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "外用后全身吸收极少，主要在皮肤局部发挥作用。",
        "precautions": "避免长期使用；出现过敏反应立即停药；避免接触眼睛。"
    },
    "他克莫司": {
        "indications": "预防器官移植后的移植物抗宿主病；中重度特应性皮炎。",
        "dosage": "外用。0.03-0.1%软膏，薄涂于患处，2次/日。口服：根据血药浓度调整剂量。",
        "contraindications": "对本品过敏者；皮肤感染者。",
        "adverse_reactions": "常见：局部烧灼感、瘙痒、红斑；少见：皮肤萎缩、毛细血管扩张、毛囊炎。",
        "interactions": "与CYP3A4抑制剂合用增加血药浓度；与CYP3A4诱导剂合用降低血药浓度。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "外用后全身吸收少，主要在皮肤局部发挥作用。",
        "precautions": "避免阳光直射；避免封包疗法；2岁以下儿童使用0.03%浓度；出现感染需停药并抗感染治疗。"
    },
    "洛索洛芬钠凝胶": {
        "indications": "骨关节炎、肌肉痛、外伤所致肿胀疼痛的局部对症治疗。",
        "dosage": "外用。适量涂于患处，1日数次。",
        "contraindications": "对本品或其他非甾体抗炎药过敏者；阿司匹林哮喘；皮肤破损处。",
        "adverse_reactions": "少见：局部皮疹、瘙痒、红斑、刺痛感。",
        "interactions": "与其他NSAIDs合用增加不良反应。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "外用后全身吸收少，主要在局部发挥作用。",
        "precautions": "避免接触眼睛和黏膜；避免长期大面积使用；出现过敏反应立即停药。"
    },
    "吸入用布地奈德混悬液": {
        "indications": "支气管哮喘；慢性阻塞性肺疾病。",
        "dosage": "吸入。成人：0.5-1mg/次，2次/日。儿童：0.25-0.5mg/次，2次/日。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：声音嘶哑、口腔念珠菌感染、咳嗽；少见：肾上腺抑制、骨质疏松、青光眼。",
        "interactions": "与CYP3A4抑制剂（如酮康唑）合用增加血药浓度。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "吸入后30分钟起效，1-2小时达峰，半衰期2-3小时。主要经肝代谢。",
        "precautions": "用药后漱口；急性哮喘发作时需合用支气管扩张剂；逐渐减量停药；监测儿童生长。"
    },
    "吸入用乙酰半胱氨酸溶液": {
        "indications": "治疗浓稠粘液分泌物过多的呼吸道疾病，如急性支气管炎、慢性支气管炎、肺气肿、粘稠物阻塞症。",
        "dosage": "吸入。3ml/次，1-2次/日。",
        "contraindications": "对本品过敏者；哮喘患者慎用。",
        "adverse_reactions": "常见：口腔炎、恶心、呕吐；少见：支气管痉挛、皮疹。",
        "interactions": "与抗生素合用需间隔2小时；与硝酸甘油合用增强后者作用。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "吸入后在局部发挥作用，部分被吸收代谢。",
        "precautions": "哮喘患者慎用；与抗生素间隔2小时使用；开启后立即使用。"
    },
    "吸入用复方异丙托溴铵溶液": {
        "indications": "需要多种支气管扩张剂联合应用的病人，如慢性阻塞性肺疾病。",
        "dosage": "吸入。成人：1支/次，3-4次/日。急性发作时可增至2支/次。",
        "contraindications": "对阿托品类药物过敏者；肥厚性梗阻型心肌病；快速性心律失常。",
        "adverse_reactions": "常见：口干、头痛、咳嗽；少见：心悸、排尿困难、视力模糊、过敏反应。",
        "interactions": "与其他抗胆碱药合用增加不良反应；与β受体激动剂合用有协同作用。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "吸入后15分钟起效，1-2小时达峰，作用持续6-8小时。",
        "precautions": "青光眼、前列腺增生患者慎用；避免进入眼睛；急性闭角型青光眼禁用。"
    },
    "甘露醇": {
        "indications": "脑水肿及青光眼的大剂量治疗；预防急性肾小管坏死；作为某些药物过量的辅助排泄。",
        "dosage": "静滴。脑水肿：0.25-2g/kg，每4-6小时1次。青光眼：1-2g/kg。",
        "contraindications": "严重失水；颅内活动性出血（颅内手术除外）；急性肺水肿；严重肾衰竭。",
        "adverse_reactions": "常见：水电解质紊乱、口渴；少见：寒战、发热、血栓性静脉炎、皮疹、肾功能损害。",
        "interactions": "与两性霉素B合用增加肾毒性；与利尿剂合用增加水电解质紊乱风险。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "静脉给药后迅速分布，不被代谢，经肾排泄。",
        "precautions": "监测水电解质平衡；监测肾功能；避免快速大剂量注射；漏出血管外可致组织坏死。"
    },
    "地塞米松磷酸钠": {
        "indications": "过敏性与自身免疫性炎症性疾病；严重感染并发的毒血症；脑水肿；休克。",
        "dosage": "肌注、静注或静滴。一般5-10mg/次，严重病例可增至20-40mg/日。",
        "contraindications": "对本品过敏者；活动性消化性溃疡；严重精神病史；严重高血压；糖尿病控制不佳。",
        "adverse_reactions": "常见：水钠潴留、高血压、血糖升高、骨质疏松、感染易感性增加；长期使用可致库欣综合征。",
        "interactions": "与利尿剂合用增加低钾风险；与NSAIDs合用增加消化道出血风险；与降糖药合用需调整剂量。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "静脉给药后迅速起效，半衰期约3-4小时，作用持续36-54小时。主要经肝代谢。",
        "precautions": "逐渐减量停药；监测血压、血糖、电解质；长期使用需补钙和维生素D；活动性感染需合用抗生素。"
    },
    "尼莫地平": {
        "indications": "蛛网膜下腔出血后的脑血管痉挛；缺血性脑血管病；偏头痛。",
        "dosage": "口服。蛛网膜下腔出血：60mg/次，每4小时1次，疗程21日。静滴：0.5mg/小时，2小时后增至1mg/小时。",
        "contraindications": "对本品过敏者；严重肝功能损害。",
        "adverse_reactions": "常见：血压下降、头痛、面部潮红、胃肠道不适；少见：心动过速、水肿、皮疹。",
        "interactions": "与降压药合用增强降压作用；与CYP3A4抑制剂合用增加血药浓度；与CYP3A4诱导剂合用降低血药浓度。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "口服吸收迅速，1小时达峰，半衰期1-2小时。主要经肝代谢。",
        "precautions": "低血压患者慎用；静滴需避光；避免与柚子汁同服；监测血压。"
    },
    "甲硝唑栓": {
        "indications": "细菌性阴道病；滴虫性阴道炎。",
        "dosage": "阴道给药。1枚/次，1次/日，睡前使用，疗程7-10日。",
        "contraindications": "对本品过敏者；妊娠期前3个月；哺乳期妇女。",
        "adverse_reactions": "常见：局部烧灼感、瘙痒；少见：恶心、头痛、金属味；罕见：白细胞减少。",
        "interactions": "与华法林合用增加出血风险；与双硫仑合用引起精神症状；与酒精合用引起双硫仑样反应。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "阴道给药后部分吸收，在局部和全身发挥作用。",
        "precautions": "用药期间及停药后3天内禁酒；出现神经系统症状立即停药；治疗期间避免性生活。"
    },
    "克林霉素磷酸酯外用溶液": {
        "indications": "寻常痤疮。",
        "dosage": "外用。涂于患处，2次/日。",
        "contraindications": "对本品过敏者；有肠炎或溃疡性结肠炎病史者。",
        "adverse_reactions": "常见：局部干燥、脱皮、烧灼感、瘙痒；少见：腹泻、腹痛（假膜性肠炎）。",
        "interactions": "与红霉素有拮抗作用，不宜合用。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "外用后全身吸收少，主要在局部发挥作用。",
        "precautions": "避免接触眼睛和黏膜；出现严重腹泻立即停药；长期使用需监测肠道菌群。"
    },
    "黄体酮": {
        "indications": "先兆流产和习惯性流产；经前期紧张综合征；无排卵型功血和无排卵型闭经；与雌激素联合用于激素替代治疗。",
        "dosage": "肌注。先兆流产：10-20mg/日，直至疼痛及出血停止。习惯性流产：10-20mg/次，每周2-3次。闭经：10mg/日，连用5日。",
        "contraindications": "对本品过敏者；血栓性静脉炎；血栓栓塞性疾病；严重肝功能损害；不明原因阴道出血。",
        "adverse_reactions": "常见：突破性出血、阴道点状出血、体重增加、乳房胀痛；少见：头痛、头晕、抑郁、肝功能异常。",
        "interactions": "与苯巴比妥、苯妥英钠合用降低本品疗效。",
        "pregnancy_category": "D级",
        "pharmacokinetics": "肌注后迅速吸收，6-8小时达峰，半衰期约5分钟。主要经肝代谢。",
        "precautions": "定期检查肝功能；监测阴道出血情况；长期用药需体检；血栓病史者慎用。"
    },
    "巴曲酶": {
        "indications": "急性缺血性脑血管疾病；突发性耳聋；伴随有缺血性症状的慢性动脉闭塞症。",
        "dosage": "静滴。首次10BU，以后隔日5BU，疗程通常1周。",
        "contraindications": "出血患者；新近手术患者；有出血可能的患者；严重肝肾功能不全。",
        "adverse_reactions": "常见：注射部位出血、创面出血、头痛、头晕、恶心；少见：过敏反应、休克。",
        "interactions": "与抗凝药、抗血小板药合用增加出血风险。",
        "pregnancy_category": "未明确",
        "pharmacokinetics": "静脉给药后迅速起效，主要经肝代谢。",
        "precautions": "用药前及用药期间监测凝血功能；避免创伤性操作；出现出血立即停药并处理。"
    },
    "硫酸镁": {
        "indications": "子痫；先兆子痫；早产（抑制宫缩）；低镁血症。",
        "dosage": "静滴。子痫：首剂4g缓慢静注，以后1-2g/小时维持。早产：4g负荷量，以后1-2g/小时维持。",
        "contraindications": "严重肾功能不全；心脏传导阻滞；心肌损害；呼吸衰竭。",
        "adverse_reactions": "常见：面部潮红、出汗、口干、恶心；过量可致肌张力减退、腱反射消失、呼吸抑制、心脏骤停。",
        "interactions": "与钙剂拮抗；与中枢抑制剂合用增强抑制作用；与氨基糖苷类合用增强神经肌肉阻滞。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "静脉给药后迅速分布，主要经肾排泄。",
        "precautions": "监测膝腱反射、呼吸、尿量；备好钙剂（解毒用）；肾功能不全者减量；中毒时立即停药并静注钙剂。"
    },
    "氨甲苯酸": {
        "indications": "原发性纤维蛋白溶解亢进所致的各种出血；前列腺、尿道、肺、脑、子宫、肾上腺、甲状腺等富有纤溶酶原激活物脏器的外伤或手术出血。",
        "dosage": "静注或静滴。0.1-0.3g/次，不超过0.6g/日。",
        "contraindications": "有血栓形成倾向者；有血栓栓塞病史者；DIC高凝期患者。",
        "adverse_reactions": "少见：头晕、头痛、腹部不适；过量可致血栓形成。",
        "interactions": "与口服避孕药合用增加血栓风险；与止血敏合用增强止血效果。",
        "pregnancy_category": "未明确",
        "pharmacokinetics": "静脉给药后迅速起效，主要经肾排泄。",
        "precautions": "有血栓形成倾向者慎用；DIC低凝期可用，高凝期禁用；监测凝血功能。"
    },
    "盐酸纳洛酮": {
        "indications": "阿片类药物过量；阿片类药物术后呼吸抑制；新生儿阿片类药物所致呼吸抑制。",
        "dosage": "静注、肌注或皮下注射。成人：0.4-0.8mg/次，必要时2-3分钟重复。儿童：0.01-0.02mg/kg。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：血压升高、心率加快、呕吐、出汗；少见：心律失常、肺水肿、惊厥。",
        "interactions": "与阿片类拮抗；与降压药合用减弱降压效果。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "静脉给药后1-2分钟起效，作用持续45-90分钟。主要经肝代谢。",
        "precautions": "作用时间短，需重复给药；心血管病患者慎用；监测呼吸和意识状态。"
    },
    "尼可刹米": {
        "indications": "中枢性呼吸功能不全；各种继发性的呼吸抑制；慢性阻塞性肺疾病伴高碳酸血症。",
        "dosage": "皮下、肌注或静注。0.25-0.5g/次，必要时每1-2小时重复，极量1.25g/次。",
        "contraindications": "抽搐及惊厥患者；对本品过敏者。",
        "adverse_reactions": "常见：多汗、恶心、打喷嚏、面部潮红；过量可致血压升高、心悸、心律失常、惊厥。",
        "interactions": "与单胺氧化酶抑制剂合用增加不良反应；与中枢兴奋剂合用增加惊厥风险。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "注射后迅速起效，作用持续5-10分钟。主要经肝代谢。",
        "precautions": "严格掌握剂量；出现惊厥立即停药；静脉注射需缓慢。"
    },
    "氟哌啶醇": {
        "indications": "急、慢性精神分裂症；躁狂症；抽动秽语综合征。",
        "dosage": "肌注。5-10mg/次，2-3次/日。极量30mg/日。",
        "contraindications": "基底神经节病变；帕金森病；严重中枢神经抑制状态；骨髓抑制；青光眼；重症肌无力。",
        "adverse_reactions": "常见：锥体外系反应（震颤、肌强直、运动迟缓）、口干、便秘、视物模糊；少见：迟发性运动障碍、恶性综合征、肝功能异常。",
        "interactions": "与锂盐合用增加神经毒性；与降压药合用增强降压作用；与抗胆碱药合用增加不良反应。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "肌注后30-60分钟起效，作用持续4-8小时。主要经肝代谢。",
        "precautions": "监测锥体外系反应；长期用药需定期检查肝功能；心血管疾病患者慎用；逐渐减量停药。"
    },
    "注射用苄星青霉素": {
        "indications": "预防风湿热复发；控制链球菌感染的流行。",
        "dosage": "肌注。成人：60-120万单位/次，每2-4周1次。儿童：30-60万单位/次，每2-4周1次。",
        "contraindications": "对青霉素过敏者；青霉素过敏性休克史者。",
        "adverse_reactions": "常见：注射部位疼痛、硬结；少见：过敏反应、血清病样反应；罕见：过敏性休克。",
        "interactions": "与丙磺舒合用增加血药浓度；与四环素类合用降低疗效。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "肌注后缓慢吸收，血药浓度低但持久，可维持2-4周。",
        "precautions": "用药前需皮试；不可静脉注射；长期用药需定期检查血象；出现过敏反应立即停药。"
    },
    "阿奇霉素干": {
        "indications": "敏感菌所致的呼吸道感染、皮肤软组织感染、中耳炎、鼻窦炎、咽炎、扁桃体炎。",
        "dosage": "口服。成人：首日500mg，以后250mg/日，连服4日。儿童：10mg/kg首日，以后5mg/kg/日，连服4日。",
        "contraindications": "对本品过敏者；严重肝功能损害。",
        "adverse_reactions": "常见：胃肠道反应、腹泻、恶心；少见：肝功能异常、皮疹、心律失常（QT间期延长）。",
        "interactions": "与抗酸药合用减少吸收；与华法林合用增加出血风险；与地高辛合用增加地高辛血药浓度。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收37%，2-3小时达峰，半衰期68小时。主要经肝代谢。",
        "precautions": "肝功能不全者慎用；与食物同服减少胃肠道反应；出现严重腹泻立即停药；监测心电图（心脏病患者）。"
    },
    "盐酸丙美卡因": {
        "indications": "眼科表面麻醉，用于眼科检查及小手术。",
        "dosage": "滴眼。1-2滴/次，根据手术需要调整。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "少见：局部刺激、角膜上皮损伤、过敏反应。",
        "interactions": "尚不明确。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "滴眼后迅速起效，作用持续15-20分钟。",
        "precautions": "不可反复长期使用；角膜上皮损伤者慎用；避免污染瓶口。"
    },
    "50%葡萄糖": {
        "indications": "补充能量和体液；低血糖症；高钾血症；脑水肿；作为某些药物的稀释剂。",
        "dosage": "静注或静滴。根据病情调整剂量。低血糖：20-40ml静注。",
        "contraindications": "糖尿病酮症酸中毒未控制者；高血糖非酮症性高渗状态。",
        "adverse_reactions": "常见：静脉炎、局部疼痛；快速注射可致高血糖、高渗性昏迷；长期单纯使用可致电解质紊乱。",
        "interactions": "与胰岛素合用降低血糖；与噻嗪类利尿剂合用增加血糖。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "静脉给药后迅速分布，提供能量。",
        "precautions": "监测血糖；静脉注射需缓慢；外渗可致组织坏死；糖尿病患者慎用。"
    },
    "碳酸氢钠": {
        "indications": "代谢性酸中毒；碱化尿液；胃酸过多；高钾血症。",
        "dosage": "静滴。根据血气分析结果调整剂量。一般5%溶液100-200ml。",
        "contraindications": "代谢性或呼吸性碱中毒；低钙血症；过量钠负荷。",
        "adverse_reactions": "常见：低钾血症、水钠潴留、代谢性碱中毒；快速注射可致心律失常。",
        "interactions": "与酸性药物合用降低疗效；与利尿剂合用增加低钾风险。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "静脉给药后迅速起效，主要经肾排泄。",
        "precautions": "监测血气分析和电解质；避免过量；心肾功能不全者慎用；外渗可致组织坏死。"
    },
    "吸入用七氟烷": {
        "indications": "全身麻醉的诱导和维持。",
        "dosage": "吸入诱导：0.5-5%浓度；维持：0.5-3%浓度。",
        "contraindications": "对本品过敏者；恶性高热病史或易感者。",
        "adverse_reactions": "常见：血压下降、呼吸抑制、恶心呕吐；少见：恶性高热、肝毒性、心律失常。",
        "interactions": "与阿片类合用增强呼吸抑制；与肌松药合用增强肌松作用；与肾上腺素合用增加心律失常风险。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "吸入后迅速起效，血/气分配系数0.65，肺泡浓度上升快。主要经肺排泄。",
        "precautions": "监测血压、心率、呼吸；备好恶性高热治疗药物；避免使用钙通道阻滞剂；监测肝功能。"
    },
    "丙泊酚乳状": {
        "indications": "全身麻醉的诱导和维持；重症监护患者的镇静。",
        "dosage": "静注。诱导：1.5-2.5mg/kg；维持：4-12mg/kg/小时。",
        "contraindications": "对本品过敏者；严重心功能不全；严重呼吸功能不全；妊娠期间。",
        "adverse_reactions": "常见：血压下降、呼吸抑制、注射部位疼痛；少见：心律失常、高脂血症、丙泊酚输注综合征。",
        "interactions": "与阿片类合用增强呼吸抑制；与肌松药合用增强肌松作用。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "静注后30-40秒起效，作用持续5-10分钟。半衰期30-60分钟。主要经肝代谢。",
        "precautions": "监测血压、心率、呼吸；缓慢注射；3岁以下儿童禁用；ICU患者监测甘油三酯。"
    },
    "硫酸鱼精蛋白": {
        "indications": "肝素过量引起的出血；心脏手术后中和肝素。",
        "dosage": "静注。用量与最后一次肝素用量相当，1mg可中和100单位肝素。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：低血压、心动过缓、呼吸困难；少见：过敏反应、肺动脉高压、出血。",
        "interactions": "与肝素拮抗。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "静注后迅速起效，作用持续2小时。",
        "precautions": "缓慢静注（10分钟）；监测凝血功能；过量可致抗凝作用；对鱼过敏者慎用。"
    },
    "托拉塞米": {
        "indications": "充血性心力衰竭所致的水肿；原发性高血压；肝硬化腹水；肾脏疾病所致水肿。",
        "dosage": "口服。水肿：5-20mg/次，1次/日。高血压：2.5-5mg/次，1次/日。静注：5-20mg/次。",
        "contraindications": "对本品过敏者；无尿；严重电解质紊乱；肝性脑病。",
        "adverse_reactions": "常见：电解质紊乱、低血压、头晕、头痛；少见：肾功能损害、血糖升高、耳毒性。",
        "interactions": "与氨基糖苷类合用增加耳肾毒性；与锂剂合用增加锂中毒风险；与降压药合用增强降压作用。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "口服吸收80-90%，1小时达峰，半衰期3.5小时。主要经肝代谢。",
        "precautions": "监测电解质、肾功能、血糖；避免与氨基糖苷类合用；痛风患者慎用；逐渐减量停药。"
    },
    "醋酸奥曲肽": {
        "indications": "食管胃底静脉曲张出血；肢端肥大症；胃肠胰内分泌肿瘤；胰腺炎。",
        "dosage": "皮下注射。肢端肥大症：0.05-0.1mg/次，每8小时1次。静脉曲张出血：0.1mg静注，以后0.025-0.05mg/小时静滴。",
        "contraindications": "对本品过敏者；妊娠期；哺乳期。",
        "adverse_reactions": "常见：胃肠道反应、胆石症、高血糖或低血糖；少见：心动过缓、甲状腺功能减退、肝功能异常。",
        "interactions": "与环孢素合用降低环孢素血药浓度；与溴隐亭合用增加溴隐亭生物利用度。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "皮下注射后30分钟起效，作用持续12小时。主要经肝代谢。",
        "precautions": "监测血糖、甲状腺功能、肝功能；胆石症患者慎用；逐渐减量停药；孕妇禁用。"
    },
    "单唾液酸四己糖神经节苷脂钠": {
        "indications": "脑血管意外后遗症；帕金森病；脊髓损伤；周围神经病变。",
        "dosage": "肌注或静滴。20-40mg/日，急性期可增至100mg/日，疗程2-6周。",
        "contraindications": "对本品过敏者；遗传性糖脂代谢异常（神经节苷脂累积病）。",
        "adverse_reactions": "少见：皮疹、过敏反应；罕见：吉兰-巴雷综合征。",
        "interactions": "尚不明确。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "注射后缓慢起效，主要经肾排泄。",
        "precautions": "出现过敏反应立即停药；吉兰-巴雷综合征患者禁用；监测神经功能。"
    },
    "盐酸格拉司琼": {
        "indications": "预防化疗引起的恶心和呕吐；预防和治疗术后恶心和呕吐。",
        "dosage": "静注或静滴。化疗前30分钟3mg，必要时可追加。术后：1mg，缓慢静注。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：头痛、便秘、乏力；少见：肝酶升高、过敏反应、QT间期延长。",
        "interactions": "与肝酶诱导剂合用降低本品血药浓度；与QT间期延长药物合用增加心律失常风险。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "静注后迅速起效，作用持续24小时。半衰期约9小时。主要经肝代谢。",
        "precautions": "监测心电图（心脏病患者）；便秘患者慎用；肠梗阻患者禁用。"
    },
    "盐酸纳美芬": {
        "indications": "完全或部分逆转阿片类药物的作用，包括由天然的或合成的阿片类药物引起的呼吸抑制。",
        "dosage": "静注。0.25-1mg/次，每2-5分钟重复，最大剂量1.5mg。",
        "contraindications": "对本品过敏者。",
        "adverse_reactions": "常见：恶心、呕吐、头晕、心动过速；少见：高血压、术后疼痛、震颤。",
        "interactions": "与阿片类拮抗。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "静注后1-2分钟起效，作用持续4-8小时。半衰期约10小时。主要经肝代谢。",
        "precautions": "监测呼吸和意识状态；心血管病患者慎用；作用时间长于纳洛酮。"
    },
    "氢溴酸依他佐辛": {
        "indications": "各种癌症及手术后的镇痛。",
        "dosage": "肌注或皮下注射。15-30mg/次，必要时每3-6小时重复。",
        "contraindications": "对本品过敏者；严重呼吸抑制；严重颅脑损伤。",
        "adverse_reactions": "常见：恶心、呕吐、头晕、嗜睡；少见：呼吸抑制、低血压、便秘、成瘾。",
        "interactions": "与中枢抑制剂合用增强抑制作用；与阿片类合用增强镇痛作用。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "肌注后15-30分钟起效，作用持续3-5小时。主要经肝代谢。",
        "precautions": "监测呼吸和血压；避免长期使用；逐渐减量停药；呼吸抑制时可用纳洛酮拮抗。"
    },
    "氢溴酸东莨菪碱": {
        "indications": "麻醉前给药；晕动病；帕金森病；有机磷中毒。",
        "dosage": "皮下或肌注。麻醉前：0.3-0.6mg/次。晕动病：0.3-0.6mg/次，必要时每6小时重复。",
        "contraindications": "青光眼；前列腺肥大；幽门梗阻；麻痹性肠梗阻。",
        "adverse_reactions": "常见：口干、视力模糊、嗜睡、心悸；少见：谵妄、尿潴留、便秘。",
        "interactions": "与金刚烷胺、吩噻嗪类合用增加不良反应；与甲氧氯普胺合用降低后者疗效。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "注射后迅速起效，作用持续4-6小时。主要经肝代谢。",
        "precautions": "老年人慎用；监测眼压；避免驾驶或操作机械。"
    },
    "氢溴酸山莨菪碱": {
        "indications": "解除平滑肌痉挛、胃肠绞痛、胆道痉挛；有机磷中毒；感染性休克。",
        "dosage": "肌注或静注。5-10mg/次，1-2次/日。",
        "contraindications": "颅内压增高、脑出血急性期、青光眼、幽门梗阻、前列腺肥大、尿潴留患者。",
        "adverse_reactions": "常见：口干、面红、视物模糊、心率加快、排尿困难；少见：谵妄、高热、皮肤过敏。",
        "interactions": "与金刚烷胺、吩噻嗪类、三环类抗抑郁药合用增加不良反应；与甲氧氯普胺合用降低后者疗效。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "注射后15-20分钟起效，作用持续3-4小时。",
        "precautions": "夏季用药时，因其闭汗作用，可使体温升高；急腹症诊断未明确时，不宜轻易使用。"
    },
    "氯化琥珀胆碱": {
        "indications": "全身麻醉时气管插管和手术中肌肉松弛。",
        "dosage": "静注。1-2mg/kg，根据需要追加。",
        "contraindications": "恶性高热病史或家族史；假性胆碱酯酶缺乏；严重烧伤；广泛性软组织损伤；高钾血症。",
        "adverse_reactions": "常见：肌痛、高钾血症、眼压升高、颅内压升高；少见：恶性高热、心律失常、支气管痉挛。",
        "interactions": "与氨基糖苷类合用增强肌松作用；与洋地黄类合用增加心律失常风险；与普鲁卡因合用延长肌松时间。",
        "pregnancy_category": "C级",
        "pharmacokinetics": "静注后30-60秒起效，作用持续5-10分钟。被假性胆碱酯酶水解。",
        "precautions": "备好恶性高热治疗药物；监测血钾；烧伤患者24小时后禁用；青光眼患者慎用。"
    },
    "碘普罗胺": {
        "indications": "CT增强扫描；血管造影；尿路造影；脊髓造影。",
        "dosage": "根据检查类型和患者体重调整剂量，一般50-150ml。",
        "contraindications": "对碘造影剂过敏史；严重甲状腺功能亢进；严重肾功能不全；脱水。",
        "adverse_reactions": "常见：恶心、呕吐、发热感、味觉异常；少见：过敏反应、荨麻疹、支气管痉挛、过敏性休克、肾功能损害。",
        "interactions": "与二甲双胍合用增加乳酸酸中毒风险；与β受体阻滞剂合用增加过敏反应严重性；与肾毒性药物合用增加肾毒性。",
        "pregnancy_category": "B级",
        "pharmacokinetics": "静脉给药后迅速分布，主要经肾排泄，24小时内排出90%以上。",
        "precautions": "用药前需询问过敏史；备好抢救设备；肾功能不全者慎用；用药前后充分水化；甲亢患者慎用。"
    }
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
    print("批量补充药品手册信息")
    print("=" * 60)
    
    # 加载数据
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    # 统计更新
    updated_count = 0
    skipped_count = 0
    
    for drug in drugs:
        name = drug.get('name', '')
        chemical_name = drug.get('chemical_name', '')
        
        # 查找匹配的手册数据
        manual_data = None
        if name in DRUG_MANUALS:
            manual_data = DRUG_MANUALS[name]
        elif chemical_name in DRUG_MANUALS:
            manual_data = DRUG_MANUALS[chemical_name]
        
        if manual_data:
            manual = drug.get('manual', {})
            
            # 只更新空字段
            for key, value in manual_data.items():
                if not manual.get(key):
                    manual[key] = value
            
            drug['manual'] = manual
            updated_count += 1
            print(f"  ✓ 已补充: {name}")
    
    print(f"\n共更新 {updated_count} 个条目")
    
    # 保存数据
    save_drugs(drugs)
    print(f"✅ 数据已保存")

if __name__ == '__main__':
    main()
