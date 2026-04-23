#!/usr/bin/env python3
"""生成缺少详细信息的药品列表"""

import json
from collections import defaultdict

def load_drug_index():
    """加载药品索引"""
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_drug_has_manual(drug_id):
    """检查药品是否已有手册数据"""
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug_id}.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug = json.load(f)
        manual = drug.get('manual', {})
        return bool(manual.get('full_indications') or manual.get('full_dosage'))
    except:
        return False

def main():
    print("=" * 60)
    print("生成缺少详细信息的药品列表")
    print("=" * 60)
    
    # 加载药品索引
    drug_index = load_drug_index()
    print(f"\n📊 药品总数: {len(drug_index)}")
    
    # 分类统计
    missing_drugs = []
    has_manual_count = 0
    
    for drug in drug_index:
        if check_drug_has_manual(drug['id']):
            has_manual_count += 1
        else:
            missing_drugs.append(drug)
    
    print(f"✅ 已有详细信息的药品: {has_manual_count}")
    print(f"❌ 缺少详细信息的药品: {len(missing_drugs)}")
    
    # 按剂型分类
    dosage_form_groups = defaultdict(list)
    for drug in missing_drugs:
        dosage_form = drug.get('dosage_form', '其他')
        if not dosage_form:
            dosage_form = '其他'
        dosage_form_groups[dosage_form].append(drug)
    
    # 生成报告
    output_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/缺少详细信息的药品列表.md'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 缺少详细信息的药品列表\n\n")
        f.write("> 本文档列出所有缺少详细说明书信息的药品，需要逐步补充网址并完善信息\n\n")
        f.write(f"- 生成日期: 2026-03-20\n")
        f.write(f"- 药品总数: {len(drug_index)}\n")
        f.write(f"- 缺少信息: {len(missing_drugs)}\n")
        f.write(f"- 已完善: {has_manual_count}\n\n")
        
        f.write("---\n\n")
        f.write("## 📋 按剂型分类\n\n")
        
        # 按剂型数量排序
        sorted_forms = sorted(dosage_form_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        for dosage_form, drugs in sorted_forms:
            f.write(f"### {dosage_form} ({len(drugs)}个)\n\n")
            
            # 按名称排序
            sorted_drugs = sorted(drugs, key=lambda x: x['name'])
            
            for drug in sorted_drugs:
                name = drug['name']
                full_name = drug.get('full_name', '')
                drug_id = drug['id']
                
                # 格式: - 药品名 (完整名称) [ID: xxx]
                if full_name and full_name != name:
                    f.write(f"- {name} ({full_name}) [ID: {drug_id}]\n")
                else:
                    f.write(f"- {name} [ID: {drug_id}]\n")
            
            f.write("\n")
        
        # 添加汇总表格
        f.write("---\n\n")
        f.write("## 📊 剂型统计\n\n")
        f.write("| 剂型 | 数量 | 占比 |\n")
        f.write("|------|------|------|\n")
        
        for dosage_form, drugs in sorted_forms:
            count = len(drugs)
            percentage = count / len(missing_drugs) * 100
            f.write(f"| {dosage_form} | {count} | {percentage:.1f}% |\n")
        
        f.write(f"| **合计** | **{len(missing_drugs)}** | **100%** |\n")
    
    print(f"\n✅ 已生成列表: {output_file}")
    
    # 显示前10个剂型统计
    print("\n📊 剂型统计（前10）:")
    print("-" * 40)
    for i, (dosage_form, drugs) in enumerate(sorted_forms[:10], 1):
        print(f"{i}. {dosage_form}: {len(drugs)}个")

if __name__ == '__main__':
    main()
