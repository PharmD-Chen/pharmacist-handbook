#!/usr/bin/env python3
"""
检查12个药品的当前状态
"""

import json
from pathlib import Path

DRUGS_LIST = [
    {"id": 113, "name": "5%葡萄糖"},
    {"id": 114, "name": "50%葡萄糖"},
    {"id": 794, "name": "※▲丁甘交联玻璃酸钠"},
    {"id": 35, "name": "盐酸利多卡因"},
    {"id": 432, "name": "盐酸曲马多"},
    {"id": 130, "name": "盐酸氨溴索"},
    {"id": 631, "name": "盐酸精氨酸"},
    {"id": 1029, "name": "硫酸镁"},
    {"id": 262, "name": "硫酸阿托品"},
    {"id": 983, "name": "碳酸氢钠"},
    {"id": 509, "name": "维生素C"},
    {"id": 137, "name": "重酒石酸去甲肾上腺素"},
]

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")


def check_drug(drug_id):
    """检查单个药品"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        source = manual.get('source', '无')
        
        # 检查关键字段
        has_indications = bool(manual.get('indications', '').strip())
        has_dosage = bool(manual.get('dosage', '').strip())
        has_contraindications = bool(manual.get('contraindications', '').strip())
        has_adverse = bool(manual.get('adverse_reactions', '').strip())
        
        info_count = sum([has_indications, has_dosage, has_contraindications, has_adverse])
        
        return {
            'source': source,
            'info_count': info_count,
            'has_indications': has_indications,
            'has_dosage': has_dosage,
            'has_contraindications': has_contraindications,
            'has_adverse': has_adverse
        }
    except Exception as e:
        return {'error': str(e)}


print("=" * 100)
print("12个药品更新后的状态检查")
print("=" * 100)
print(f"{'ID':<6} {'药品名称':<25} {'来源':<20} {'信息完整度':<10} {'适应症':<6} {'用量':<6} {'禁忌':<6} {'不良反应':<8}")
print("-" * 100)

for drug in DRUGS_LIST:
    result = check_drug(drug['id'])
    
    if 'error' in result:
        print(f"{drug['id']:<6} {drug['name']:<25} 错误: {result['error']}")
    else:
        source = result['source']
        info_count = result['info_count']
        
        # 信息完整度显示
        if info_count >= 4:
            info_status = "✅ 完整"
        elif info_count >= 2:
            info_status = f"⚠️  {info_count}/4"
        else:
            info_status = f"❌ {info_count}/4"
        
        ind = "✓" if result['has_indications'] else "✗"
        dos = "✓" if result['has_dosage'] else "✗"
        con = "✓" if result['has_contraindications'] else "✗"
        adv = "✓" if result['has_adverse'] else "✗"
        
        print(f"{drug['id']:<6} {drug['name']:<25} {source:<20} {info_status:<10} {ind:<6} {dos:<6} {con:<6} {adv:<8}")

print("=" * 100)
