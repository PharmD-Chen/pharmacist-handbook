#!/usr/bin/env python3
"""
更新 index.json 中白脉软膏的名称和拼音
"""

import json
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

def main():
    print('读取 index.json...')
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)

    # 查找并更新 ID 502
    updated = False
    for drug in index:
        if drug['id'] == 502:
            print(f'找到 ID 502: {drug}')
            drug['name'] = '白脉软膏'
            drug['dosage_form'] = ''
            drug['pinyin'] = 'baimairuangao'
            drug['pinyin_initials'] = 'bmrg'
            drug['dosage_form_pinyin'] = ''
            drug['dosage_form_initials'] = ''
            print(f'更新后: {drug}')
            updated = True
            break

    if updated:
        print('写入更新后的 index.json...')
        with open(DATA_DIR / 'index.json', 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        print('✅ 完成!')
    else:
        print('❌ 未找到 ID 502')

if __name__ == '__main__':
    main()
