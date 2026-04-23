#!/usr/bin/env python3
"""
检查药物手册内容并自动修复常见问题
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

def simplify_text(text: str, max_length: int = 150) -> str:
    """简化文本内容"""
    if not text:
        return text
    
    # 去除HTML标签
    text = re.sub(r'<br\s*/?>', ' ', text)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除多余空格
    text = ' '.join(text.split())
    
    # 如果仍然过长，截断并添加省略号
    if len(text) > max_length:
        # 尝试在句子边界截断
        sentences = re.split(r'([。；])', text)
        result = ''
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punct = sentences[i+1] if i+1 < len(sentences) else ''
            if len(result) + len(sentence) + len(punct) <= max_length:
                result += sentence + punct
            else:
                break
        text = result if result else text[:max_length] + '...'
    
    return text.strip()

def extract_solvent_from_dosage(dosage: str) -> str:
    """从用法用量中提取溶媒信息"""
    solvents = []
    
    # 查找溶媒相关描述
    patterns = [
        r'(?:肌内注射|肌注)[^。]*?(?:注射用水|生理盐水|葡萄糖|氯化钠)[^。]*?(?:溶解|稀释)',
        r'(?:静脉注射|静注)[^。]*?(?:注射用水|生理盐水|葡萄糖|氯化钠)[^。]*?(?:溶解|稀释)',
        r'(?:静脉滴注|静滴)[^。]*?(?:注射用水|生理盐水|葡萄糖|氯化钠)[^。]*?(?:溶解|稀释|滴注)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, dosage)
        solvents.extend(matches)
    
    if solvents:
        return '；'.join(list(set(solvents))[:3])  # 最多取3个
    return ''

def check_and_fix_drug(drug_id: int) -> Tuple[bool, List[str]]:
    """检查并修复单个药物，返回(是否修改, 修改记录)"""
    file_path = DATA_DIR / f'{drug_id}.json'
    if not file_path.exists():
        return False, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_data = json.dumps(data, ensure_ascii=False, sort_keys=True)
    manual = data.get('manual', {})
    name = data.get('name', '')
    dosage_form = data.get('dosage_form', '')
    changes = []
    
    is_injection = '注射' in name or '注射' in dosage_form
    
    # 修复1：注射剂型添加溶媒选择
    if is_injection and not manual.get('solvent'):
        full_dosage = manual.get('full_dosage', '')
        if full_dosage:
            solvent = extract_solvent_from_dosage(full_dosage)
            if solvent:
                manual['solvent'] = solvent
                changes.append('添加溶媒选择')
    
    # 修复2：精简版内容过长
    fields_to_simplify = {
        'indications': 180,
        'dosage': 180,
        'contraindications': 150,
        'adverse_reactions': 180,
        'precautions': 180
    }
    
    for field, max_len in fields_to_simplify.items():
        content = manual.get(field, '')
        if content and len(content) > max_len:
            # 检查是否有对应的full_字段
            full_field = f'full_{field}'
            if full_field in manual and manual[full_field]:
                # 简化精简版
                simplified = simplify_text(manual[full_field], max_len)
                if simplified and len(simplified) < len(content):
                    manual[field] = simplified
                    changes.append(f'简化{field}')
    
    # 修复3：修正interactions字段（如果包含注意事项内容）
    interactions = manual.get('interactions', '')
    if interactions and len(interactions) > 150:
        # 如果包含非相互作用内容，重置为简短版本
        if '本品为' in interactions or '保存不当' in interactions or '如发现' in interactions:
            manual['interactions'] = '暂未发现有临床意义的药物相互作用。'
            changes.append('修正interactions字段')
    
    # 检查是否有修改
    new_data = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if new_data != original_data:
        # 保存修改
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, changes
    
    return False, []

def process_batch(start_idx: int, end_idx: int, all_ids: List[int]) -> Dict:
    """处理一批药物"""
    results = {
        'checked': 0,
        'fixed': 0,
        'details': []
    }
    
    batch_ids = all_ids[start_idx:end_idx]
    
    print(f'\n{"="*70}')
    print(f'处理第 {start_idx+1}-{min(end_idx, len(all_ids))} 个药物 (共 {len(all_ids)} 个)')
    print(f'{"="*70}')
    
    for drug_id in batch_ids:
        results['checked'] += 1
        modified, changes = check_and_fix_drug(drug_id)
        
        if modified:
            results['fixed'] += 1
            results['details'].append({
                'id': drug_id,
                'changes': changes
            })
            # 读取药物名称
            file_path = DATA_DIR / f'{drug_id}.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ ID {drug_id}: {data.get('name', '')}")
            for change in changes:
                print(f"   - {change}")
    
    print(f'\n本批次: 检查 {results["checked"]} 个, 修复 {results["fixed"]} 个')
    return results

def main():
    # 获取所有药物ID
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    all_ids = [d['id'] for d in index]
    all_ids.sort()
    
    print(f'共有 {len(all_ids)} 个药物')
    print('每20个药物为一组进行处理')
    
    # 先处理前100个药物作为示例
    batch_size = 20
    total_fixed = 0
    
    for i in range(0, min(100, len(all_ids)), batch_size):
        results = process_batch(i, i + batch_size, all_ids)
        total_fixed += results['fixed']
        
        if i + batch_size < len(all_ids) and i + batch_size < 100:
            print(f'\n已完成 {min(i+batch_size, 100)}/100 个药物')
    
    # 汇总
    print(f'\n{"="*70}')
    print('前100个药物处理完成！')
    print(f'共修复 {total_fixed} 个药物')
    print(f'{"="*70}')
    
    # 询问是否继续处理剩余药物
    remaining = len(all_ids) - 100
    if remaining > 0:
        print(f'\n还有 {remaining} 个药物待处理')
        print('建议先检查前100个药物的修复效果，确认无误后再继续')

if __name__ == '__main__':
    main()
