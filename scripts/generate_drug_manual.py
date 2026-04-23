#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成精简版和详细版药品手册内容，并更新到数据源
"""

import json
import re

def simplify_indications(text):
    """精简适应症"""
    if not text:
        return ""
    # 去除多余空格，保留关键信息
    text = re.sub(r'\s+', ' ', text)
    # 如果超过200字，截取前200字
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def simplify_dosage(text, dosage_form):
    """精简用法用量，根据剂型筛选"""
    if not text:
        return ""
    
    # 清理文本
    text = re.sub(r'\s+', ' ', text)
    
    # 根据剂型筛选相关内容
    lines = text.split('。')
    relevant_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 根据剂型判断相关性
        if '注射' in dosage_form or '注射' in line:
            if any(kw in line for kw in ['静脉', '肌内', '皮下', '注射', '滴注', '静滴']):
                relevant_lines.append(line)
        elif '片' in dosage_form or '胶囊' in dosage_form or '颗粒' in dosage_form:
            if any(kw in line for kw in ['口服', '吞服', '含服', '餐前', '餐后', '每日']):
                relevant_lines.append(line)
        elif '吸入' in dosage_form:
            if any(kw in line for kw in ['吸入', '喷', '揿']):
                relevant_lines.append(line)
        elif '滴眼' in dosage_form or '眼用' in dosage_form:
            if any(kw in line for kw in ['滴眼', '滴于', '眼部']):
                relevant_lines.append(line)
        else:
            relevant_lines.append(line)
    
    # 如果没有筛选到相关内容，返回原文的前200字
    if not relevant_lines:
        return text[:197] + "..." if len(text) > 200 else text
    
    result = '。'.join(relevant_lines[:3])  # 最多保留3条
    if len(result) > 200:
        result = result[:197] + "..."
    return result

def simplify_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    # 提取关键禁忌信息
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def simplify_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def extract_pharmacokinetics(text):
    """提取药代动力学关键参数"""
    if not text:
        return ""
    
    # 提取关键参数
    params = []
    
    # 达峰时间
    match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', text)
    if match:
        params.append(f"Tmax: {match.group(1)}h")
    
    # 半衰期
    match = re.search(r'半衰期.*?([\d\.]+)\s*小时?', text)
    if match:
        params.append(f"t1/2: {match.group(1)}h")
    
    # 蛋白结合率
    match = re.search(r'蛋白结合率.*?([\d\.]+)%', text)
    if match:
        params.append(f"蛋白结合率: {match.group(1)}%")
    
    # 生物利用度
    match = re.search(r'生物利用度.*?([\d\.]+)%', text)
    if match:
        params.append(f"生物利用度: {match.group(1)}%")
    
    if params:
        return "；".join(params)
    
    # 如果没有提取到参数，返回精简后的原文
    text = re.sub(r'\s+', ' ', text)
    return text[:150] + "..." if len(text) > 150 else text

def generate_drug_manual(drug_info, dosage_form):
    """生成药品手册内容"""
    manual = {
        # 精简版
        "indications": simplify_indications(drug_info.get('indications', '')),
        "dosage": simplify_dosage(drug_info.get('dosage', ''), dosage_form),
        "contraindications": simplify_contraindications(drug_info.get('contraindications', '')),
        "adverse_reactions": simplify_adverse_reactions(drug_info.get('adverse_reactions', '')),
        "interactions": drug_info.get('interactions', '')[:150] if drug_info.get('interactions') else "",
        "precautions": drug_info.get('precautions', '')[:150] if drug_info.get('precautions') else "",
        "pregnancy_category": drug_info.get('pregnancy_category', ''),
        "pharmacokinetics": extract_pharmacokinetics(drug_info.get('pharmacokinetics', '')),
        
        # 详细版
        "full_indications": drug_info.get('indications', ''),
        "full_dosage": drug_info.get('dosage', ''),
        "full_contraindications": drug_info.get('contraindications', ''),
        "full_adverse_reactions": drug_info.get('adverse_reactions', ''),
        "full_interactions": drug_info.get('interactions', ''),
        "full_precautions": drug_info.get('precautions', ''),
        "full_pharmacokinetics": drug_info.get('pharmacokinetics', ''),
        
        "source": "湖南药事服务网"
    }
    
    return manual

def main():
    # 读取提取结果
    with open('原始材料/新药品信息提取结果.json', 'r', encoding='utf-8') as f:
        extraction_results = json.load(f)
    
    # 读取Excel获取剂型和规格信息
    import pandas as pd
    excel_path = '原始材料/2026年第一次药事会过会药品信息.xlsx'
    df = pd.read_excel(excel_path, sheet_name='新药信息总表', header=2)
    df = df.dropna(subset=[df.columns[0]])
    
    # 重命名列
    column_mapping = {
        '松江区公立医疗机构新药信息总表': '序号',
        'Unnamed: 1': '通用名',
        'Unnamed: 2': '规格',
        'Unnamed: 3': '剂型',
        'Unnamed: 4': '药理作用与适应症',
        'Unnamed: 5': '生产企业',
        'Unnamed: 6': '单价（元）',
        'Unnamed: 7': '医保类型',
        'Unnamed: 8': '基药类别',
        'Unnamed: 9': '备注'
    }
    df = df.rename(columns=column_mapping)
    
    # 创建药品信息字典
    drug_info_dict = {}
    for _, row in df.iterrows():
        drug_name = str(row['通用名']) if pd.notna(row['通用名']) else ''
        if drug_name and drug_name != 'nan':
            drug_info_dict[drug_name] = {
                '规格': row['规格'],
                '剂型': row['剂型'],
                '生产企业': row['生产企业']
            }
    
    # 生成药品手册内容
    new_drugs = []
    for result in extraction_results:
        if not result['提取成功']:
            continue
        
        drug_name = result['通用名']
        drug_data = result['data']
        
        # 获取剂型和规格
        info = drug_info_dict.get(drug_name, {})
        dosage_form = info.get('剂型', '')
        specification = info.get('规格', '')
        manufacturer = info.get('生产企业', '')
        
        # 生成手册内容
        manual = generate_drug_manual(drug_data, dosage_form)
        
        # 构建药品数据结构
        drug_entry = {
            "id": None,  # 稍后分配
            "name": drug_name,
            "full_name": drug_name,
            "chemical_name": drug_name,
            "dosage_form": dosage_form,
            "types": [],
            "manufacturers": [manufacturer] if manufacturer else [],
            "specifications": [{
                "specification": specification,
                "manufacturer": manufacturer
            }] if specification and manufacturer else [],
            "pinyin": "",
            "pinyin_initials": "",
            "dosage_form_pinyin": "",
            "dosage_form_initials": "",
            "manual": manual,
            "url": {
                "hnysfww": result['url'],
                "last_updated": "2026-03-24"
            }
        }
        
        new_drugs.append(drug_entry)
        
        print(f"✓ 已生成 {drug_name} 的药品手册")
        print(f"  - 精简版适应症: {len(manual['indications'])}字")
        print(f"  - 精简版用法用量: {len(manual['dosage'])}字")
    
    # 保存新药品数据
    output_file = '原始材料/新药品手册数据.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_drugs, f, ensure_ascii=False, indent=2)
    
    print(f"\n已生成 {len(new_drugs)} 个新药品的手册数据")
    print(f"保存到: {output_file}")
    
    return new_drugs

if __name__ == '__main__':
    main()
