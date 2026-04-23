#!/usr/bin/env python3
"""修复drugs.js中的语法错误 - 未转义的换行符"""

import re

def fix_json_syntax():
    print("正在读取 drugs.js 文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("查找并修复未转义的换行符...")
    
    # 找到所有在字符串值中的未转义换行符
    # 匹配模式：在双引号字符串中的换行符
    
    # 方法：逐行处理，找到不完整的字符串
    lines = content.split('\n')
    fixed_lines = []
    in_multiline_string = False
    multiline_buffer = ""
    
    for i, line in enumerate(lines):
        if in_multiline_string:
            # 检查这一行是否结束多行字符串
            # 如果这一行包含未转义的"，可能是字符串结束
            # 但需要检查是否是奇数个引号
            quote_count = line.count('"')
            escaped_quote_count = line.count('\\"')
            actual_quotes = quote_count - escaped_quote_count
            
            if actual_quotes > 0:
                # 字符串结束
                multiline_buffer += '<br>' + line.strip()
                fixed_lines.append(multiline_buffer)
                in_multiline_string = False
                multiline_buffer = ""
            else:
                # 继续多行字符串
                multiline_buffer += '<br>' + line.strip()
        else:
            # 检查是否是多行字符串的开始
            # 如果这一行包含奇数个未转义的引号，可能是多行字符串
            quote_count = line.count('"')
            escaped_quote_count = line.count('\\"')
            actual_quotes = quote_count - escaped_quote_count
            
            # 检查是否是属性行但未结束
            if ':' in line and actual_quotes % 2 == 1 and not line.strip().endswith(','):
                # 可能是多行字符串的开始
                if not line.strip().endswith('"'):
                    in_multiline_string = True
                    multiline_buffer = line
                    continue
            
            fixed_lines.append(line)
    
    # 如果还有未结束的多行字符串，添加它
    if in_multiline_string and multiline_buffer:
        fixed_lines.append(multiline_buffer)
    
    new_content = '\n'.join(fixed_lines)
    
    print("正在保存修复后的文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 修复完成！")
    
    # 再次检查
    print("\n验证修复结果...")
    import subprocess
    result = subprocess.run(
        ['node', '--check', '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ 语法检查通过！")
    else:
        print("❌ 仍有语法错误:")
        print(result.stderr[:500])

if __name__ == '__main__':
    fix_json_syntax()
