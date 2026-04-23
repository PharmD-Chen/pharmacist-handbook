#!/usr/bin/env python3
"""
从 index.json 重新生成 drugs.js 文件
"""

import json
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data')

def main():
    print('读取 index.json...')
    with open(DATA_DIR / 'drugs/index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)

    print(f'共有 {len(index)} 个药品')

    # 生成 drugs.js
    js_content = f'const drugIndex = {json.dumps(index, ensure_ascii=False, indent=2)};'

    print('写入 drugs.js...')
    with open(DATA_DIR / 'drugs.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    print('✅ 完成!')

if __name__ == '__main__':
    main()
