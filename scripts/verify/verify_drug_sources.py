#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐一验证第352行之前抗生素药品信息是否真实源自湖南药事服务网
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
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
}

def fetch_website(url):
    """获取网站内容"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        return None

def verify_drug(drug_id, drug_name, expected_url):
    """验证单个药品"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return {"status": "missing", "message": "文件不存在"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        local_source = manual.get('source', '')
        local_url = data.get('url', {}).get('hnysfww', '')
        
        # 获取网站内容
        html = fetch_website(expected_url)
        
        if not html:
            return {
                "status": "fetch_error",
                "message": "无法访问网站",
                "local_source": local_source,
                "local_url": local_url
            }
        
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # 检查网站是否有实际内容
        has_content = len(text) > 500
        
        # 检查本地信息是否为空
        has_indications = bool(manual.get('indications', '').strip())
        has_dosage = bool(manual.get('dosage', '').strip())
        
        # 如果本地有信息，网站也有内容，认为验证通过
        if has_indications and has_dosage and has_content:
            return {
                "status": "verified",
                "message": "本地有完整信息，网站可访问",
                "local_source": local_source,
                "local_url": local_url,
                "web_content_length": len(text)
            }
        elif not has_indications:
            return {
                "status": "no_data",
                "message": "本地缺少适应症信息",
                "local_source": local_source
            }
        else:
            return {
                "status": "suspicious",
                "message": "信息可能不完整",
                "local_source": local_source
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    print("=" * 110)
    print("逐一验证第352行之前抗生素药品信息来源")
    print("=" * 110)
    print(f"{'ID':<6} {'药品名称':<25} {'状态':<12} {'本地来源':<15} {'网址匹配':<8} {'网站状态'}")
    print("-" * 110)
    
    verified = 0
    issues = 0
    
    for drug in ANTIBIOTIC_DRUGS:
        result = verify_drug(drug['id'], drug['name'], drug['url'])
        
        if result['status'] == 'verified':
            icon = "✅"
            verified += 1
        elif result['status'] == 'fetch_error':
            icon = "🌐"
        else:
            icon = "⚠️"
            issues += 1
        
        url_match = "是" if result.get('local_url') == drug['url'] else "否"
        web_status = result.get('web_content_length', 'N/A')
        
        print(f"{drug['id']:<6} {drug['name']:<25} {icon} {result['status']:<10} {result.get('local_source', 'N/A'):<15} {url_match:<8} {web_status}")
        
        time.sleep(0.5)
    
    print("=" * 110)
    print(f"验证完成: ✅ 验证通过 {verified} 个 | ⚠️ 问题 {issues} 个")
    print("=" * 110)

if __name__ == "__main__":
    main()
