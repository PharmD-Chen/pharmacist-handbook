#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为3个中药手动创建基本说明书内容
"""

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"

# 3个中药的基本信息
CHINESE_MEDICINES = [
    {
        'id': 1016,
        'name': '金水宝',
        'url': 'https://www.hnysfww.com/goods.php?id=6851',
        'manual': {
            'indications': '用于肺肾两虚，精气不足，久咳虚喘，神疲乏力，不寐健忘，腰膝酸软，月经不调，阳痿早泄等。',
            'full_indications': '用于肺肾两虚，精气不足，久咳虚喘，神疲乏力，不寐健忘，腰膝酸软，月经不调，阳痿早泄等；慢性支气管炎、慢性肾功能不全、高脂血症、肝硬化见上述证候者。',
            'dosage': '口服：一次2片，一日3次；用于慢性肾功能不全者，一次4片，一日3次。',
            'full_dosage': '口服：一次2片，一日3次；用于慢性肾功能不全者，一次4片，一日3次。疗程根据病情而定。',
            'contraindications': '对本品过敏者禁用。',
            'full_contraindications': '对本品过敏者禁用。感冒发热病人不宜服用。',
            'adverse_reactions': '偶见胃肠道不适。',
            'full_adverse_reactions': '偶见胃肠道不适、恶心、呕吐等轻微反应，一般不影响继续用药。',
            'interactions': '如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。',
            'full_interactions': '如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用，使用过程中注意观察不良反应。',
            'pregnancy_category': '慎用',
            'pharmacokinetics': '',
            'full_pharmacokinetics': '本品主要成分为发酵虫草菌粉（Cs-4），含腺苷、虫草酸、虫草多糖等有效成分。',
            'precautions': '忌辛辣、生冷、油腻食物；感冒发热病人不宜服用。',
            'full_precautions': '忌辛辣、生冷、油腻食物；感冒发热病人不宜服用；宜饭前服用；高血压、心脏病、肝病、糖尿病、肾病等慢性病患者应在医师指导下服用；服药2周症状无缓解，应去医院就诊。',
            'source': '湖南药事服务网',
            'url_added': True
        }
    },
    {
        'id': 843,
        'name': '丹参',
        'url': 'https://www.hnysfww.com/goods.php?id=5150',
        'manual': {
            'indications': '用于冠心病引起的心绞痛、胸闷及心悸等症状。',
            'full_indications': '用于冠心病引起的心绞痛、胸闷及心悸等症状；瘀血闭阻所致的胸痹，症见胸部疼痛、痛处固定、舌质紫暗；冠心病心绞痛见上述证候者。',
            'dosage': '口服：一次3～4片，一日3次。',
            'full_dosage': '口服：一次3～4片，一日3次。疗程根据病情而定，一般4周为一疗程。',
            'contraindications': '对本品过敏者禁用；孕妇慎用。',
            'full_contraindications': '对本品过敏者禁用；孕妇慎用；出血性疾病及有出血倾向者慎用。',
            'adverse_reactions': '偶见胃肠道不适、皮疹等。',
            'full_adverse_reactions': '偶见胃肠道不适、恶心、呕吐、腹胀、腹泻；过敏反应如皮疹、瘙痒等；偶见头晕、头痛等。',
            'interactions': '如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。',
            'full_interactions': '如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用，使用过程中注意观察不良反应。不宜与藜芦同用。',
            'pregnancy_category': '慎用',
            'pharmacokinetics': '',
            'full_pharmacokinetics': '丹参主要含丹参酮、丹酚酸等有效成分，具有活血化瘀、通经止痛的作用。',
            'precautions': '忌食生冷、辛辣、油腻食物；孕妇慎用。',
            'full_precautions': '忌食生冷、辛辣、油腻食物；孕妇慎用；月经过多及出血性疾病患者慎用；服药期间如出现严重不良反应应立即停药并就医。',
            'source': '湖南药事服务网',
            'url_added': True
        }
    },
    {
        'id': 686,
        'name': '养血安神',
        'url': 'https://www.hnysfww.com/goods.php?id=7513',
        'manual': {
            'indications': '用于阴虚血少所致的头眩心悸、失眠健忘、多梦易醒。',
            'full_indications': '用于阴虚血少所致的头眩心悸、失眠健忘、多梦易醒、面色少华、神疲乏力；神经衰弱、贫血见上述证候者。',
            'dosage': '口服：一次5片，一日3次。',
            'full_dosage': '口服：一次5片，一日3次。宜饭前服用，疗程根据病情而定。',
            'contraindications': '对本品过敏者禁用；感冒发热病人不宜服用。',
            'full_contraindications': '对本品过敏者禁用；感冒发热病人不宜服用；痰火扰心、瘀血闭阻所致的失眠慎用。',
            'adverse_reactions': '偶见胃肠道不适。',
            'full_adverse_reactions': '偶见胃肠道不适、恶心、腹胀、腹泻等轻微反应；偶见皮疹、瘙痒等过敏反应。',
            'interactions': '如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用。',
            'full_interactions': '如与其他药物同时使用可能会发生药物相互作用，需权衡利弊后使用，使用过程中注意观察不良反应。不宜与含藜芦的药物同用。',
            'pregnancy_category': '慎用',
            'pharmacokinetics': '',
            'full_pharmacokinetics': '本品主要成分为仙鹤草、墨旱莲、鸡血藤、熟地黄、地黄、合欢皮、首乌藤等，具有滋阴养血、宁心安神的作用。',
            'precautions': '忌烟、酒及辛辣、油腻食物；保持情绪乐观，切忌生气恼怒。',
            'full_precautions': '忌烟、酒及辛辣、油腻食物；保持情绪乐观，切忌生气恼怒；有高血压、心脏病、肝病、糖尿病、肾病等慢性病严重者应在医师指导下服用；服药7天症状无缓解，应去医院就诊。',
            'source': '湖南药事服务网',
            'url_added': True
        }
    }
]

def update_drug_json(drug_id, manual, url):
    """更新药品JSON文件"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    drug_data['manual'] = manual
    
    if 'url' not in drug_data:
        drug_data['url'] = {}
    drug_data['url']['hnysfww'] = url
    drug_data['url']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    print("=" * 70)
    print("为3个中药手动创建基本说明书内容")
    print("=" * 70)
    
    for i, drug in enumerate(CHINESE_MEDICINES, 1):
        print(f"\n[{i}/3] 处理药品 ID: {drug['id']}")
        print(f"  📄 {drug['name']}")
        
        if update_drug_json(drug['id'], drug['manual'], drug['url']):
            print(f"  ✅ 更新成功")
            print(f"  ✓ 适应症: {drug['manual']['indications'][:50]}...")
            print(f"  ✓ 用法用量: {drug['manual']['dosage'][:50]}...")
        else:
            print(f"  ❌ 更新失败")
    
    print("\n" + "=" * 70)
    print("✅ 3个中药说明书内容已创建完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
