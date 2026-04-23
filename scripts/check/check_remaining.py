#!/usr/bin/env python3
import re
import json
import glob

# 读取所有有网址的药品
with_url = []
with open('pharmacist-handbook/data/drugs_without_manual.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('=') or line.startswith('没有'):
            continue
        match = re.match(r'(\d+)\.\s+(.+?)\s+\|\s+(.+?)\s+\|\s+(.+)', line)
        if match:
            num = match.group(1)
            name = match.group(2).strip()
            dosage = match.group(3).strip()
            full_info = match.group(4).strip()
            url_match = re.search(r'https?://\S+', full_info)
            if url_match:
                with_url.append({
                    'num': int(num),
                    'name': name,
                    'dosage_form': dosage,
                    'full_info': full_info,
                    'url': url_match.group(0)
                })

# 加载已处理的药品
processed = set()
batch_files = glob.glob('pharmacist-handbook/data/common_drugs_batch*.json')
for batch_file in batch_files:
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for drug in data:
                key = f"{drug.get('name', '')}|{drug.get('dosage_form', '')}"
                processed.add(key)
    except:
        pass

# 过滤掉已处理的药品
remaining = []
for drug in with_url:
    key = f"{drug['name']}|{drug['dosage_form']}"
    if key not in processed:
        remaining.append(drug)

print(f"有网址的药品总数: {len(with_url)}")
print(f"已处理: {len(processed)}")
print(f"待处理: {len(remaining)}")
print(f"\n已创建的批次文件: {len(batch_files)} 个")

# 显示前20个待处理药品
print(f"\n前20个待处理药品:")
for i, drug in enumerate(remaining[:20], 1):
    print(f"{i}. {drug['name']} | {drug['dosage_form']}")
