#!/usr/bin/env python3
"""更新替加环素的药物相互作用精简版"""

import re

def update_tigecycline():
    """更新替加环素的药物相互作用"""
    
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找替加环素的记录
    pattern = r'("name": "※▲注射用替加环素".*?"interactions": ")([^"]*)(".*?"source":)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print(f"找到替加环素记录")
        print(f"当前interactions: {match.group(2)[:100]}...")
        
        # 替换为新的精简内容
        new_content = content[:match.start(2)] + "暂未发现有临床意义的药物相互作用。" + content[match.end(2):]
        
        with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 已更新替加环素的药物相互作用为：暂未发现有临床意义的药物相互作用。")
        return True
    else:
        print("❌ 未找到替加环素记录")
        return False

if __name__ == '__main__':
    update_tigecycline()
