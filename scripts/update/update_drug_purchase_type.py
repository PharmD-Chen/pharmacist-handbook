#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新药品数据，添加采购类型信息（常规供应/临时采购）
"""

import json
import re
import pandas as pd
from pathlib import Path

EXCEL_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/药品目录 20260318.xlsx")
DRUGS_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js")

def load_drugs():
    """加载药品数据"""
    with open(DRUGS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    return []

def save_drugs(drugs):
    """保存药品数据"""
    content = f"""// 药品数据文件
// 生成时间: 2026-03-19
// 药品数量: {len(drugs)}

const DRUGS_DATA = {json.dumps(drugs, ensure_ascii=False, indent=2)};
"""
    with open(DRUGS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def read_temp_purchase_info():
    """读取Excel文件，获取临时采购信息"""
    df = pd.read_excel(EXCEL_FILE, header=1)
    
    # 药品通用名在第1列（索引1）
    name_col = df.columns[1]
    # 是否临时采购在第10列（索引10）
    temp_col = df.columns[10]
    
    temp_purchase_dict = {}
    
    for idx, row in df.iterrows():
        drug_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
        is_temp = str(row[temp_col]).strip() if pd.notna(row[temp_col]) else ""
        
        if drug_name and drug_name != "nan":
            temp_purchase_dict[drug_name] = (is_temp == "是")
    
    return temp_purchase_dict

def update_drugs():
    """更新药品数据"""
    # 读取临时采购信息
    temp_purchase_dict = read_temp_purchase_info()
    print(f"从Excel读取到 {len(temp_purchase_dict)} 个药品信息")
    print(f"其中临时采购: {sum(1 for v in temp_purchase_dict.values() if v)} 个")
    
    # 加载药品数据
    drugs = load_drugs()
    print(f"\n当前数据库有 {len(drugs)} 个药品")
    
    # 更新每个药品的采购类型
    updated_count = 0
    not_found_count = 0
    
    for drug in drugs:
        name = drug.get('name', '')
        chemical_name = drug.get('chemical_name', '')
        full_name = drug.get('full_name', '')
        
        # 尝试匹配药品名称
        purchase_type = None
        
        # 先尝试通用名匹配
        if name in temp_purchase_dict:
            purchase_type = "临时采购" if temp_purchase_dict[name] else "常规供应"
        # 再尝试化学名匹配
        elif chemical_name in temp_purchase_dict:
            purchase_type = "临时采购" if temp_purchase_dict[chemical_name] else "常规供应"
        # 最后尝试完整名称匹配（去掉括号内容）
        else:
            # 清理名称，去掉医保标记等
            clean_name = re.sub(r'[※▲\(\)（）甲乙0-9%]+', '', name).strip()
            if clean_name in temp_purchase_dict:
                purchase_type = "临时采购" if temp_purchase_dict[clean_name] else "常规供应"
        
        if purchase_type:
            drug['purchase_type'] = purchase_type
            updated_count += 1
        else:
            # 默认设置为常规供应
            drug['purchase_type'] = "常规供应"
            not_found_count += 1
    
    print(f"\n更新完成:")
    print(f"  成功匹配: {updated_count} 个")
    print(f"  未匹配到（默认常规供应）: {not_found_count} 个")
    
    # 统计
    temp_count = sum(1 for d in drugs if d.get('purchase_type') == "临时采购")
    normal_count = sum(1 for d in drugs if d.get('purchase_type') == "常规供应")
    print(f"\n统计:")
    print(f"  常规供应: {normal_count} 个")
    print(f"  临时采购: {temp_count} 个")
    
    # 保存数据
    save_drugs(drugs)
    print(f"\n✅ 数据已保存到: {DRUGS_FILE}")

if __name__ == '__main__':
    update_drugs()
