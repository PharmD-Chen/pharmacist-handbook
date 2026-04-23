#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从湖南药事服务网获取甲磺酸酚妥拉明注射液信息 - 改进版
"""

import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://www.hnysfww.com/goods.php?id=153"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

try:
    print(f"正在获取: {url}")
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找药品详情区域
    # 通常药品信息在特定的div或table中
    print("\n查找药品信息...")
    
    # 尝试查找包含"适应证"或"适应症"的元素
    indications_elem = None
    for elem in soup.find_all(text=re.compile(r'适应[证症]')):
        print(f"找到适应证元素: {elem.parent.name}")
        # 获取父元素的文本
        parent = elem.parent
        if parent:
            indications_elem = parent
            break
    
    if indications_elem:
        print(f"\n适应证元素内容: {indications_elem.get_text()[:200]}")
    
    # 查找所有可能包含药品信息的div
    print("\n\n查找所有div元素...")
    divs = soup.find_all('div', class_=re.compile(r'(detail|info|content|main)'))
    print(f"找到 {len(divs)} 个可能的div")
    
    for i, div in enumerate(divs[:5]):
        text = div.get_text(strip=True)
        if len(text) > 100:
            print(f"\nDiv {i+1} (长度: {len(text)}):")
            print(text[:500])
            print("-" * 60)
    
    # 查找所有table
    print("\n\n查找所有table元素...")
    tables = soup.find_all('table')
    print(f"找到 {len(tables)} 个table")
    
    for i, table in enumerate(tables[:3]):
        text = table.get_text(strip=True)
        if len(text) > 50:
            print(f"\nTable {i+1} (长度: {len(text)}):")
            print(text[:500])
            print("-" * 60)
    
    # 保存完整HTML用于分析
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/phentolamine_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print("\n完整HTML已保存到 phentolamine_page.html")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
