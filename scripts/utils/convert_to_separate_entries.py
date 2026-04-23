#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将药品数据从合并格式转换为每个规格独立条目
"""

import json
import re
from pathlib import Path

DRUGS_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js")

def load_drugs():
    """加载药品数据"""
    with open(DRUGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    return []

def convert_to_separate_entries(drugs):
    """将合并的药品条目转换为每个规格独立条目"""
    new_drugs = []
    new_id = 1
    
    for drug in drugs:
        # 获取药品手册信息
        manual = drug.get('manual', {})
        
        # 为每个规格创建独立条目
        for spec in drug.get('specifications', []):
            new_drug = {
                "id": new_id,
                "name": drug['name'],
                "dosage_form": drug['dosage_form'],
                "full_name": drug['full_name'],
                "chemical_name": drug.get('chemical_name', ''),
                "types": drug.get('types', []),
                "manufacturers": [spec['manufacturer']],  # 只保留当前规格的厂家
                "specifications": [spec],  # 只包含当前规格
                "spec_count": 1,
                "manual": manual,  # 所有规格共享相同的手册内容
                "pinyin": drug.get('pinyin', ''),
                "pinyin_initials": drug.get('pinyin_initials', ''),
                "dosage_form_pinyin": drug.get('dosage_form_pinyin', ''),
                "dosage_form_initials": drug.get('dosage_form_initials', ''),
                "purchase_type": drug.get('purchase_type', '常规供应')
            }
            new_drugs.append(new_drug)
            new_id += 1
    
    return new_drugs

def save_drugs(drugs):
    """保存药品数据"""
    content = f"""// 药品数据文件
// 生成时间: 2026-03-19
// 药品数量: {len(drugs)}

const DRUGS_DATA = {json.dumps(drugs, ensure_ascii=False, indent=2)};
"""
    with open(DRUGS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("=" * 60)
    print("转换药品数据架构")
    print("=" * 60)
    
    # 加载原始数据
    drugs = load_drugs()
    print(f"原始数据: {len(drugs)} 个合并条目")
    
    # 计算原始总规格数
    total_specs = sum(len(d.get('specifications', [])) for d in drugs)
    print(f"原始规格数: {total_specs} 个")
    
    # 转换为独立条目
    new_drugs = convert_to_separate_entries(drugs)
    print(f"转换后: {len(new_drugs)} 个独立条目")
    
    # 保存新数据
    save_drugs(new_drugs)
    print(f"\n✅ 数据已保存到: {DRUGS_FILE}")
    
    # 显示示例
    print("\n示例条目:")
    for i, drug in enumerate(new_drugs[:3]):
        spec = drug['specifications'][0]
        print(f"  {i+1}. {drug['name']} - {spec['specification']} ({spec['manufacturer']})")

if __name__ == '__main__':
    main()
