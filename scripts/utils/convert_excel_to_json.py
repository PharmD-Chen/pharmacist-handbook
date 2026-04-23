#!/usr/bin/env python3
"""将药品目录Excel转换为JSON文件"""

import pandas as pd
import json
import re

def clean_name(name):
    """清理药品名称，去除※▲等特殊标记"""
    if pd.isna(name):
        return ""
    return re.sub(r'^[※▲]+', '', str(name)).strip()

def main():
    excel_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/原始材料/药品目录 20260318.xlsx'
    output_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drug_catalog.json'
    
    print(f"正在读取Excel文件: {excel_path}")
    df = pd.read_excel(excel_path)
    
    print(f"✅ 成功读取，共 {len(df)} 行数据")
    print(f"列名: {list(df.columns)}")
    
    # 查看前几行数据
    print("\n前5行数据:")
    print(df.head())
    
    # 转换数据
    catalog = []
    for idx, row in df.iterrows():
        # 获取临购药品列（K列）
        # Excel中的"临购药品"列，值为"是"表示临时采购，"否"表示常规供应
        purchase_type = "常规供应"  # 默认值
        
        lin_gou = row.get('临购药品', '')
        if pd.notna(lin_gou) and str(lin_gou).strip() == '是':
            purchase_type = "临时采购"
        
        item = {
            'id': idx + 1,
            'name': clean_name(row.get('药品名称', '')),
            'dosage_form': str(row.get('剂型', '')).strip() if pd.notna(row.get('剂型', '')) else '',
            'full_name': str(row.get('药品通用名', '')).strip() if pd.notna(row.get('药品通用名', '')) else '',
            'purchase_type': purchase_type,
            'manufacturers': [str(row.get('生产厂家', '')).strip()] if pd.notna(row.get('生产厂家', '')) else [],
            'specifications': [{
                'specification': str(row.get('规格', '')).strip(),
                'manufacturer': str(row.get('生产厂家', '')).strip() if pd.notna(row.get('生产厂家', '')) else '',
                'price': float(row.get('单价', 0)) if pd.notna(row.get('单价', 0)) else 0,
                'unit': str(row.get('单位', '')).strip() if pd.notna(row.get('单位', '')) else '',
                'code': str(row.get('药品代码', '')).strip() if pd.notna(row.get('药品代码', '')) else '',
                'approval_number': str(row.get('批准文号', '')).strip() if pd.notna(row.get('批准文号', '')) else '',
                'insurance_code': str(row.get('医保编码', '')).strip() if pd.notna(row.get('医保编码', '')) else ''
            }] if pd.notna(row.get('规格', '')) else []
        }
        catalog.append(item)
    
    # 保存为JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存到: {output_path}")
    print(f"共转换 {len(catalog)} 个药品")
    
    # 统计临时采购药品数量
    temp_count = sum(1 for item in catalog if item['purchase_type'] == '临时采购')
    print(f"临时采购药品: {temp_count} 个")
    print(f"常规供应药品: {len(catalog) - temp_count} 个")

if __name__ == '__main__':
    main()
