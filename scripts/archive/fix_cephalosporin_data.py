#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补充头孢哌酮舒巴坦的缺失数据
"""

import json
import re
from pathlib import Path

DRUGS_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js")

# 头孢哌酮舒巴坦的完整数据
CEPHALOSPORIN_DATA = {
    "indications": "本品用于治疗由敏感菌所引起的下列感染：<br>1）上、下呼吸道感染；<br>2）上、下泌尿道感染；<br>3）腹膜炎、胆囊炎、胆管炎和其他腹腔内感染；<br>4）败血症；<br>5）脑膜炎；<br>6）皮肤软组织感染；<br>7）骨骼及关节感染；<br>8）盆腔炎、子宫内膜炎、淋病及其他生殖系统感染。<br><br>由于头孢哌酮/舒巴坦具有广谱抗菌活性，因此单用本品就能治疗大多数感染，但有时也需与其他抗生素联合应用。",
    "dosage": "静脉滴注。先用5%葡萄糖注射液或氯化钠注射液适量溶解，然后再用同一溶媒稀释至50～100ml供静脉滴注，滴注时间为30～60分钟。<br><br><strong>成人：</strong>常用量一日2～4g，严重或难治性感染可增至一日8g。分等量每12小时静脉滴注1次。舒巴坦每日最高剂量不超过4g。<br><br><strong>儿童：</strong>常用量一日40～80mg/kg，等分2～4次滴注。严重或难治性感染可增至一日160mg/kg。等分2～4次滴注。新生儿出生第一周内，应每隔12小时给药1次。舒巴坦每日最高剂量不超过80mg/kg。<br><br><strong>肾功能不全患者：</strong>肌酐清除率15~30ml/min的患者每日舒巴坦最高剂量为1g（即本品最大剂量为2.0g），分等量每12小时注射一次。肌酐清除率<15ml/min的患者每日舒巴坦最高剂量为500mg（即本品1.0g），分等量每12小时注射一次。",
    "pregnancy_category": "B级",
    "pharmacokinetics": "静脉注射本品（1g头孢哌酮，1g舒巴坦）5分钟后，头孢哌酮和舒巴坦的平均血药峰浓度（Cmax）分别为236.8mg/L和130.2mg/L，蛋白结合率分别为70%～93%和38%，血消除半衰期（t1/2b）分别为1.7小时和1小时。广泛分布于体内各组织体液中，包括胆汁、皮肤、阑尾、输卵管、卵巢、子宫等。该药主要经肾排泄，所给剂量的约25%头孢哌酮和84%舒巴坦随尿排泄，余下的大部分头孢哌酮经胆汁排泄。"
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
    print("补充头孢哌酮舒巴坦数据")
    print("=" * 60)
    
    # 加载数据
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    # 查找并更新头孢哌酮舒巴坦
    updated_count = 0
    target_names = ["注射用头孢哌酮钠舒巴坦钠", "※注射用头孢哌酮钠舒巴坦钠"]
    
    for drug in drugs:
        if drug.get('name') in target_names or drug.get('chemical_name') == "注射用头孢哌酮钠舒巴坦钠":
            manual = drug.get('manual', {})
            
            # 检查是否需要更新
            needs_update = False
            if not manual.get('indications'):
                manual['indications'] = CEPHALOSPORIN_DATA['indications']
                needs_update = True
                print(f"  ✓ 补充适应症: {drug['name']} - {drug['specifications'][0]['specification']}")
            
            if not manual.get('dosage'):
                manual['dosage'] = CEPHALOSPORIN_DATA['dosage']
                needs_update = True
                print(f"  ✓ 补充用法用量: {drug['name']} - {drug['specifications'][0]['specification']}")
            
            if not manual.get('pregnancy_category'):
                manual['pregnancy_category'] = CEPHALOSPORIN_DATA['pregnancy_category']
                needs_update = True
            
            if not manual.get('pharmacokinetics'):
                manual['pharmacokinetics'] = CEPHALOSPORIN_DATA['pharmacokinetics']
                needs_update = True
            
            if needs_update:
                drug['manual'] = manual
                updated_count += 1
    
    print(f"\n共更新 {updated_count} 个条目")
    
    # 保存数据
    save_drugs(drugs)
    print(f"✅ 数据已保存")

if __name__ == '__main__':
    main()
