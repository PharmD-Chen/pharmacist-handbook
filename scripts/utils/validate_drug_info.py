#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证已导入药品信息的完整性
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook")
DRUGS_FILE = BASE_DIR / "data/drugs.js"

def load_drugs():
    """加载药品数据"""
    with open(DRUGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        # 提取JSON部分
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    return []

def validate_drug(drug):
    """验证单个药品的信息完整性"""
    issues = []
    
    # 基本信息检查
    if not drug.get('name'):
        issues.append("缺少药品名称")
    if not drug.get('dosage_form'):
        issues.append("缺少剂型")
    if not drug.get('pinyin'):
        issues.append("缺少拼音")
    if not drug.get('pinyin_initials'):
        issues.append("缺少拼音首字母")
    
    # 规格信息检查
    specs = drug.get('specifications', [])
    if not specs:
        issues.append("缺少规格信息")
    else:
        for i, spec in enumerate(specs):
            if not spec.get('specification'):
                issues.append(f"规格{i+1}缺少规格描述")
            if not spec.get('manufacturer'):
                issues.append(f"规格{i+1}缺少生产厂家")
    
    # 说明书信息检查
    manual = drug.get('manual', {})
    if manual:
        # 检查关键字段
        key_fields = ['indications', 'contraindications', 'adverse_reactions', 'precautions']
        empty_fields = []
        for field in key_fields:
            if not manual.get(field):
                empty_fields.append(field)
        
        if empty_fields:
            issues.append(f"说明书字段为空: {', '.join(empty_fields)}")
        
        if not manual.get('source'):
            issues.append("说明书缺少来源")
    else:
        issues.append("缺少说明书信息")
    
    return issues

def analyze_data_quality():
    """分析数据质量"""
    drugs = load_drugs()
    
    print("="*70)
    print("📊 药品信息完整性验证报告")
    print("="*70)
    print(f"\n总药品数: {len(drugs)} 个\n")
    
    # 统计各类问题
    drugs_with_manual = 0
    drugs_without_manual = 0
    
    manual_field_stats = defaultdict(int)
    issues_by_type = defaultdict(list)
    
    # 关键字段
    key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                  'interactions', 'pregnancy_category', 'pharmacokinetics', 'precautions']
    
    for drug in drugs:
        drug_id = drug.get('id', 'N/A')
        name = drug.get('name', '未知')
        dosage = drug.get('dosage_form', '未知')
        
        manual = drug.get('manual', {})
        
        if manual and any(manual.values()):
            drugs_with_manual += 1
            
            # 统计各字段填充情况
            for field in key_fields:
                if manual.get(field):
                    manual_field_stats[field] += 1
            
            # 检查是否有空字段
            empty_fields = [f for f in key_fields if not manual.get(f)]
            if empty_fields:
                issues_by_type['部分字段为空'].append({
                    'id': drug_id,
                    'name': name,
                    'dosage': dosage,
                    'empty_fields': empty_fields
                })
        else:
            drugs_without_manual += 1
            issues_by_type['缺少说明书'].append({
                'id': drug_id,
                'name': name,
                'dosage': dosage
            })
    
    # 输出统计
    print("="*70)
    print("✅ 整体统计")
    print("="*70)
    print(f"有说明书的药品: {drugs_with_manual} 个 ({drugs_with_manual/len(drugs)*100:.1f}%)")
    print(f"无说明书的药品: {drugs_without_manual} 个 ({drugs_without_manual/len(drugs)*100:.1f}%)")
    
    print("\n" + "="*70)
    print("📋 说明书字段填充情况")
    print("="*70)
    for field in key_fields:
        count = manual_field_stats[field]
        percentage = count / drugs_with_manual * 100 if drugs_with_manual > 0 else 0
        field_names = {
            'indications': '适应症',
            'dosage': '用法用量',
            'contraindications': '禁忌症',
            'adverse_reactions': '不良反应',
            'interactions': '药物相互作用',
            'pregnancy_category': '妊娠分级',
            'pharmacokinetics': '药代动力学',
            'precautions': '注意事项'
        }
        print(f"  {field_names.get(field, field)}: {count}/{drugs_with_manual} ({percentage:.1f}%)")
    
    print("\n" + "="*70)
    print("⚠️  问题统计")
    print("="*70)
    for issue_type, items in issues_by_type.items():
        print(f"\n{issue_type}: {len(items)} 个药品")
        if issue_type == '部分字段为空':
            # 显示前10个示例
            print("  示例（前10个）:")
            for item in items[:10]:
                empty = ', '.join(item['empty_fields'][:3])
                if len(item['empty_fields']) > 3:
                    empty += f" 等{len(item['empty_fields'])}个字段"
                print(f"    - {item['name']} ({item['dosage']}): 缺 {empty}")
        elif issue_type == '缺少说明书':
            # 显示前20个
            print("  列表（前20个）:")
            for item in items[:20]:
                print(f"    - {item['name']} ({item['dosage']})")
            if len(items) > 20:
                print(f"    ... 还有 {len(items)-20} 个")
    
    # 输出建议
    print("\n" + "="*70)
    print("💡 改进建议")
    print("="*70)
    
    if drugs_without_manual > 0:
        print(f"1. 优先补充 {drugs_without_manual} 个缺少说明书的药品")
    
    # 找出填充率最低的字段
    field_fill_rates = []
    for field in key_fields:
        count = manual_field_stats[field]
        rate = count / drugs_with_manual * 100 if drugs_with_manual > 0 else 0
        field_fill_rates.append((field, rate))
    
    field_fill_rates.sort(key=lambda x: x[1])
    print(f"2. 重点补充以下字段（填充率较低）:")
    for field, rate in field_fill_rates[:3]:
        field_names = {
            'indications': '适应症',
            'dosage': '用法用量',
            'contraindications': '禁忌症',
            'adverse_reactions': '不良反应',
            'interactions': '药物相互作用',
            'pregnancy_category': '妊娠分级',
            'pharmacokinetics': '药代动力学',
            'precautions': '注意事项'
        }
        print(f"   - {field_names.get(field, field)}: 当前填充率 {rate:.1f}%")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    analyze_data_quality()
