#!/usr/bin/env python3
"""整理 pharmacist-handbook/data 文件夹"""

import os
import shutil
from pathlib import Path

def main():
    data_dir = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data')
    backup_dir = data_dir / 'backup'
    
    # 创建备份文件夹
    backup_dir.mkdir(exist_ok=True)
    
    # 需要保留在根目录的核心文件
    core_files = {
        'drug_catalog.json',      # 药品目录（从Excel转换）
        'drugs.js',               # 原始药品数据（备用）
        'drugs_test.js',          # 测试数据
    }
    
    # 需要移动到 backup 的中间文件
    backup_patterns = [
        'common_drugs_batch*.json',
        'common_drugs_part*.json',
        '*_drugs.json',
        '*_drugs_part*.json',
        'drugs_with_info.js',
        'drugs_without_manual.txt',
        'manual_drug_info_template.json',
        'sample_manual.json',
        'drug_info_example.json',
    ]
    
    moved_count = 0
    
    # 移动匹配的文件到 backup
    for pattern in backup_patterns:
        for file_path in data_dir.glob(pattern):
            if file_path.is_file():
                dest = backup_dir / file_path.name
                shutil.move(str(file_path), str(dest))
                print(f"📦 已移动: {file_path.name} -> backup/")
                moved_count += 1
    
    print(f"\n✅ 整理完成！")
    print(f"📦 已移动 {moved_count} 个文件到 backup/")
    
    # 统计剩余文件
    remaining = [f.name for f in data_dir.iterdir() if f.is_file()]
    print(f"📁 根目录保留 {len(remaining)} 个核心文件:")
    for f in sorted(remaining):
        print(f"   - {f}")
    
    # 统计 drugs 文件夹
    drugs_dir = data_dir / 'drugs'
    if drugs_dir.exists():
        drug_files = list(drugs_dir.glob('*.json'))
        print(f"\n💊 drugs/ 文件夹包含 {len(drug_files)} 个药品JSON文件")
        print(f"   - index.json (药品索引)")
        print(f"   - 1.json ~ {len(drug_files)-1}.json (各药品详细数据)")

if __name__ == '__main__':
    main()
