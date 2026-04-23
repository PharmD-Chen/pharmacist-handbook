#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import re

# 1. 读取Excel药品目录
df = pd.read_excel('原始材料/药品目录 20260318.xlsx')
excel_drugs = {}
for _, row in df.iterrows():
    name = str(row['药品名称']).strip() if pd.notna(row['药品名称']) else ''
    chemical = str(row['药品化学名']).strip() if pd.notna(row['药品化学名']) else ''
    
    # 提取剂型
    dosage = '其他'
    if '注射液' in chemical: dosage = '注射液'
    elif '片' in chemical: dosage = '片'
    elif '胶囊' in chemical: dosage = '胶囊'
    elif '颗粒' in chemical: dosage = '颗粒'
    elif '喷雾' in chemical: dosage = '喷雾剂'
    elif '软膏' in chemical: dosage = '软膏'
    elif '滴眼' in chemical: dosage = '滴眼液'
    elif '滴耳' in chemical: dosage = '滴耳液'
    elif '滴鼻' in chemical: dosage = '滴鼻液'
    elif '栓' in chemical: dosage = '栓剂'
    elif '贴' in chemical: dosage = '贴剂'
    elif '凝胶' in chemical: dosage = '凝胶'
    elif '散' in chemical: dosage = '散剂'
    elif '丸' in chemical: dosage = '丸'
    elif '糖浆' in chemical: dosage = '糖浆'
    elif '口服' in chemical: dosage = '口服液'
    elif '混悬' in chemical: dosage = '混悬液'
    elif '乳膏' in chemical: dosage = '乳膏'
    elif '吸入' in chemical: dosage = '吸入剂'
    elif '注射用' in chemical: dosage = '注射用'
    elif '溶液' in chemical: dosage = '溶液'
    elif '其他' in chemical or '酊' in chemical: dosage = '其他'
    
    # 清理Excel中的名称（移除医保标记）
    clean_name = re.sub(r'\([^)]*\)', '', name)
    clean_name = clean_name.replace('※', '').replace('▲', '').strip()
    
    key = f"{clean_name}|{dosage}"
    if key not in excel_drugs:
        excel_drugs[key] = {'name': clean_name, 'dosage': dosage, 'chemical': chemical, 'original': name}

# 2. 读取已完成药品（从drugs.js中提取）
with open('pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
    content = f.read()

names = re.findall(r'"name":\s*"([^"]+)"', content)
dosages = re.findall(r'"dosage_form":\s*"([^"]+)"', content)

completed = set()
for name, dosage in zip(names, dosages):
    clean_name = name.replace('※', '').replace('▲', '').strip()
    key = f"{clean_name}|{dosage}"
    completed.add(key)

# 3. 读取drugs_without_manual.txt
without_manual = {}
with open('pharmacist-handbook/data/drugs_without_manual.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('=') or line.startswith('没有'):
            continue
        match = re.match(r'\d+\.\s+(.+?)\s+\|\s+(.+?)\s+\|\s+(.+)', line)
        if match:
            name = match.group(1).strip()
            dosage = match.group(2).strip()
            full_info = match.group(3).strip()
            url_match = re.search(r'https?://\S+', full_info)
            url = url_match.group(0) if url_match else ''
            clean_name = name.replace('※', '').replace('▲', '').strip()
            key = f"{clean_name}|{dosage}"
            without_manual[key] = {'name': name, 'dosage': dosage, 'url': url}

# 4. 分析结果
print("=" * 70)
print("药品梳理报告")
print("=" * 70)
print(f"\n1. Excel原始目录药品总数: {len(excel_drugs)} 个（按通用名+剂型去重）")
print(f"2. 数据库中已有药品数: {len(completed)} 个")
print(f"3. 暂无详细信息的药品数: {len(without_manual)} 个")

# 5. 找出Excel中有但数据库中没有的药品
missing_in_db = []
for key, info in excel_drugs.items():
    if key not in completed:
        missing_in_db.append((key, info))

print(f"\n4. Excel中有但数据库中缺失的药品: {len(missing_in_db)} 个")

# 6. 找出没有网址的药品
no_url = []
for key, info in without_manual.items():
    if not info['url']:
        no_url.append((key, info))

print(f"5. 在without_manual中但没有网址的药品: {len(no_url)} 个")

# 7. 找出在Excel中且在没有详细信息列表中但没有网址的药品
need_url = []
for key in excel_drugs:
    if key in without_manual and not without_manual[key]['url']:
        need_url.append((key, excel_drugs[key], without_manual[key]))

print(f"6. Excel中有、在without_manual中、但没有网址的药品: {len(need_url)} 个")

# 8. 保存详细报告
with open('drug_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("药品梳理详细报告\n")
    f.write("=" * 70 + "\n\n")
    
    f.write(f"1. Excel原始目录药品总数: {len(excel_drugs)} 个\n")
    f.write(f"2. 数据库中已有药品数: {len(completed)} 个\n")
    f.write(f"3. 暂无详细信息的药品数: {len(without_manual)} 个\n")
    f.write(f"4. Excel中有但数据库中缺失的药品: {len(missing_in_db)} 个\n")
    f.write(f"5. 在without_manual中但没有网址的药品: {len(no_url)} 个\n")
    f.write(f"6. Excel中有、在without_manual中、但没有网址的药品: {len(need_url)} 个\n\n")
    
    f.write("=" * 70 + "\n")
    f.write("需要添加网址的药品（按通用名+剂型）:\n")
    f.write("=" * 70 + "\n")
    for i, (key, excel_info, wm_info) in enumerate(sorted(need_url), 1):
        f.write(f"{i}. {wm_info['name']} | {wm_info['dosage']} | {excel_info['chemical']}\n")

print("\n详细报告已保存到: drug_analysis_report.txt")
print(f"\n需要添加网址的药品共 {len(need_url)} 个")
print("\n前30个需要添加网址的药品:")
for i, (key, excel_info, wm_info) in enumerate(sorted(need_url)[:30], 1):
    print(f"{i}. {wm_info['name']} | {wm_info['dosage']}")
