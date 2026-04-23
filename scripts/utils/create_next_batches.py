#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建后续批次文件（batch68及以后）
"""

import json
import re
from pathlib import Path

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
                        'dosage_form': dosage,
                        'full_info': full_info,
                        'url': url_match.group(0)
                    })
    return drugs

def load_processed_drugs():
    """加载已处理的药品"""
    processed = set()
    import glob
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
    return processed

def create_batches():
    """创建后续批次"""
    all_drugs = extract_drugs_with_url()
    processed = load_processed_drugs()
    
    # 过滤掉已处理的药品
    remaining = []
    for drug in all_drugs:
        key = f"{drug['name']}|{drug['dosage_form']}"
        if key not in processed:
            remaining.append(drug)
    
    print(f"有网址的药品总数: {len(all_drugs)}")
    print(f"已处理: {len(processed)}")
    print(f"待处理: {len(remaining)}")
    
    # 创建batch68-71（每批50个）
    batch_size = 50
    start_batch = 68
    
    created = []
    for i in range(0, min(200, len(remaining)), batch_size):
        batch_num = start_batch + i // batch_size
        batch_drugs = remaining[i:i + batch_size]
        
        if not batch_drugs:
            break
        
        output_file = f'pharmacist-handbook/data/common_drugs_batch{batch_num}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_drugs, f, ensure_ascii=False, indent=2)
        
        created.append((batch_num, output_file, len(batch_drugs)))
        print(f"\n已创建 batch{batch_num}: {len(batch_drugs)} 个药品")
        for j, drug in enumerate(batch_drugs[:5], 1):
            print(f"  {j}. {drug['name']} | {drug['dosage_form']}")
        if len(batch_drugs) > 5:
            print(f"  ... 还有 {len(batch_drugs) - 5} 个")
    
    return created

if __name__ == '__main__':
    create_batches()
