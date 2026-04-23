#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理药品信息抓取和导入
"""
import re
import json
import os
import sys

# 添加scripts目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pharmacist-handbook', 'scripts'))

def extract_drugs_with_url():
    """提取有网址的药品"""
    drugs = []
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
                    drugs.append({
                        'num': int(num),
                        'name': name,
                        'dosage': dosage,
                        'full_info': full_info,
                        'url': url_match.group(0)
                    })
    return drugs

def create_batch_json(drugs, batch_size=50, start_idx=0):
    """创建批次JSON文件"""
    batch_drugs = drugs[start_idx:start_idx + batch_size]
    if not batch_drugs:
        return None
    
    batch_num = start_idx // batch_size + 67  # 从batch67开始
    output_file = f'pharmacist-handbook/data/common_drugs_batch{batch_num}.json'
    
    result = []
    for drug in batch_drugs:
        result.append({
            'name': drug['name'],
            'dosage_form': drug['dosage'],
            'url': drug['url'],
            'full_info': drug['full_info']
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return output_file, batch_drugs

if __name__ == '__main__':
    # 提取所有有网址的药品
    all_drugs = extract_drugs_with_url()
    print(f"共有 {len(all_drugs)} 个药品有网址")
    
    # 获取下一个批次号
    import glob
    existing_batches = glob.glob('pharmacist-handbook/data/common_drugs_batch*.json')
    next_batch = 67
    if existing_batches:
        batch_numbers = []
        for f in existing_batches:
            match = re.search(r'batch(\d+)\.json', f)
            if match:
                batch_numbers.append(int(match.group(1)))
        if batch_numbers:
            next_batch = max(batch_numbers) + 1
    
    print(f"\n下一个批次号: batch{next_batch}")
    
    # 创建新批次（处理前50个）
    # 检查哪些药品已经处理过
    processed = set()
    for batch_file in existing_batches:
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
    for drug in all_drugs:
        key = f"{drug['name']}|{drug['dosage']}"
        if key not in processed:
            remaining.append(drug)
    
    print(f"\n已处理: {len(processed)} 个")
    print(f"待处理: {len(remaining)} 个")
    
    if remaining:
        # 创建新批次
        batch_file, batch_drugs = create_batch_json(remaining, 50, 0)
        print(f"\n已创建批次文件: {batch_file}")
        print(f"包含 {len(batch_drugs)} 个药品:")
        for i, drug in enumerate(batch_drugs[:10], 1):
            print(f"  {i}. {drug['name']} | {drug['dosage']}")
        if len(batch_drugs) > 10:
            print(f"  ... 还有 {len(batch_drugs) - 10} 个")
