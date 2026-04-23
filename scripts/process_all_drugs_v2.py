#!/usr/bin/env python3
"""
使用V2改进版脚本处理所有药物
"""

import json
import sys
from pathlib import Path

# 导入V2版本的函数
sys.path.insert(0, str(Path(__file__).parent))
from check_and_fix_drugs_v2 import check_and_fix_drug_v2, DATA_DIR

def main():
    # 获取所有药物ID
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    all_ids = [d['id'] for d in index]
    all_ids.sort()
    
    total = len(all_ids)
    print(f'共有 {total} 个药物需要处理')
    print('使用V2改进版脚本批量处理...\n')
    
    # 处理所有药物
    batch_size = 50
    total_fixed = 0
    total_checked = 0
    
    for i in range(0, total, batch_size):
        batch_ids = all_ids[i:i+batch_size]
        batch_fixed = 0
        
        print(f'处理第 {i+1}-{min(i+batch_size, total)} 个药物...', end=' ')
        
        for drug_id in batch_ids:
            total_checked += 1
            modified, changes = check_and_fix_drug_v2(drug_id)
            if modified:
                batch_fixed += 1
                total_fixed += 1
        
        print(f'修复 {batch_fixed} 个')
        
        # 每处理200个显示进度
        if (i + batch_size) % 200 == 0 or i + batch_size >= total:
            print(f'  进度: {min(i+batch_size, total)}/{total} ({min(i+batch_size, total)/total*100:.1f}%)')
    
    # 汇总
    print(f'\n{"="*70}')
    print('所有药物处理完成！')
    print(f'共检查 {total_checked} 个药物')
    print(f'共修复 {total_fixed} 个药物')
    print(f'修复率: {total_fixed/total_checked*100:.1f}%')
    print(f'{"="*70}')

if __name__ == '__main__':
    main()
