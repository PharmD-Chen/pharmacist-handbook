#!/usr/bin/env python3
"""
根据湖南药事服务网更新阿司匹林的完整内容
网址: https://www.hnysfww.com/goods.php?id=1155
"""

import json
import re

# 根据网站内容更新的完整数据
ASPIRIN_FULL = {
    "indications": "本品的抗血小板聚集作用，可减少动脉粥样硬化疾病血栓形成的危险，用于：<br>1）<strong>急性心肌梗死、心绞痛、冠状动脉介入治疗搭桥术</strong>（球囊扩张、支架置入）、透析用动静脉分流；<br>2）<strong>心肌梗死后、脑卒中后、一过性脑缺血后的再发预防</strong>；<br>3）<strong>心房颤动、人工心脏瓣膜置换术后，外周动脉闭塞性疾病、深静脉等血栓形成的预防</strong>；<br>4）<strong>有心脑血管瘤危险病人</strong>（如高血压、糖尿病）<strong>的一级预防</strong>；<br>5）<strong>预防子痫前期</strong>；<br>6）<strong>治疗产科抗磷脂综合征</strong>。",
    
    "dosage": "<strong>口服</strong>。<br><br><strong>急性心肌梗死</strong>：首次<strong>300mg嚼服</strong>，以后100-200mg/日。<br><strong>长期预防</strong>：100mg/日。<br><strong>饭前</strong>用适量水送服。",
    
    "contraindications": "①<strong>活动性溃疡或其他原因引起的消化道出血</strong>；<br>②<strong>血友病或血小板减少症</strong>；<br>③<strong>有阿司匹林或其他非甾体抗炎药过敏史者</strong>；<br>④<strong>分娩前2~3周禁用</strong>；<br>⑤本品易于通过胎盘，妊娠头3个月应用可致畸胎，妊娠后3个月长期大量应用可使妊娠期延长，增加过期产综合征及产前出血危险。",
    
    "adverse_reactions": "一般用于解热镇痛的剂量很少引起不良反应。长期大剂量用药（血浓度＞200μg/ml）时较易出现不良反应。<br><br><strong>较常见</strong>（3%～9%）：<strong>恶心、呕吐、上腹部不适或疼痛</strong>等胃肠道反应；长期或大剂量服用可有<strong>胃肠道出血或溃疡</strong>。<br><br><strong>中枢神经</strong>：可逆性<strong>耳鸣、听力下降</strong>（血药浓度达200～300μg/ml后出现）。<br><br><strong>过敏反应</strong>（0.2%）：<strong>哮喘、荨麻疹、血管神经性水肿或休克</strong>（阿司匹林哮喘），严重者可致死亡。<br><br><strong>肝、肾功能损害</strong>：与剂量大小有关，血药浓度达250μg/ml时易发生，可逆性，停药后可恢复。",
    
    "interactions": "①<strong>与抗凝药（华法林）、氯吡格雷合用</strong>：出血风险增加；<br>②<strong>与布洛芬合用</strong>：减弱心血管保护作用；<br>③<strong>与酒精合用</strong>：增加胃肠道出血风险；<br>④与其他非甾体抗炎药合用：增加胃肠道不良反应。",
    
    "pregnancy_category": "C级（早期），<strong>D级（晚期）</strong>。妊娠20周或之后使用可导致罕见且严重的胎儿肾脏问题。",
    
    "pharmacokinetics": "本品具有较强的抗血小板作用，机制在于<strong>抑制环氧化酶而使前列腺素合成受到影响</strong>，特别是血栓素A2（TXA2）的合成减少，从而抑制血栓形成。<br><br>口服吸收迅速，1-2小时达峰。半衰期15-20分钟（阿司匹林），2-3小时（水杨酸，小剂量）。",
    
    "precautions": "①<strong>饭前服用</strong>；<br>②<strong>手术前7-10天停药</strong>；<br>③<strong>哮喘患者慎用</strong>；<br>④长期用药定期检查血象、肝肾功能；<br>⑤出现<strong>耳鸣、头痛立即停药</strong>；<br>⑥儿童病毒感染时禁用（Reye综合征风险）。",
    
    "black_box_warning": "<strong>警示</strong>：在孕20周或之后使用非甾体抗炎药（NSAIDs）可导致罕见且严重的胎儿肾脏问题，可能引起宫内羊水不足并出现并发症。"
}

# 精简版内容
ASPIRIN_SUMMARY = {
    "indications": "抗血小板：<strong>心梗预防、中风二级预防、心绞痛</strong>；<strong>支架/搭桥术后</strong>；<strong>深静脉血栓预防</strong>；子痫前期预防。",
    
    "dosage": "口服。<strong>饭前</strong>用适量水送服。<br><strong>急性心梗</strong>：首次<strong>300mg嚼服</strong>，以后100-200mg/日。<br><strong>长期预防</strong>：100mg/日。",
    
    "contraindications": "<strong>活动性溃疡、消化道出血</strong>；血友病、血小板减少；<strong>阿司匹林哮喘</strong>；<strong>妊娠晚期</strong>。",
    
    "adverse_reactions": "常见：<strong>胃肠道不适、出血、溃疡</strong>；<strong>耳鸣、听力下降</strong>（水杨酸反应）；<strong>过敏反应</strong>（哮喘、荨麻疹）；肝肾功能损害。",
    
    "interactions": "<strong>与抗凝药（华法林）、氯吡格雷合用：出血风险增加</strong>；与布洛芬合用：减弱心血管保护作用；与酒精合用：增加胃肠道出血风险。",
    
    "pregnancy_category": "C级（早期），<strong>D级（晚期）</strong>。孕20周后使用可致胎儿肾脏问题。",
    
    "pharmacokinetics": "抑制环氧化酶，减少TXA2合成，抑制血栓形成。口服吸收迅速，1-2小时达峰。",
    
    "precautions": "<strong>饭前服用</strong>；<strong>手术前7-10天停药</strong>；哮喘患者慎用；出现耳鸣、头痛立即停药。",
    
    "black_box_warning": "<strong>警示</strong>：孕20周或之后使用可导致罕见且严重的胎儿肾脏问题，可能引起宫内羊水不足并出现并发症。"
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

def update_aspirin(drugs):
    """更新阿司匹林的内容"""
    updated_count = 0
    
    for drug in drugs:
        name = drug.get('name', '')
        chemical_name = drug.get('chemical_name', '')
        
        # 匹配阿司匹林
        if name == '阿司匹林' or chemical_name == '阿司匹林':
            manual = drug.get('manual', {})
            
            # 更新精简版内容
            for key, value in ASPIRIN_SUMMARY.items():
                manual[key] = value
            
            # 更新完整版内容
            for key, value in ASPIRIN_FULL.items():
                full_key = f'full_{key}'
                manual[full_key] = value
            
            drug['manual'] = manual
            updated_count += 1
            print(f"✓ 已更新: {name} ({drug.get('dosage_form', '')})")
    
    return drugs, updated_count

def main():
    print("=" * 60)
    print("更新阿司匹林的内容")
    print("数据来源: https://www.hnysfww.com/goods.php?id=1155")
    print("=" * 60)
    
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    drugs, updated_count = update_aspirin(drugs)
    
    print(f"\n共更新 {updated_count} 个条目")
    
    save_drugs(drugs)
    print(f"✅ 数据已保存")

if __name__ == '__main__':
    main()
