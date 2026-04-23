#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证抗生素药品信息是否真实源自湖南药事服务网
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import time

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 第352行之前有网址的抗生素药品
ANTIBIOTIC_DRUGS = [
    {"id": 86, "name": "甲硝唑氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2328"},
    {"id": 77, "name": "盐酸克林霉素", "url": "https://www.hnysfww.com/goods.php?id=2038"},
    {"id": 224, "name": "硫酸阿米卡星", "url": "https://www.hnysfww.com/goods.php?id=1980"},
    {"id": 398, "name": "盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 281, "name": "左氧氟沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 439, "name": "克林霉素磷酸酯", "url": "https://www.hnysfww.com/goods.php?id=2039"},
    {"id": 656, "name": "注射用头孢曲松钠/氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1907"},
    {"id": 658, "name": "注射用头孢地嗪钠/5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=1916"},
    {"id": 757, "name": "※▲盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 804, "name": "利奈唑胺葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=2115"},
    {"id": 916, "name": "※硫酸庆大霉素", "url": "https://www.hnysfww.com/goods.php?id=1977"},
    {"id": 282, "name": "左氧氟沙星片", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 495, "name": "盐酸莫西沙星片", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 677, "name": "阿奇霉素片", "url": "https://www.hnysfww.com/goods.php?id=2016"},
    {"id": 970, "name": "甲硝唑片", "url": "https://www.hnysfww.com/goods.php?id=2328"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}

def fetch_website_content(url):
    """从网站获取内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Error: {e}"

def verify_drug_info(drug_id, drug_name, url):
    """验证单个药品的信息"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return {"status": "missing_file", "message": "文件不存在"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        indications = manual.get('indications', '')
        
        # 获取网站内容
        website_content = fetch_website_content(url)
        
        if website_content.startswith("Error"):
            return {
                "status": "fetch_error", 
                "message": f"无法获取网站内容: {website_content}",
                "indications_length": len(indications),
                "source": manual.get('source', '')
            }
        
        # 检查适应症是否来自网站
        # 提取适应症的前20个字符作为关键词
        if len(indications) > 20:
            keyword = indications[:20].replace(" ", "").replace("\n", "")
        else:
            keyword = indications.replace(" ", "").replace("\n", "")
        
        # 清理网站内容
        website_clean = website_content.replace(" ", "").replace("\n", "").replace("\t", "")
        
        # 检查关键词是否存在于网站内容中
        if keyword and keyword in website_clean:
            return {
                "status": "verified", 
                "message": "适应症内容验证通过",
                "indications_length": len(indications),
                "source": manual.get('source', ''),
                "keyword_found": keyword[:30] + "..." if len(keyword) > 30 else keyword
            }
        else:
            return {
                "status": "mismatch", 
                "message": "适应症内容可能不来自该网站",
                "indications_length": len(indications),
                "source": manual.get('source', ''),
                "keyword_checked": keyword[:30] + "..." if len(keyword) > 30 else keyword
            }
        
    except Exception as e:
        return {"status": "error", "message": f"验证错误: {e}"}

def main():
    """主函数"""
    print("=" * 100)
    print("验证抗生素药品信息来源 - 第352行之前的药品")
    print("=" * 100)
    print(f"{'ID':<6} {'药品名称':<25} {'状态':<15} {'来源':<15} {'信息长度':<10} {'备注'}")
    print("-" * 100)
    
    verified_count = 0
    mismatch_count = 0
    error_count = 0
    
    for i, drug in enumerate(ANTIBIOTIC_DRUGS, 1):
        result = verify_drug_info(drug['id'], drug['name'], drug['url'])
        
        status_icon = "❓"
        if result['status'] == 'verified':
            status_icon = "✅"
            verified_count += 1
        elif result['status'] == 'mismatch':
            status_icon = "⚠️"
            mismatch_count += 1
        elif result['status'] in ['fetch_error', 'error']:
            status_icon = "❌"
            error_count += 1
        
        print(f"{drug['id']:<6} {drug['name']:<25} {status_icon} {result['status']:<12} {result.get('source', 'N/A'):<15} {result.get('indications_length', 0):<10} {result['message']}")
        
        # 添加延迟避免请求过快
        if i < len(ANTIBIOTIC_DRUGS):
            time.sleep(1)
    
    print("=" * 100)
    print(f"验证完成: ✅ 验证通过 {verified_count} 个 | ⚠️ 可能不匹配 {mismatch_count} 个 | ❌ 错误 {error_count} 个")
    print("=" * 100)
    
    if mismatch_count > 0:
        print("\n⚠️ 警告：部分药品信息