#!/usr/bin/env python3
"""
改进剂型判断逻辑，确保药品名称包含剂型
"""

import json
import re
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')
INDEX_FILE = DATA_DIR / 'index.json'

def extract_dosage_form_from_full_name(full_name):
    """从全名中提取剂型"""
    if not full_name:
        return None
    
    # 定义剂型关键词（按优先级排序）
    dosage_form_patterns = [
        (r'注射液', '注射液'),
        (r'注射用', '注射用'),
        (r'吸入溶液', '吸入溶液'),
        (r'肠溶缓释胶囊', '肠溶缓释胶囊'),
        (r'肠溶胶囊', '肠溶胶囊'),
        (r'缓释胶囊', '缓释胶囊'),
        (r'胶囊', '胶囊'),
        (r'肠溶缓释片', '肠溶缓释片'),
        (r'缓释片', '缓释片'),
        (r'肠溶片', '肠溶片'),
        (r'分散片', '分散片'),
        (r'泡腾片', '泡腾片'),
        (r'咀嚼片', '咀嚼片'),
        (r'含片', '含片'),
        (r'舌下片', '舌下片'),
        (r'贴片', '贴片'),
        (r'片剂', '片'),
        (r'片$', '片'),  # 以"片"结尾
        (r'颗粒', '颗粒'),
        (r'散剂', '散剂'),
        (r'滴眼液', '滴眼液'),
        (r'眼用凝胶', '眼用凝胶'),
        (r'眼膏', '眼膏'),
        (r'滴耳液', '滴耳液'),
        (r'滴鼻液', '滴鼻液'),
        (r'软膏', '软膏'),
        (r'乳膏', '乳膏'),
        (r'凝胶', '凝胶'),
        (r'栓剂', '栓剂'),
        (r'贴膏', '贴膏'),
        (r'膏药', '膏药'),
        (r'喷雾剂', '喷雾剂'),
        (r'气雾剂', '气雾剂'),
        (r'粉雾剂', '粉雾剂'),
        (r'混悬液', '混悬液'),
        (r'口服溶液', '口服溶液'),
        (r'糖浆', '糖浆'),
        (r'酊剂', '酊剂'),
        (r'搽剂', '搽剂'),
        (r'洗剂', '洗剂'),
        (r'涂剂', '涂剂'),
        (r'膜剂', '膜剂'),
        (r'丸剂', '丸剂'),
        (r'滴丸', '滴丸'),
        (r'植入剂', '植入剂'),
        (r'冻干粉针', '冻干粉针'),
    ]
    
    # 移除前缀如(甲)、(乙)等
    clean_name = re.sub(r'^[（\(][甲乙丙自][^）\)]*[）\)]', '', full_name)
    clean_name = re.sub(r'^※▲', '', clean_name)
    
    for pattern, form_name in dosage_form_patterns:
        if re.search(pattern, clean_name):
            return form_name
    
    return None

def update_drug_dosage_form(drug_data):
    """更新单个药物的剂型信息"""
    name = drug_data.get('name', '')
    full_name = drug_data.get('full_name', '')
    current_dosage_form = drug_data.get('dosage_form', '')
    
    changes = []
    
    # 从全名中提取剂型
    extracted_form = extract_dosage_form_from_full_name(full_name)
    
    if extracted_form:
        # 更新剂型字段
        if current_dosage_form != extracted_form:
            drug_data['dosage_form'] = extracted_form
            changes.append(f'剂型: {current_dosage_form} -> {extracted_form}')
        
        # 检查名称是否包含剂型
        if extracted_form not in name:
            # 名称不包含剂型，需要更新
            # 从全名中提取完整药品名（不含前缀）
            clean_full_name = re.sub(r'^[（\(][甲乙丙自][^）\)]*[）\)]', '', full_name)
            clean_full_name = re.sub(r'^※▲', '', clean_full_name)
            
            # 如果全名与当前名称不同，更新名称
            if clean_full_name != name:
                old_name = name
                drug_data['name'] = clean_full_name
                changes.append(f'名称: {old_name} -> {clean_full_name}')
    
    return changes

def main():
    print('='*70)
    print('改进剂型判断逻辑')
    print('='*70)
    
    # 读取index.json
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    updated_count = 0
    changes_list = []
    
    for drug in index:
        drug_id = drug.get('id')
        changes = update_drug_dosage_form(drug)
        
        if changes:
            updated_count += 1
            changes_list.append({
                'id': drug_id,
                'name': drug.get('name', ''),
                'changes': changes
            })
            print(f"\n✅ ID {drug_id}: {drug.get('name', '')}")
            for change in changes:
                print(f"   - {change}")
    
    # 保存更新后的index.json
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    # 同时更新各个药物JSON文件
    print(f'\n{"="*70}')
    print('更新各个药物文件...')
    print(f'{"="*70}')
    
    file_updated = 0
    for drug in index:
        drug_id = drug.get('id')
        file_path = DATA_DIR / f'{drug_id}.json'
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新剂型信息
            old_name = data.get('name', '')
            old_dosage_form = data.get('dosage_form', '')
            
            data['name'] = drug.get('name', '')
            data['dosage_form'] = drug.get('dosage_form', '')
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if old_name != data['name'] or old_dosage_form != data['dosage_form']:
                file_updated += 1
    
    print(f'\n{"="*70}')
    print('处理完成！')
    print(f'共更新 {updated_count} 个药物条目')
    print(f'共更新 {file_updated} 个药物文件')
    print(f'{"="*70}')

if __name__ == '__main__':
    main()
