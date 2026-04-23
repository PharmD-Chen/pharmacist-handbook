#!/usr/bin/env python3
"""
分析药品手册数据，统计有手册信息的药品
"""

import json
import re

def load_drugs():
    """加载药品数据"""
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

def analyze_manuals(drugs):
    """分析手册信息"""
    total_drugs = len(drugs)
    drugs_with_manual = 0
    drugs_without_manual = 0
    field_stats = {}
    
    for drug in drugs:
        manual = drug.get('manual', {})
        if manual and any(manual.values()):
            drugs_with_manual += 1
            
            # 统计每个字段的存在情况
            for key in manual.keys():
                if not key.startswith('full_'):  # 不统计full_字段
                    if key not in field_stats:
                        field_stats[key] = 0
                    field_stats[key] += 1
        else:
            drugs_without_manual += 1
    
    return {
        'total': total_drugs,
        'with_manual': drugs_with_manual,
        'without_manual': drugs_without_manual,
        'field_stats': field_stats
    }

def main():
    print("=" * 60)
    print("药品手册数据分析")
    print("=" * 60)
    
    drugs = load_drugs()
    stats = analyze_manuals(drugs)
    
    print(f"\n药品总数: {stats['total']}")
    print(f"有手册信息: {stats['with_manual']} ({stats['with_manual']/stats['total']*100:.1f}%)")
    print(f"无手册信息: {stats['without_manual']} ({stats['without_manual']/stats['total']*100:.1f}%)")
    
    print("\n手册字段统计:")
    for field, count in sorted(stats['field_stats'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {field}: {count} 个药品")
    
    # 列出一些有手册的药品示例
    print("\n有手册信息的药品示例（前20个）:")
    count = 0
    for drug in drugs:
        manual = drug.get('manual', {})
        if manual and any(manual.values()):
            count += 1
            print(f"  {count}. {drug['name']}")
            if count >= 20:
                break

if __name__ == '__main__':
    main()
