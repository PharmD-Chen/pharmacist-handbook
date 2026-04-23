#!/usr/bin/env python3
"""
修复药品名称 - 最终版
彻底清理所有前缀，只保留药品名称+剂型
"""

import json
import re
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')
INDEX_FILE = DATA_DIR / 'index.json'

def clean_drug_name(full_name):
    """从全名中清理出纯净的药品名称（包含剂型）"""
    if not full_name:
        return None
    
    # 移除所有前缀：※▲、(甲)、(乙)、(乙10%)等
    clean_name = full_name
    
    # 移除※▲
    clean_name = re.sub(r'^※▲', '', clean_name)
    
    # 移除医保类别前缀，包括带百分比的情况
    clean_name = re.sub(r'^[（\(][甲乙丙自]\d*%?[）\)]', '', clean_name)
    clean_name = re.sub(r'^[（\(][甲乙丙自][）\)]', '', clean_name)
    
    # 移除后缀 [国基]、[市基]等
    clean_name = re.sub(r'\[.*?\]', '', clean_name)
    
    return clean_name.strip()

def main():
    print('='*70)
    print('修复药品名称 - 最终版')
    print('='*70)
    
    # 读取index.json
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    updated_count = 0
    
    for drug in index:
        drug_id = drug.get('id')
        name = drug.get('name', '')
        full_name = drug.get('full_name', '')
        
        # 从全名提取纯净名称
        new_name = clean_drug_name(full_name)
        
        # 如果新名称与原名称不同
        if new_name and new_name != name:
            print(f"\n✅ ID {drug_id}:")
            print(f"   原名称: {name}")
            print(f"   新名称: {new_name}")
            drug['name'] = new_name
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
            new_name = drug.get('name', '')
            
            if old_name != new_name:
                data['name'] = new_name
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                file_updated += 1
    
    print(f'\n{"="*70}')
    print('处理完成！')
    print(f'共更新 {updated_count} 个药物条目')
    print(f'共更新 {file_updated} 个药物文件')
    print(f'{"="*70}')

if __name__ == '__main__':
    main()
