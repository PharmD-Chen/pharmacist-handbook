#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加阿利沙坦酯吲达帕胺缓释片的用法用量
"""

import json
import re

def main():
    # 读取现有数据源
    drugs_js_path = 'pharmacist-handbook/data/drugs/drugs.js'
    with open(drugs_js_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取现有数据
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    drugs_data = json.loads(match.group(1))
    
    # 添加用法用量
    dosage_info = "每日一次，每次一片"
    
    for drug in drugs_data:
        if drug['name'] == '阿利沙坦酯吲达帕胺缓释片':
            print("更新阿利沙坦酯吲达帕胺缓释片的用法用量...")
            
            # 更新用法用量
            drug['manual']['dosage'] = dosage_info
            drug['manual']['full_dosage'] = dosage_info
            
            # 移除标记
            if 'needs_update' in drug['manual']:
                del drug['manual']['needs_update']
            if 'issue' in drug['manual']:
                del drug['manual']['issue']
            
            print(f"  ✓ 用法用量: {dosage_info}")
    
    # 保存更新后的数据
    output_content = f"""// 药品手册数据 - 更新于 2026-03-24
// 共 {len(drugs_data)} 个药品

const drugIndex = {json.dumps(drugs_data, ensure_ascii=False, indent=2)};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndex }};
}}
"""
    
    with open(drugs_js_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\n已保存更新后的数据到: {drugs_js_path}")

if __name__ == '__main__':
    main()
