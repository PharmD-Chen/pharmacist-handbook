#!/usr/bin/env python3
"""检查药品网址汇总文件中的重复药品名称"""

import re
from collections import defaultdict

def extract_drug_names(content):
    """从Markdown内容中提取药品名称"""
    drug_names = []
    
    # 匹配列表格式: `- 药品名 https://...`
    list_pattern = r'^-\s*([^\n]+?)\s+https://www\.hnysfww\.com'
    list_matches = re.findall(list_pattern, content, re.MULTILINE)
    for name in list_matches:
        # 清理名称
        clean_name = re.sub(r'^[※▲]+', '', name).strip()
        if clean_name:
            drug_names.append(clean_name)
    
    # 匹配表格格式: `| 序号 | 药品名 | 剂型 | 规格 | ... |`
    table_pattern = r'\|\s*\d+\s*\|\s*([^|]+?)\s*\|'
    table_matches = re.findall(table_pattern, content)
    for name in table_matches:
        # 清理名称
        clean_name = re.sub(r'^[※▲]+', '', name).strip()
        if clean_name and clean_name not in ['药品名称', '药品名']:
            drug_names.append(clean_name)
    
    return drug_names

def find_duplicates(drug_names):
    """查找重复的药品名称"""
    name_counts = defaultdict(list)
    
    for idx, name in enumerate(drug_names):
        # 标准化名称用于比较（去除空格、统一大小写）
        normalized = re.sub(r'\s+', '', name).lower()
        name_counts[normalized].append((idx, name))
    
    duplicates = {k: v for k, v in name_counts.items() if len(v) > 1}
    return duplicates

def main():
    input_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 60)
    print("药品网址汇总 - 重复检查报告")
    print("=" * 60)
    
    # 提取药品名称
    drug_names = extract_drug_names(content)
    print(f"\n📊 共找到 {len(drug_names)} 个药品名称")
    
    # 查找重复
    duplicates = find_duplicates(drug_names)
    
    if duplicates:
        print(f"\n⚠️  发现 {len(duplicates)} 个重复药品名称：")
        print("-" * 60)
        
        for normalized, occurrences in sorted(duplicates.items()):
            print(f"\n🔴 重复药品: {occurrences[0][1]}")
            print(f"   出现次数: {len(occurrences)} 次")
            for idx, (pos, original_name) in enumerate(occurrences, 1):
                print(f"   第{idx}次: {original_name}")
    else:
        print("\n✅ 未发现重复药品名称")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总药品数: {len(drug_names)}")
    unique_count = len(set(re.sub(r'\s+', '', n).lower() for n in drug_names))
    print(f"唯一药品数: {unique_count}")
    print(f"重复组数: {len(duplicates)}")
    if duplicates:
        total_duplicates = sum(len(v) for v in duplicates.values())
        print(f"重复总次数: {total_duplicates}")

if __name__ == '__main__':
    main()
