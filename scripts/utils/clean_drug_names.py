#!/usr/bin/env python3
"""清理药品网址汇总文件，去除※▲标记"""

import re

def main():
    input_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计原始※▲标记数量
    original_count = len(re.findall(r'※|▲', content))
    print(f"原始文件中 ※▲ 标记数量: {original_count}")
    
    # 去除药品名称前的※▲标记
    # 处理列表格式: `- ※▲药品名 https://...`
    content = re.sub(r'^(-\s*)[※▲]+', r'\1', content, flags=re.MULTILINE)
    
    # 处理表格格式: `| 序号 | ※▲药品名 | 剂型 | ... |`
    content = re.sub(r'(\|\s*\d+\s*\|\s*)[※▲]+', r'\1', content)
    
    # 保存文件
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 统计清理后的※▲标记数量
    cleaned_count = len(re.findall(r'※|▲', content))
    print(f"清理后 ※▲ 标记数量: {cleaned_count}")
    print(f"✅ 已清理 {original_count - cleaned_count} 个标记")
    print(f"✅ 文件已保存: {input_file}")

if __name__ == '__main__':
    main()
