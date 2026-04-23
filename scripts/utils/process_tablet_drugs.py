#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理片剂药品详细信息
从湖南药事服务网获取信息并更新药品JSON文件
"""

import os
import re
import json
import time
from pathlib import Path
from datetime import datetime

# 路径配置
BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"
MISSING_LIST_FILE = BASE_DIR / "缺少详细信息的药品列表.md"
SUMMARY_FILE = BASE_DIR / "药品网址汇总.md"

def parse_drug_line(line):
    """解析药品列表行，提取药品信息"""
    # 匹配格式: - 药品名 (规格) [ID: xxx] https://www.hnysfww.com/goods.php?id=xxx
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
    """读取片剂药品列表（第16-220行）"""
    drugs = []
    
    with open(MISSING_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 第16-220行（索引15-219）
    for i in range(15, min(220, len(lines))):
        line = lines[i].strip()
        if line.startswith('-'):
            drug_info = parse_drug_line(line)
            if drug_info and drug_info['url']:
                drugs.append(drug_info)
    
    return drugs

def update_drug_info(drug_id, drug_name, url):
    """更新药品信息到JSON文件"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    if not json_path.exists():
        print(f"  ⚠️ 药品文件不存在: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 更新网址信息
        if 'url' not in drug_data:
            drug_data['url'] = {}
        
        drug_data['url']['hnysfww'] = url
        drug_data['url']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # 确保manual字段存在
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        # 标记为已补充网址
        drug_data['manual']['url_added'] = True
        drug_data['manual']['source'] = '湖南药事服务网'
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 更新失败: {e}")
        return False

def update_summary_md(drugs):
    """更新药品网址汇总.md文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 读取现有内容
    if SUMMARY_FILE.exists():
        with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# 药品手册网址汇总\n\n> 本文档汇总了所有药品的湖南药事服务网网址信息\n> \n> 最后更新：\n\n"
    
    # 更新最后更新时间
    content = re.sub(
        r'最后更新：\d{4}-\d{2}-\d{2}',
        f'最后更新：{today}',
        content
    )
    
    # 查找"已补充完整手册的药品"表格
    # 在表格后添加新的药品条目
    table_pattern = r'(## 一、已补充完整手册的药品.*?\n\| 序号 \| 药品名称 \| 网址 \| 补充日期 \| 备注 \|\n\|[-| ]+\|)'
    
    # 准备新条目
    new_entries = []
    existing_drugs = set()
    
    # 提取已有药品名称
    existing_pattern = r'\|\s*\d+\s*\|\s*([^|]+)\s*\|'
    for match in re.finditer(existing_pattern, content):
        existing_drugs.add(match.group(1).strip())
    
    # 添加新药品
    seq = len(existing_drugs) + 1
    for drug in drugs:
        drug_name = drug['name']
        if drug_name not in existing_drugs:
            url = drug['url']
            new_entries.append(f"| {seq} | {drug_name} | {url} | {today} | 片剂 |")
            seq += 1
    
    if new_entries:
        # 找到表格末尾并插入新条目
        lines = content.split('\n')
        insert_idx = -1
        for i, line in enumerate(lines):
            if '| 序号 | 药品名称 | 网址 | 补充日期 | 备注 |' in line:
                # 找到表头后的分隔行
                for j in range(i+1, len(lines)):
                    if '|' in lines[j] and '---' in lines[j]:
                        insert_idx = j
                        break
                break
        
        if insert_idx > 0:
            # 在分隔行后插入新条目
            lines = lines[:insert_idx+1] + new_entries + lines[insert_idx+1:]
            content = '\n'.join(lines)
    
    # 写入文件
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(new_entries)

def main():
    """主函数"""
    print("=" * 60)
    print("处理片剂药品详细信息")
    print("=" * 60)
    
    # 1. 读取片剂药品列表
    print("\n📋 步骤1: 读取片剂药品列表...")
    drugs = read_tablet_drugs()
    print(f"   找到 {len(drugs)} 个有网址的片剂药品")
    
    # 2. 更新药品JSON文件
    print("\n💾 步骤2: 更新药品JSON文件...")
    updated = 0
    failed = 0
    
    for drug in drugs:
        print(f"   处理: {drug['name']} [ID: {drug['id']}]")
        if update_drug_info(drug['id'], drug['name'], drug['url']):
            updated += 1
        else:
            failed += 1
        time.sleep(0.1)  # 避免过快
    
    print(f"   ✅ 成功更新: {updated} 个")
    if failed > 0:
        print(f"   ⚠️ 失败: {failed} 个")
    
    # 3. 更新汇总文档
    print("\n📝 步骤3: 更新药品网址汇总.md...")
    added = update_summary_md(drugs)
    print(f"   ✅ 新增 {added} 条记录到汇总文档")
    
    print("\n" + "=" * 60)
    print("处理完成！")
    print(f"- 药品总数: {len(drugs)}")
    print(f"- 更新成功: {updated}")
    print(f"- 汇总新增: {added}")
    print("=" * 60)

if __name__ == '__main__':
    main()
