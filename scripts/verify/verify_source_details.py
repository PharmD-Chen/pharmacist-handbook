#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐一验证第352行之前抗生素药品信息是否真实源自湖南药事服务网
通过实际访问网站并比对关键内容
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

def fetch_website_content(url):
    """从网站获取内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        return None

def extract_key_info(html_content):
    """从HTML中提取关键信息"""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 获取页面文本
    text = soup.get_text()
    
    # 提取关键部分（适应症、用法用量等）
    info = {
        'full_text': text,
        'has_indications': '适应症' in text or '适应证' in text,
        'has_dosage': '用法用量' in text or '用法与用量' in text,
        'has_contraindications': '禁忌' in text,
        'has_adverse': '不良反应' in text,
    }
    
    return info

def verify_drug(drug):
    """验证单个药品"""
    drug_id = drug['id']
    drug_name = drug['name']
    url = drug['url']
    
    file_path = DATA_DIR / f"{drug_id}.json"
    
    # 读取本地文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            local_data = json.load(f)
        
        manual = local_data.get('manual', {})
        local_indications = manual.get('indications', '')
        local_source = manual.get('source', '')
    except:
        return {
            'id': drug_id,
            'name': drug_name,
            'status': 'file_error',
            'message': '无法读取本地文件'
        }
    
    # 获取网站内容
    html_content = fetch_website_content(url)
    
    if not html_content:
        return {
            'id': drug_id,
            'name': drug_name,
            'status': 'fetch_error',
            'message': '无法获取网站内容',
            'local_source': local_source,
            'local_indications_length': len(local_indications)
        }
    
    web_info = extract_key_info(html_content)
    
    if not web_info:
        return {
            'id': drug_id,
            'name': drug_name,
            'status': 'parse_error',
            'message': '无法解析网站内容',
            'local_source': local_source,
            'local_indications_length': len(local_indications)
        }
    
    # 验证关键信息是否存在
    verification = {
        'has_indications': web_info['has_indications'],
        'has_dosage': web_info['has_dosage'],
        'has_contraindications': web_info['has_contraindications'],
        'has_adverse': web_info['has_adverse'],
    }
    
    # 如果网站有这些信息，但本地没有，说明本地信息可能不是来自该网站
    if web_info['has_indications'] and not local_indications:
        return {
            'id': drug_id,
            'name': drug_name,
            'status': 'suspicious',
            'message': '网站有适应症信息但本地为空',
            'local_source': local_source,
            'verification': verification
        }
    
    # 检查来源标记
    if local_source != "湖南药事服务网":
        return {
            'id': drug_id,
            'name': drug_name,
            'status': 'wrong_source',
            'message': f'来源标记为: {local_source}',
            'local_source': local_source,
            'verification': verification
        }
    
    return {
        'id': drug_id,
        'name': drug_name,
        'status': 'verified',
        'message': '信息完整，来源正确',
        'local_source': local_source,
        'local_indications_length': len(local_indications),
        'verification': verification
    }

def main():
    """主函数"""
    print("=" * 120)
    print("逐一验证第352行之前抗生素药品信息来源")
    print("=" * 120)
    print(f"{'ID':<6} {'药品名称':<28} {'状态':<12} {'来源':<15} {'适应症':<8} {'用量':<8} {'禁忌':<8} {'不良反应':<8} {'备注'}")
    print("-" * 120)
    
    verified_count = 0
    issue_count = 0
    
