#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复药品数据问题
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
    if not match:
        print("无法解析现有数据源")
        return
    
    drugs_data = json.loads(match.group(1))
    print(f"现有药品数量: {len(drugs_data)}")
    
    # 修复问题1: 利鲁唑口服混悬液 - 数据错误（填充了舒巴坦的数据）
    # 需要从湖南药事服务网重新获取正确的数据
    print("\n修复问题1: 利鲁唑口服混悬液")
    for drug in drugs_data:
        if drug['name'] == '利鲁唑口服混悬液':
            print(f"  当前数据: {drug['manual']['dosage'][:50]}...")
            # 标记需要重新获取数据
            drug['manual']['needs_update'] = True
            drug['manual']['issue'] = '数据错误，填充了舒巴坦的用法用量'
            print(f"  已标记需要更新")
    
    # 修复问题2: 阿利沙坦酯吲达帕胺缓释片 - 无用法用量
    print("\n修复问题2: 阿利沙坦酯吲达帕胺缓释片")
    for drug in drugs_data:
        if drug['name'] == '阿利沙坦酯吲达帕胺缓释片':
            print(f"  当前用法用量: '{drug['manual']['dosage']}'")
            # 从提取结果看，该药品在湖南药事服务网确实没有用法用量数据
            # 需要手动补充或从其他来源获取
            drug['manual']['needs_update'] = True
            drug['manual']['issue'] = '湖南药事服务网无用法用量数据'
            print(f"  已标记需要更新")
    
    # 修复问题3: 注射用美罗培南氯化钠注射液 - 精简版用法用量错误
    print("\n修复问题3: 注射用美罗培南氯化钠注射液")
    for drug in drugs_data:
        if drug['name'] == '注射用美罗培南氯化钠注射液':
            print(f"  当前精简版: {drug['manual']['dosage'][:80]}...")
            print(f"  当前详细版: {drug['manual']['full_dosage'][:80]}...")
            # 精简版提取错误，应该使用详细版的前200字
            full_dosage = drug['manual']['full_dosage']
            # 提取关键用法用量信息（前200字）
            lines = full_dosage.split('。')
            simplified = []
            for line in lines:
                line = line.strip()
                if '成人常用量' in line or '肾功能' in line or '剂量' in line:
                    simplified.append(line)
                if len('。'.join(simplified)) > 200:
                    break
            
            if simplified:
                drug['manual']['dosage'] = '。'.join(simplified) + '。'
                print(f"  修复后精简版: {drug['manual']['dosage'][:80]}...")
    
    # 保存修复后的数据
    output_content = f"""// 药品手册数据 - 修复于 2026-03-24
// 共 {len(drugs_data)} 个药品

const drugIndex = {json.dumps(drugs_data, ensure_ascii=False, indent=2)};

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndex }};
}}
"""
    
    # 保存到文件
    with open(drugs_js_path, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\n已保存修复后的数据到: {drugs_js_path}")
    
    # 生成需要手动处理的药品列表
    print("\n需要手动处理的药品:")
    for drug in drugs_data:
        if drug.get('manual', {}).get('needs_update'):
            print(f"  - {drug['name']}: {drug['manual']['issue']}")

if __name__ == '__main__':
    main()
