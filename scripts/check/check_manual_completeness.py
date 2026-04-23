#!/usr/bin/env python3
"""
检查药品手册内容的完整性和来源
"""
import json
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'

def check_manual_completeness():
    """检查药品手册内容的完整性"""
    
    # 读取药品索引
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)
    
    # 统计
    total_drugs = len(drugs_index)
    drugs_with_complete_manual = 0
    drugs_with_partial_manual = 0
    drugs_without_manual = 0
    
    # 按来源统计
    source_stats = defaultdict(int)
    
    # 字段统计
    field_stats = {
        'indications': 0,
        'dosage': 0,
        'contraindications': 0,
        'adverse_reactions': 0,
        'interactions': 0,
        'precautions': 0,
        'pharmacokinetics': 0,
        'pregnancy_category': 0
    }
    
    # 记录详细情况
    complete_drugs = []
    partial_drugs = []
    empty_drugs = []
    non_hnysfww_drugs = []
    
    print("=" * 80)
    print("药品手册内容完整性检查报告")
    print("=" * 80)
    print(f"\n总药品数: {total_drugs}")
    
    # 检查每个药品
    for drug in drugs_index:
        drug_id = drug['id']
        drug_name = drug['name']
        
        # 读取药品详情文件
        drug_file = DRUGS_DIR / f'{drug_id}.json'
        
        if not drug_file.exists():
            drugs_without_manual += 1
            empty_drugs.append({'id': drug_id, 'name': drug_name, 'reason': '文件不存在'})
            continue
        
        try:
            with open(drug_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            manual = drug_data.get('manual', {})
            
            # 检查关键字段
            has_content = False
            filled_fields = []
            
            for field in field_stats.keys():
                value = manual.get(field)
                if value and value.strip() and value != 'null' and value != 'None':
                    field_stats[field] += 1
                    filled_fields.append(field)
                    has_content = True
            
            # 检查来源
            source = manual.get('source', '')
            if source:
                source_stats[source] += 1
            
            # 判断完整性
            if len(filled_fields) >= 6:  # 至少有6个关键字段
                drugs_with_complete_manual += 1
                complete_drugs.append({
                    'id': drug_id,
                    'name': drug_name,
                    'fields': filled_fields,
                    'source': source
                })
            elif has_content:
                drugs_with_partial_manual += 1
                partial_drugs.append({
                    'id': drug_id,
                    'name': drug_name,
                    'fields': filled_fields,
                    'source': source
                })
            else:
                drugs_without_manual += 1
                empty_drugs.append({
                    'id': drug_id,
                    'name': drug_name,
                    'reason': '手册内容为空'
                })
            
            # 记录非湖南药事服务网来源
            if source and '湖南药事服务网' not in source:
                non_hnysfww_drugs.append({
                    'id': drug_id,
                    'name': drug_name,
                    'source': source
                })
                
        except Exception as e:
            drugs_without_manual += 1
            empty_drugs.append({
                'id': drug_id,
                'name': drug_name,
                'reason': f'读取错误: {str(e)}'
            })
    
    # 打印统计结果
    print(f"\n【内容完整性统计】")
    print(f"✓ 内容完整 (≥6个字段): {drugs_with_complete_manual} ({drugs_with_complete_manual/total_drugs*100:.1f}%)")
    print(f"△ 内容部分 (1-5个字段): {drugs_with_partial_manual} ({drugs_with_partial_manual/total_drugs*100:.1f}%)")
    print(f"✗ 无内容: {drugs_without_manual} ({drugs_without_manual/total_drugs*100:.1f}%)")
    
    print(f"\n【各字段覆盖情况】")
    for field, count in field_stats.items():
        print(f"  {field:25s}: {count:4d} ({count/total_drugs*100:5.1f}%)")
    
    print(f"\n【数据来源统计】")
    for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source or '未标注':30s}: {count:4d}")
    
    # 打印非湖南药事服务网来源的药品
    if non_hnysfww_drugs:
        print(f"\n【非湖南药事服务网来源的药品】({len(non_hnysfww_drugs)}个)")
        print("-" * 80)
        for drug in non_hnysfww_drugs[:30]:
            print(f"ID {drug['id']:4d}: {drug['name'][:30]:30s} - 来源: {drug['source']}")
        if len(non_hnysfww_drugs) > 30:
            print(f"\n... 还有 {len(non_hnysfww_drugs) - 30} 个")
    
    # 打印部分内容的药品示例
    if partial_drugs:
        print(f"\n【部分内容的药品示例】({len(partial_drugs)}个)")
        print("-" * 80)
        for drug in partial_drugs[:20]:
            print(f"ID {drug['id']:4d}: {drug['name'][:30]:30s} - 字段: {', '.join(drug['fields'])}")
        if len(partial_drugs) > 20:
            print(f"\n... 还有 {len(partial_drugs) - 20} 个")
    
    # 保存报告
    report_file = PROJECT_DIR / 'output' / 'manual_completeness_report.txt'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("药品手册内容完整性检查报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"总药品数: {total_drugs}\n\n")
        
        f.write("【内容完整性统计】\n")
        f.write(f"✓ 内容完整 (≥6个字段): {drugs_with_complete_manual} ({drugs_with_complete_manual/total_drugs*100:.1f}%)\n")
        f.write(f"△ 内容部分 (1-5个字段): {drugs_with_partial_manual} ({drugs_with_partial_manual/total_drugs*100:.1f}%)\n")
        f.write(f"✗ 无内容: {drugs_without_manual} ({drugs_without_manual/total_drugs*100:.1f}%)\n\n")
        
        f.write("【各字段覆盖情况】\n")
        for field, count in field_stats.items():
            f.write(f"  {field:25s}: {count:4d} ({count/total_drugs*100:5.1f}%)\n")
        
        f.write(f"\n【数据来源统计】\n")
        for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {source or '未标注':30s}: {count:4d}\n")
        
        if non_hnysfww_drugs:
            f.write(f"\n【非湖南药事服务网来源的药品】({len(non_hnysfww_drugs)}个)\n")
            f.write("-" * 80 + "\n")
            for drug in non_hnysfww_drugs:
                f.write(f"ID {drug['id']:4d}: {drug['name']} - 来源: {drug['source']}\n")
        
        if partial_drugs:
            f.write(f"\n【部分内容的药品列表】({len(partial_drugs)}个)\n")
            f.write("-" * 80 + "\n")
            for drug in partial_drugs:
                f.write(f"ID {drug['id']:4d}: {drug['name']} - 字段: {', '.join(drug['fields'])}\n")
        
        if empty_drugs:
            f.write(f"\n【无内容的药品列表】({len(empty_drugs)}个)\n")
            f.write("-" * 80 + "\n")
            for drug in empty_drugs:
                f.write(f"ID {drug['id']:4d}: {drug['name']} - {drug['reason']}\n")
    
    print(f"\n✓ 报告已保存: {report_file}")
    
    return {
        'complete': complete_drugs,
        'partial': partial_drugs,
        'empty': empty_drugs,
        'non_hnysfww': non_hnysfww_drugs
    }

if __name__ == '__main__':
    check_manual_completeness()
