#!/usr/bin/env python3
"""
修复药品名称，移除特殊前缀，确保包含剂型
"""

import json
import re
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')
INDEX_FILE = DATA_DIR / 'index.json'

def clean_name(name):
    """清理名称中的特殊前缀"""
    if not name:
        return name
    
    # 移除※▲前缀
    name = re.sub(r'^※▲', '', name)
    # 移除医保类别前缀
    name = re.sub(r'^[（\(][甲乙丙自][^）\)]*[）\)]', '', name)
    # 移除[国基]、[市基]等后缀
    name = re.sub(r'\[.*?\]', '', name)
    
    return name.strip()

def extract_dosage_form(name):
    """从名称中提取剂型"""
    patterns = [
        (r'注射液$', '注射液'),
        (r'注射用', '注射用'),
        (r'吸入溶液$', '吸入溶液'),
        (r'肠溶缓释胶囊$', '肠溶缓释胶囊'),
        (r'肠溶胶囊$', '肠溶胶囊'),
        (r'缓释胶囊$', '缓释胶囊'),
        (r'软胶囊$', '软胶囊'),
        (r'胶囊$', '胶囊'),
        (r'肠溶缓释片$', '肠溶缓释片'),
        (r'缓释片$', '缓释片'),
        (r'肠溶片$', '肠溶片'),
        (r'分散片$', '分散片'),
        (r'泡腾片$', '泡腾片'),
        (r'咀嚼片$', '咀嚼片'),
        (r'含片$', '含片'),
        (r'舌下片$', '舌下片'),
        (r'贴片$', '贴片'),
        (r'片$', '片'),
        (r'颗粒$', '颗粒'),
        (r'散剂$', '散剂'),
        (r'滴眼液$', '滴眼液'),
        (r'眼用凝胶$', '眼用凝胶'),
        (r'眼膏$', '眼膏'),
        (r'滴耳液$', '滴耳液'),
        (r'滴鼻液$', '滴鼻液'),
        (r'乳膏$', '乳膏'),
        (r'软膏$', '软膏'),
        (r'凝胶$', '凝胶'),
        (r'栓剂$', '栓剂'),
        (r'贴膏$', '贴膏'),
        (r'膏药$', '膏药'),
        (r'喷雾剂$', '喷雾剂'),
        (r'气雾剂$', '气雾剂'),
        (r'粉雾剂$', '粉雾剂'),
        (r'混悬液$', '混悬液'),
        (r'口服溶液$', '口服溶液'),
        (r'糖浆$', '糖浆'),
        (r'酊剂$', '酊剂'),
        (r'搽剂$', '搽剂'),
        (r'洗剂$', '洗剂'),
        (r'涂剂$', '涂剂'),
        (r'膜剂$', '膜剂'),
        (r'丸剂$', '丸剂'),
        (r'滴丸$', '滴丸'),
        (r'植入剂$', '植入剂'),
        (r'冻干粉针$', '冻干粉针'),
    ]
    
    for pattern, form in patterns:
        if re.search(pattern, name):
            return form
    return ''

def main():
    print('='*70)
    print('修复药品名称')
    print('='*70)
    
    # 读取index.json
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    updated_count = 0
    
    for drug in index:
        drug_id = drug.get('id')
        name = drug.get('name', '')
        full_name = drug.get('full_name', '')
        
        # 清理名称
        new_name = clean_name(name)
        
        # 如果清理后的名称与原名称不同
        if new_name != name:
            print(f"\n✅ ID {drug_id}:")
            print(f"   原名称: {name}")
            print(f"   新名称: {new_name}")
            drug['name'] = new_name
            updated_count += 1
        
        # 更新剂型
        current_form = drug.get('dosage_form', '')
        extracted_form = extract_dosage_form(new_name)
        
        if extracted_form and extracted_form != current_form:
            print(f"   剂型: {current_form} -> {extracted_form}")
            drug['dosage_form'] = extracted_form
            if new_name == name:
                updated_count += 1
    
    # 保存index.json
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    # 更新各个药物文件
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
            
            old_name = data.get('name', '')
            old_form = data.get('dosage_form', '')
            
            data['name'] = drug.get('name', '')
            data['dosage_form'] = drug.get('dosage_form', '')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if old_name != data['name'] or old_form != data['dosage_form']:
                file_updated += 1
    
    print(f'\n{"="*70}')
    print('处理完成！')
    print(f'共更新 {updated_count} 个药物条目')
    print(f'共更新 {file_updated} 个药物文件')
    print(f'{"="*70}')

if __name__ == '__main__':
    main()
