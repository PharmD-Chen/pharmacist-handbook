#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查有网址但详细内容空缺的药品
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"
MISSING_LIST_FILE = BASE_DIR / "缺少详细信息的药品列表.md"
OUTPUT_FILE = BASE_DIR / "有网址但内容空缺的药品列表.md"

def parse_drug_line(line):
    """解析药品列表行，提取药品信息"""
    pattern = r'-\s*(.+?)\s*\((.+?)\)\s*\[ID:\s*(\d+)\]\s*(https://www\.hnysfww\.com/goods\.php\?id=\d+)?'
    match = re.match(pattern, line.strip())
    
    if match:
        return {
            'name': match.group(1).strip(),
            'spec': match.group(2).strip(),
            'id': int(match.group(3)),
            'url': match.group(4) if match.group(4) else None
        }
    return None

def read_all_drugs_with_url():
    """读取所有有网址的药品"""
    drugs = []
    
    with open(MISSING_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith('-'):
            drug_info = parse_drug_line(line)
            if drug_info and drug_info['url']:
                drugs.append(drug_info)
    
    return drugs

def check_manual_empty(drug_id):
    """检查药品的manual字段是否为空"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        return None, "文件不存在"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 检查是否有manual字段
        if 'manual' not in drug_data:
            return drug_data, "无manual字段"
        
        manual = drug_data['manual']
        
        # 检查关键字段是否为空
        empty_fields = []
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                      'interactions', 'precautions']
        
        for field in key_fields:
            if field not in manual or not manual[field]:
                empty_fields.append(field)
        
        if empty_fields:
            return drug_data, f"空缺字段: {', '.join(empty_fields)}"
        
        return drug_data, None
        
    except Exception as e:
        return None, f"读取错误: {e}"

def main():
    print("=" * 70)
    print("检查有网址但详细内容空缺的药品")
    print("=" * 70)
    
    # 1. 读取所有有网址的药品
    print("\n📋 步骤1: 读取所有有网址的药品...")
    drugs_with_url = read_all_drugs_with_url()
    print(f"   找到 {len(drugs_with_url)} 个有网址的药品")
    
    # 2. 检查每个药品的manual字段
    print("\n🔍 步骤2: 检查药品详细内容...")
    empty_manual_drugs = []
    checked = 0
    
    for drug in drugs_with_url:
        drug_data, error = check_manual_empty(drug['id'])
        checked += 1
        
        if error:
            empty_manual_drugs.append({
                'id': drug['id'],
                'name': drug['name'],
                'spec': drug['spec'],
                'url': drug['url'],
                'error': error
            })
            print(f"   ⚠️  [{drug['id']}] {drug['name']}: {error}")
        
        if checked % 50 == 0:
            print(f"   已检查 {checked}/{len(drugs_with_url)} 个药品...")
    
    # 3. 生成报告
    print(f"\n📊 检查结果:")
    print(f"   - 总药品数: {len(drugs_with_url)}")
    print(f"   - 内容完整: {len(drugs_with_url) - len(empty_manual_drugs)}")
    print(f"   - 内容空缺: {len(empty_manual_drugs)}")
    
    # 4. 输出到文件
    if empty_manual_drugs:
        print(f"\n📝 步骤3: 生成空缺药品列表...")
        
        content = f"""# 有网址但详细内容空缺的药品列表

> 本文档列出所有已有湖南药事服务网网址但详细手册内容空缺的药品
> 
> 生成日期: {datetime.now().strftime('%Y-%m-%d')}
> 空缺药品数: {len(empty_manual_drugs)}

---

## 📋 药品列表

| 序号 | 药品名称 | 规格 | ID | 网址 | 空缺内容 |
|------|----------|------|----|------|----------|
"""
        
        for idx, drug in enumerate(empty_manual_drugs, 1):
            content += f"| {idx} | {drug['name']} | {drug['spec']} | {drug['id']} | [链接]({drug['url']}) | {drug['error']} |\n"
        
        content += f"""

---

## 📊 统计信息

- **总药品数**: {len(drugs_with_url)}
- **内容完整**: {len(drugs_with_url) - len(empty_manual_drugs)}
- **内容空缺**: {len(empty_manual_drugs)}
- **完成率**: {((len(drugs_with_url) - len(empty_manual_drugs)) / len(drugs_with_url) * 100):.1f}%

---

## 🔧 下一步操作

这些药品需要从湖南药事服务网获取详细说明书信息并补充到JSON文件中。
"""
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ 已生成报告: {OUTPUT_FILE}")
    
    print("\n" + "=" * 70)
    print("检查完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
