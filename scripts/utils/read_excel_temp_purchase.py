#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取Excel文件获取临时采购信息
"""

import pandas as pd
from pathlib import Path

EXCEL_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/药品目录 20260318.xlsx")

def read_temp_purchase_info():
    """读取Excel文件，获取临时采购信息"""
    # 读取Excel文件
    df = pd.read_excel(EXCEL_FILE, header=1)  # 从第2行开始读取（标题行）
    
    # 打印列名，查看K列的名称
    print("Excel列名:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    
    # 查找K列（第10列，索引为10）
    # 通常K列是第11列，索引为10
    k_column = df.columns[10] if len(df.columns) > 10 else None
    print(f"\nK列名称: {k_column}")
    
    # 获取药品名称和临时采购信息
    temp_purchase_dict = {}
    
    # 假设药品名称在A列（通用名）
    name_col = df.columns[0]  # A列
    
    if k_column:
        for idx, row in df.iterrows():
            drug_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""
            is_temp = str(row[k_column]).strip() if pd.notna(row[k_column]) else ""
            
            if drug_name and drug_name != "nan":
                # 如果是"是"，则为临时采购
                temp_purchase_dict[drug_name] = (is_temp == "是")
    
    print(f"\n读取到 {len(temp_purchase_dict)} 个药品信息")
    print(f"临时采购药品数量: {sum(1 for v in temp_purchase_dict.values() if v)}")
    
    # 显示前10个示例
    print("\n前10个药品示例:")
    for i, (name, is_temp) in enumerate(list(temp_purchase_dict.items())[:10]):
        status = "临时采购" if is_temp else "常规供应"
        print(f"  {name}: {status}")
    
    return temp_purchase_dict

if __name__ == '__main__':
    read_temp_purchase_info()
