#!/usr/bin/env python3
"""
修正特定药物的手册内容
"""

import json
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
        # 氨茶碱 (ID: 6)
        6: {
            'solvent': '静滴：以5％～10％葡萄糖注射液稀释；静注：每25～100mg用5％葡萄糖注射液稀释至20～40ml。',
        },
        
        # 氟尿嘧啶 (ID: 7)
        7: {
            'pharmacokinetics': 't1/2约10-20分钟，主要在肝脏代谢，经肾脏排泄。',
            'solvent': '静滴：以5%葡萄糖注射液或0.9%氯化钠注射液稀释；静注：直接注射或适当稀释。',
        },
        
        # 头孢他啶阿维巴坦 (ID: 15)
        15: {
            'solvent': '静滴：每2.5g用10ml注射用水溶解，再以0.9%氯化钠注射液或5%葡萄糖注射液100-250ml稀释，滴注时间2小时。',
        },
        
        # 注射用紫杉醇聚合物胶束 (ID: 16)
        16: {
            'solvent': '静滴：用5%葡萄糖注射液或0.9%氯化钠注射液稀释，滴注时间3小时。',
        },
        
        # 注射用替加环素 (ID: 17)
        17: {
            'solvent': '静滴：每50mg用5.3ml注射用水或0.9%氯化钠注射液溶解，再以0.9%氯化钠注射液或5%葡萄糖注射液100ml稀释，滴注时间30-60分钟。',
        },
        
        # 注射用鼠神经生长因子 (ID: 19)
        19: {
            'pharmacokinetics': '皮下或肌肉注射后迅速吸收，t1/2约2-3小时，主要经肾脏排泄。',
            'solvent': '肌注/皮下：每支用2ml注射用水溶解。',
        },
    }
    
    print('='*70)
    print('修正特定药物')
    print('='*70)
    
    fixed_count = 0
    for drug_id, drug_fixes in fixes.items():
        if fix_drug(drug_id, drug_fixes):
            fixed_count += 1
    
    print(f'\n共修正 {fixed_count} 个药物')

if __name__ == '__main__':
    main()
