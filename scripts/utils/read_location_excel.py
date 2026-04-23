#!/usr/bin/env python3
"""读取住院药房货位号Excel文件"""

import pandas as pd

def main():
    excel_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/住院药房 货位号.xlsx'
    
    print(f"正在读取Excel文件: {excel_path}")
    df = pd.read_excel(excel_path)
    
    print(f"\n✅ 成功读取，共 {len(df)} 行数据")
    print(f"\n列名: {list(df.columns)}")
    
    print("\n前10行数据:")
    print(df.head(10))
    
    print("\n数据示例:")
    for idx, row in df.head(5).iterrows():
        print(f"\n行 {idx + 1}:")
        for col in df.columns:
            print(f"  {col}: {row.get(col, '')}")

if __name__ == '__main__':
    main()
