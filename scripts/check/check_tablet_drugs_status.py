#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查第16-220行片剂药品的详细内容状态
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"
MISSING_LIST_FILE = BASE_DIR / "缺少详细信息的药品列表.md"

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

def read_tablet_drugs():
    """读取第16-220行的片剂药品"""
    drugs = []
    
    with open(MISSING_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 第16-220行（索引15-219）
    for i in range(15, min(220, len(lines))):
        line = lines[i].strip()
        if line.startswith('-'):
            drug_info = parse_drug_line(line)
            if drug_info:
                drugs.append(drug_info)
    
    return drugs

def check_manual_status(drug_id):
    """检查药品的manual字段状态"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        return "文件不存在"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 检查是否有manual字段
        if 'manual' not in drug_data:
            return "无manual字段"
        
        manual = drug_data['manual']
        
        # 检查关键字段是否为空
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                      'interactions', 'precautions']
        
        empty_fields = []
        for field in key_fields:
            if field not in manual or not manual[field]:
                empty_fields.append(field)
        
        if empty_fields:
            return f"空缺{len(empty_fields)}个字段"
        
        return "完整"
        
    except Exception as e:
        return f"读取错误: {e}"

def main():
    print("=" * 70)
    print("检查第16-220行片剂药品的详细内容状态")
    print("=" * 70)
    
    # 1. 读取片剂药品
    print("\n📋 步骤1: 读取片剂药品列表...")
    drugs = read_tablet_drugs()
    print(f"   找到 {len(drugs)} 个片剂药品")
    
    # 2. 统计有网址和没有网址的药品
    with_url = [d for d in drugs if d['url']]
    without_url = [d for d in drugs if not d['url']]
    
    print(f"\n📊 网址统计:")
    print(f"   - 有网址: {len(with_url)} 个")
    print(f"   - 无网址: {len(without_url)} 个")
    
    # 3. 检查有网址药品的内容状态
    print(f"\n🔍 步骤2: 检查有网址药品的内容状态...")
    
    complete = 0
    incomplete = 0
    empty_manual = []
    
    for drug in with_url:
        status = check_manual_status(drug['id'])
        if status == "完整":
            complete += 1
        else:
            incomplete += 1
            empty_manual.append({
                'id': drug['id'],
                'name': drug['name'],
                'url': drug['url'],
                'status': status
            })
    
    print(f"\n📊 内容状态统计:")
    print(f"   - 内容完整: {complete} 个")
    print(f"   - 内容空缺: {incomplete} 个")
    
    # 4. 显示无网址的药品
    if without_url:
        print(f"\n⚠️ 无网址的药品 ({len(without_url)}个):")
        for drug in without_url:
            print(f"   - [{drug['id']}] {drug['name']}")
    
    # 5. 显示内容空缺的药品（前20个）
    if empty_manual:
        print(f"\n⚠️ 内容空缺的药品 (显示前20个，共{len(empty_manual)}个):")
        for drug in empty_manual[:20]:
            print(f"   - [{drug['id']}] {drug['name']}: {drug['status']}")
        
        if len(empty_manual) > 20:
            print(f"   ... 还有 {len(empty_manual) - 20} 个")
    
    print("\n" + "=" * 70)
    print("检查完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
