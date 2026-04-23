#!/usr/bin/env python3
"""检查Excel文件的所有sheet"""

import pandas as pd

def main():
    excel_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/住院药房 货位号.xlsx'
    
    # 读取所有sheet
    xls = pd.ExcelFile(excel_path)
    
    print(f"Excel文件: {excel_path}")
    print(f"\n包含 {len(xls.sheet_names)} 个sheet:")
    
    for i, sheet_name in enumerate(xls.sheet_names, 1):
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        print(f"\n{i}. Sheet名称: {sheet_name}")
        print(f"   行数: {len(df)}")
        print(f"   列名: {list(df.columns)}")
        print(f"   前3行:")
        print(df.head(3).to_string())

if __name__ == '__main__':
    main()
