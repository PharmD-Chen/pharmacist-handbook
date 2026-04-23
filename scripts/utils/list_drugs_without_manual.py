#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出所有缺少说明书的药品清单
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook")
DRUGS_FILE = BASE_DIR / "data/drugs.js"
OUTPUT_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/drugs_without_manual_list.txt")

def load_drugs():
    """加载药品数据"""
    with open(DRUGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    return []

def main():
    drugs = load_drugs()
    
    # 找出缺少说明书的药品
    drugs_without_manual = []
    for drug in drugs:
        manual = drug.get('manual', {})
        if not manual or not any(manual.values()):
            drugs_without_manual.append({
                'id': drug.get('id', 'N/A'),
                'name': drug.get('name', '未知'),
                'dosage_form': drug.get('dosage_form', '未知'),
                'full_name': drug.get('full_name', ''),
                'pinyin_initials': drug.get('pinyin_initials', '')
            })
    
    # 按剂型分组统计
    dosage_form_groups = defaultdict(list)
    for drug in drugs_without_manual:
        dosage_form_groups[drug['dosage_form']].append(drug)
    
    # 生成报告
    lines = []
    lines.append("="*80)
    lines.append("缺少说明书的药品清单")
    lines.append("="*80)
    lines.append(f"\n总计: {len(drugs_without_manual)} 个药品\n")
    
    # 按剂型分组显示
    lines.append("="*80)
    lines.append("按剂型分类统计")
    lines.append("="*80)
    for dosage_form in sorted(dosage_form_groups.keys()):
        count = len(dosage_form_groups[dosage_form])
        lines.append(f"\n{dosage_form}: {count} 个")
        for drug in dosage_form_groups[dosage_form]:
            lines.append(f"  - {drug['name']}")
    
    # 完整清单
    lines.append("\n" + "="*80)
    lines.append("完整清单（按ID排序）")
    lines.append("="*80)
    
    # 按ID排序
    sorted_drugs = sorted(drugs_without_manual, key=lambda x: x['id'] if x['id'] != 'N/A' else 0)
    
    for i, drug in enumerate(sorted_drugs, 1):
        lines.append(f"\n{i}. ID: {drug['id']}")
        lines.append(f"   名称: {drug['name']}")
        lines.append(f"   剂型: {drug['dosage_form']}")
        if drug['full_name']:
            lines.append(f"   完整名称: {drug['full_name']}")
        if drug['pinyin_initials']:
            lines.append(f"   拼音首字母: {drug['pinyin_initials']}")
    
    # 保存到文件
    content = "\n".join(lines)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 同时输出到控制台
    print(content)
    print(f"\n{'='*80}")
    print(f"✅ 清单已保存到: {OUTPUT_FILE}")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
