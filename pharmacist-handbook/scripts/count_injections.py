#!/usr/bin/env python3
"""
统计已有详细信息的药品中注射剂型的数量
"""

import json
import re

def load_drugs():
    """加载药品数据"""
    with open('data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取JSON数组
    start = content.find('[')
    end = content.rfind(']')
    if start == -1 or end == -1:
        print("错误: 无法找到JSON数据")
        return []
    
    return json.loads(content[start:end+1])

def is_injection(dosage_form):
    """判断是否为注射剂型"""
    injection_keywords = ['注射', '输液', '滴注', '静脉', '肌内', '皮下', '针剂']
    return any(keyword in dosage_form for keyword in injection_keywords)

def main():
    drugs = load_drugs()
    
    # 筛选已有详细信息的药品
    drugs_with_manual = [d for d in drugs if d.get('manual') and d['manual'].get('source')]
    
    # 统计注射剂型
    injection_drugs = []
    for drug in drugs_with_manual:
        dosage_form = drug.get('dosage_form', '')
        if is_injection(dosage_form):
            injection_drugs.append({
                'name': drug['name'],
                'dosage_form': dosage_form,
                'source': drug['manual'].get('source', '')
            })
    
    # 按剂型分类统计
    dosage_form_count = {}
    for drug in injection_drugs:
        form = drug['dosage_form']
        if form not in dosage_form_count:
            dosage_form_count[form] = 0
        dosage_form_count[form] += 1
    
    print('='*70)
    print('📊 注射剂型药品统计')
    print('='*70)
    print(f'已有详细信息的药品总数: {len(drugs_with_manual)} 个')
    print(f'注射剂型药品数量: {len(injection_drugs)} 个')
    print(f'注射剂型占比: {len(injection_drugs)/len(drugs_with_manual)*100:.2f}%')
    
    print('\n' + '='*70)
    print('📋 按剂型分类统计')
    print('='*70)
    for form, count in sorted(dosage_form_count.items(), key=lambda x: x[1], reverse=True):
        print(f'{form}: {count} 个')
    
    print('\n' + '='*70)
    print('💉 注射剂型药品列表（前30个）')
    print('='*70)
    for i, drug in enumerate(injection_drugs[:30], 1):
        print(f'{i}. {drug["name"]} {drug["dosage_form"]}')
    
    if len(injection_drugs) > 30:
        print(f'\n... 还有 {len(injection_drugs) - 30} 个注射剂型药品')
    
    print('='*70)

if __name__ == '__main__':
    main()
