#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将新药品添加到数据源文件中
"""

import json
import re
from datetime import datetime

def main():
    # 读取现有数据源
    drugs_js_path = 'pharmacist-handbook/data/drugs/drugs.js'
    with open(drugs_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取现有数据
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("无法解析现有数据源")
        return
    
    existing_drugs = json.loads(match.group(1))
    print(f"现有药品数量: {len(existing_drugs)}")
    
    # 读取新药品数据
    with open('原始材料/新药品手册数据.json', 'r', encoding='utf-8') as f:
        new_drugs = json.load(f)
    
    print(f"新药品数量: {len(new_drugs)}")
    
    # 为新药品分配ID
    max_id = max(drug.get('id', 0) for drug in existing_drugs)
    for i, drug in enumerate(new_drugs, 1):
        drug['id'] = max_id + i
    
    # 合并数据
    all_drugs = existing_drugs + new_drugs
    print(f"合并后药品总数: {len(all_drugs)}")
    
    # 生成新的JS文件内容
    output_content = f"""// 药品手册数据 - 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 共 {len(all_drugs)} 个药品

const drugIndex = {json.dumps(all_drugs, ensure_ascii=False, indent=2)};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndex }};
}}
"""
    
    # 保存到新的JS文件
    output_path = 'pharmacist-handbook/data/drugs/drugs_updated.js'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\n已保存到: {output_path}")
    
    # 同时更新原文件
    with open(drugs_js_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"已更新原文件: {drugs_js_path}")
    
    # 显示新添加的药品
    print("\n新添加的药品:")
    for drug in new_drugs:
        print(f"  ID {drug['id']}: {drug['name']}")
        if drug.get('manual', {}).get('dosage'):
            print(f"    用法用量: {drug['manual']['dosage'][:50]}...")

if __name__ == '__main__':
    main()
