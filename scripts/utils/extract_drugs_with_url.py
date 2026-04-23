#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从清单中提取有网址的药品
"""

import re
import json
from pathlib import Path

LIST_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/drugs_without_manual_list.txt")
OUTPUT_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/common_drugs_batch70.json")

def extract_drugs():
    """提取有网址的药品"""
    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    drugs = []
    # 匹配格式: "- 药品名 剂型 https://..."
    # 或者: "- 药品名 https://..."
    lines = content.split('\n')
    
    current_dosage_form = ""
    for line in lines:
        line = line.strip()
        
        # 检测剂型标题行
        if ':' in line and '个' in line:
            # 提取剂型
            match = re.match(r'(.+):\s*\d+\s*个', line)
            if match:
                current_dosage_form = match.group(1).strip()
            continue
        
        # 匹配药品行
        if line.startswith('- ') or line.startswith('  - '):
            # 提取网址
            url_match = re.search(r'https?://\S+', line)
            if url_match:
                url = url_match.group(0)
                # 提取药品名
                # 格式: "- 药品名" 或 "- ※▲药品名"
                name_match = re.match(r'\s*-\s+([※▲]*[^\s]+(?:\s+[^\s]+)*)', line)
                if name_match:
                    name = name_match.group(1).strip()
                    # 清理网址后面的内容
                    name = re.sub(r'\s+https.*$', '', name)
                    
                    drugs.append({
                        'name': name,
                        'dosage_form': current_dosage_form if current_dosage_form else '其他',
                        'url': url,
                        'full_info': f"{name} {url}"
                    })
    
    return drugs

def main():
    drugs = extract_drugs()
    print(f"提取到 {len(drugs)} 个有网址的药品")
    
    # 保存为JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(drugs, f, ensure_ascii=False, indent=2)
    
    print(f"\n已保存到: {OUTPUT_FILE}")
    print("\n药品列表:")
    for i, drug in enumerate(drugs, 1):
        print(f"{i}. {drug['name']} ({drug['dosage_form']})")

if __name__ == '__main__':
    main()
