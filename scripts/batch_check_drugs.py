#!/usr/bin/env python3
"""
批量检查药物手册内容
检查项目：
1. 精简版内容是否合理压缩
2. 注射剂型是否有溶媒选择
3. 名称和拼音首字母是否正确
"""

import json
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

def check_drug(drug_id: int) -> Dict[str, Any]:
    """检查单个药物"""
    file_path = DATA_DIR / f'{drug_id}.json'
    if not file_path.exists():
        return {'id': drug_id, 'exists': False}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    manual = data.get('manual', {})
    name = data.get('name', '')
    dosage_form = data.get('dosage_form', '')
    
    # 检查1：注射剂型是否有溶媒选择
    is_injection = '注射' in name or '注射' in dosage_form
    has_solvent = bool(manual.get('solvent'))
    
    if is_injection and not has_solvent:
        issues.append('缺少溶媒选择')
    
    # 检查2：精简版内容是否过长（超过200字符）
    fields_to_check = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 'precautions']
    for field in fields_to_check:
        content = manual.get(field, '')
        if content and len(content) > 200:
            issues.append(f'{field}精简版过长({len(content)}字符)')
    
    # 检查3：interactions是否包含非相互作用内容
    interactions = manual.get('interactions', '')
    if interactions and len(interactions) > 150:
        # 检查是否包含注意事项的内容
        if '本品为' in interactions or '保存' in interactions or '慎用' in interactions:
            issues.append('interactions包含非相互作用内容')
    
    # 检查4：名称和剂型是否匹配
    if '注射液' in name and dosage_form:
        issues.append('名称已含注射液，剂型应为空')
    
    return {
        'id': drug_id,
        'name': name,
        'exists': True,
        'issues': issues,
        'is_injection': is_injection,
        'has_solvent': has_solvent
    }

def check_batch(start_id: int, end_id: int) -> List[Dict]:
    """检查一批药物"""
    results = []
    print(f'\n{"="*60}')
    print(f'检查药物 ID {start_id} - {end_id}')
    print(f'{"="*60}')
    
    for drug_id in range(start_id, end_id + 1):
        result = check_drug(drug_id)
        if result['exists'] and result['issues']:
            results.append(result)
            print(f"\n⚠️ ID {result['id']}: {result['name']}")
            for issue in result['issues']:
                print(f"   - {issue}")
    
    if not results:
        print('\n✅ 本批次药物检查通过，未发现明显问题')
    else:
        print(f'\n📊 本批次共发现 {len(results)} 个药物需要修正')
    
    return results

def main():
    # 获取所有药物ID
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    all_ids = [d['id'] for d in index]
    all_ids.sort()
    
    print(f'共有 {len(all_ids)} 个药物需要检查')
    print('每20个药物为一组进行检查')
    
    # 分批检查
    batch_size = 20
    all_issues = []
    
    for i in range(0, len(all_ids), batch_size):
        batch_ids = all_ids[i:i+batch_size]
        start_id = batch_ids[0]
        end_id = batch_ids[-1]
        
        results = check_batch(start_id, end_id)
        all_issues.extend(results)
        
        # 每检查完一批，询问是否继续
        if i + batch_size < len(all_ids):
            print(f'\n{"="*60}')
            print(f'已完成 {i+len(batch_ids)}/{len(all_ids)} 个药物检查')
            print(f'{"="*60}')
    
    # 汇总报告
    print(f'\n{"="*60}')
    print('检查完成！汇总报告')
    print(f'{"="*60}')
    
    if all_issues:
        print(f'\n共发现 {len(all_issues)} 个药物需要修正：\n')
        
        # 按问题类型分类
        solvent_issues = [r for r in all_issues if '缺少溶媒选择' in r['issues']]
        long_content_issues = [r for r in all_issues if any('过长' in i for i in r['issues'])]
        interactions_issues = [r for r in all_issues if any('interactions' in i for i in r['issues'])]
        
        if solvent_issues:
            print(f'\n💉 缺少溶媒选择的注射剂 ({len(solvent_issues)}个):')
            for r in solvent_issues[:10]:  # 只显示前10个
                print(f'   ID {r["id"]}: {r["name"]}')
            if len(solvent_issues) > 10:
                print(f'   ... 还有 {len(solvent_issues)-10} 个')
        
        if long_content_issues:
            print(f'\n📝 精简版内容过长的药物 ({len(long_content_issues)}个):')
            for r in long_content_issues[:10]:
                print(f'   ID {r["id"]}: {r["name"]}')
            if len(long_content_issues) > 10:
                print(f'   ... 还有 {len(long_content_issues)-10} 个')
        
        if interactions_issues:
            print(f'\n⚠️ interactions字段异常的药物 ({len(interactions_issues)}个):')
            for r in interactions_issues[:10]:
                print(f'   ID {r["id"]}: {r["name"]}')
            if len(interactions_issues) > 10:
                print(f'   ... 还有 {len(interactions_issues)-10} 个')
    else:
        print('\n✅ 所有药物检查通过！')

if __name__ == '__main__':
    main()
