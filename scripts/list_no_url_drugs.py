#!/usr/bin/env python3
"""
列出仍缺失网址的药品目录
"""

import json
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

# 加载索引
with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# 找出无网址的药品
no_url_drugs = []

for drug in index:
    drug_id = drug['id']
    json_file = DATA_DIR / f'{drug_id}.json'

    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        url = data.get('url', {}).get('hnysfww', '')
        if not url:
            no_url_drugs.append({
                'id': drug_id,
                'name': drug['name'],
                'dosage_form': drug.get('dosage_form', ''),
                'types': ','.join(drug.get('types', []))
            })

# 打印结果
print('=' * 80)
print(f'仍缺失网址的药品目录 (共 {len(no_url_drugs)} 个)')
print('=' * 80)
print()
print('| ID | 药品名称 | 剂型 | 类型 |')
print('|----|---------|------|------|')

for drug in sorted(no_url_drugs, key=lambda x: x['id']):
    print(f"| {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['types']} |")

print()
print('=' * 80)
print(f'总计: {len(no_url_drugs)} 个药品缺失网址')
print('=' * 80)
