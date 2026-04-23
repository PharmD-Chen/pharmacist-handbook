#!/usr/bin/env python3
"""
修正特定药物的手册内容 - V3
针对用户反馈的具体问题进行修复
"""

import json
import re
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

def fix_drug(drug_id, fixes):
    """修正单个药物"""
    file_path = DATA_DIR / f'{drug_id}.json'
    if not file_path.exists():
        print(f'❌ ID {drug_id}: 文件不存在')
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    manual = data.get('manual', {})
    name = data.get('name', '')
    
    # 应用修正
    for field, value in fixes.items():
        if value is not None:
            manual[field] = value
    
    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'✅ ID {drug_id}: {name} - 已修正')
    return True

def main():
    # 定义需要修正的药物
    fixes = {
        # 氯化钾 (ID: 5) - 修正详版药代动力学
        5: {
            'full_pharmacokinetics': '钾是细胞内的主要阳离子，其浓度为150-160mmol/L，而细胞外的主要阳离子是钠离子，血清钾浓度仅为3.5-5.0mmol/L。机体主要依靠细胞膜上的Na+-K+-ATP酶来维持细胞内外的K+、Na+浓度差。正常的细胞内外钾离子浓度及浓度差与细胞的某些功能有着密切的关系，如碳水化合物代谢、糖原贮存和蛋白质代谢、神经、肌肉包括心肌的兴奋性和传导性等。',
        },
        
        # 氨茶碱 (ID: 6) - 全面修正
        6: {
            # 添加黑框警示
            'black_box_warning': '茶碱在血清中的治疗浓度与发生毒性反应的浓度接近。某些生理条件、基础疾病、合并用药等因素可能降低血清茶碱清除率，增加毒性反应的发生风险，具有此类风险因素的患者应当慎用本品，如需使用应减少剂量，并监测茶碱血清浓度。快速性心律失常、高血压控制不良、心肌缺血、有癫痫或癫痫样发作病史等的患者慎用本品。',
            # 修正药物相互作用
            'interactions': '与克林霉素等抗菌药合用降低本品清除率；与锂盐合用加速锂排出；与普萘洛尔合用抑制支气管扩张；苯巴比妥等刺激代谢；维拉帕米增加毒性；提高洋地黄敏感性；与咖啡因合用疗效增但不良反应多；稀盐酸减少吸收；避免与维生素C等配伍。',
            # 修正详版药物相互作用
            'full_interactions': '⑴与克林霉素、林可霉素、大环内酯类、四环素类、喹诺酮类抗菌药物合用时，可降低本品在肝脏的清除率，使血药浓度升高，甚至出现毒性反应。<br>⑵与锂盐合用时，可加速肾脏对锂的排出，锂盐的疗效因而降低。<br>⑶与普萘洛尔合用时，本品的支气管扩张作用可能受到抑制。<br>⑷苯巴比妥、苯妥英、利福平等可刺激氨茶碱在肝脏中代谢，使其清除率增加。<br>⑸维拉帕米可干扰氨茶碱在肝脏内的代谢，增加血药浓度和毒性。<br>⑹本品可提高心肌对洋地黄药物的敏感性，合用时后者的心脏毒性增加。<br>⑺与咖啡因及其他茶碱类药合用时，疗效可增加但不良反应也可增多。<br>⑻稀盐酸可减少氨茶碱在小肠的吸收。<br>⑼静脉输液时，应避免与维生素C、促皮质激素、去甲肾上腺素、四环素族盐酸盐配伍。',
            # 修正详版用法用量（去除多余内容）
            'full_dosage': '⑴成人常用量：<br>①口服，一次0.1～0.2g，一日3次；极量：一次0.5g，一日1.0g。<br>②肌内注射，一次0.25～0.5g，应加用2％盐酸普鲁卡因。<br>③静脉注射，一次0.25～0.5g，一日0.5～1.0g，每25～100mg用5％葡萄糖注射液稀释至20～40ml，注入速度每分钟≤10mg。<br>④静脉滴注，一次0.25～0.5g，一日0.5～1.0g，以5％～10％葡萄糖注射液稀释后缓慢滴注。极量一次0.5g，一日1.0g。<br>⑤直肠给药，一般在睡前或便后，一次0.25～0.5g，一日1～2次。<br>⑵小儿常用量：<br>①口服，一次按体重5mg/kg，一日2～3次。<br>②静脉注射，一次按体重2～4mg/kg，以5％～10％葡萄糖注射液稀释，缓慢注射。<br>⑶用于新生儿呼吸暂停的治疗，负荷量4~6mg/kg，静脉给药，15~20分钟内给完；12小时后给予维持量，一次1.5~2mg/kg，一日2~3次，静脉或口服给药。',
            # 修正详版药代动力学
            'full_pharmacokinetics': '口服本品或由直肠或胃肠道外给药均能迅速被吸收。在体内氨茶碱释放出茶碱，后者的蛋白结合率为60％。分布容积约为0.5L/kg。半衰期（t1/2）为3～9小时。静注6mg/kg氨茶碱，其在半小时内血药浓度可达10μg/ml，它在体内的生物转化率有个体间差异。空腹状态下口服本品，在2小时血药浓度达峰值。本品的大部分以代谢产物形式通过肾排出，10％以原形排出。',
        },
    }
    
    print('='*70)
    print('修正特定药物 - V3')
    print('='*70)
    
    fixed_count = 0
    for drug_id, drug_fixes in fixes.items():
        if fix_drug(drug_id, drug_fixes):
            fixed_count += 1
    
    print(f'\n共修正 {fixed_count} 个药物')

if __name__ == '__main__':
    main()
