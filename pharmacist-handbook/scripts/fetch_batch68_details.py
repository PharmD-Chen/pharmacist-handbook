#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取batch68药品详细信息
"""

import json
import requests
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
BATCH_FILE = BASE_DIR / "pharmacist-handbook/data/common_drugs_batch68.json"
OUTPUT_FILE = BASE_DIR / "pharmacist-handbook/data/common_drugs_batch68_fetched.json"

def fetch_drug_detail(url):
    """从湖南药事服务网抓取药品详细信息"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"  ✗ 请求失败: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取药品信息
        info = {
            'indications': '',
            'dosage': '',
            'contraindications': '',
            'adverse_reactions': '',
            'interactions': '',
            'pregnancy_category': '',
            'pharmacokinetics': '',
            'precautions': '',
            'source': '湖南药事服务网'
        }
        
        # 尝试提取适应症
        indications_patterns = ['适应症', '功能主治', '主治']
        for pattern in indications_patterns:
            elem = soup.find(string=re.compile(pattern))
            if elem:
                parent = elem.find_parent(['div', 'td', 'p', 'span'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        info['indications'] = next_elem.get_text(strip=True)
                        break
        
        # 尝试提取用法用量
        dosage_patterns = ['用法用量', '用法用']
        for pattern in dosage_patterns:
            elem = soup.find(string=re.compile(pattern))
            if elem:
                parent = elem.find_parent(['div', 'td', 'p', 'span'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        info['dosage'] = next_elem.get_text(strip=True)
                        break
        
        # 尝试提取禁忌
        contraindications_patterns = ['禁忌', '禁忌症']
        for pattern in contraindications_patterns:
            elem = soup.find(string=re.compile(pattern))
            if elem:
                parent = elem.find_parent(['div', 'td', 'p', 'span'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        info['contraindications'] = next_elem.get_text(strip=True)
                        break
        
        # 尝试提取不良反应
        adverse_patterns = ['不良反应', '副作用']
        for pattern in adverse_patterns:
            elem = soup.find(string=re.compile(pattern))
            if elem:
                parent = elem.find_parent(['div', 'td', 'p', 'span'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        info['adverse_reactions'] = next_elem.get_text(strip=True)
                        break
        
        # 尝试提取药物相互作用
        interactions_patterns = ['药物相互作用', '相互作用']
        for pattern in interactions_patterns:
            elem = soup.find(string=re.compile(pattern))
            if elem:
                parent = elem.find_parent(['div', 'td', 'p', 'span'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        info['interactions'] = next_elem.get_text(strip=True)
                        break
        
        # 尝试提取注意事项
        precautions_patterns = ['注意事项', '注意']
        for pattern in precautions_patterns:
            elem = soup.find(string=re.compile(pattern))
            if elem:
                parent = elem.find_parent(['div', 'td', 'p', 'span'])
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        info['precautions'] = next_elem.get_text(strip=True)
                        break
        
        # 如果以上方法都没获取到数据，尝试从页面文本中提取
        if not any(info.values()):
            # 获取页面主要内容
            content = soup.get_text()
            # 清理文本
            content = re.sub(r'\s+', ' ', content)
            
            # 尝试匹配常见的药品信息模式
            indications_match = re.search(r'适应症[：:]\s*([^；。]+)', content)
            if indications_match:
                info['indications'] = indications_match.group(1).strip()[:500]
            
            dosage_match = re.search(r'用法用量[：:]\s*([^；。]+)', content)
            if dosage_match:
                info['dosage'] = dosage_match.group(1).strip()[:500]
        
        return info
        
    except Exception as e:
        print(f"  ✗ 抓取异常: {e}")
        return None

def process_batch():
    """处理批次药品"""
    # 读取批次文件
    with open(BATCH_FILE, 'r', encoding='utf-8') as f:
        drugs = json.load(f)
    
    print(f"开始处理 {len(drugs)} 个药品...\n")
    
    results = []
    success_count = 0
    
    for i, drug in enumerate(drugs, 1):
        name = drug['name']
        dosage = drug['dosage_form']
        url = drug['url']
        
        print(f"[{i}/{len(drugs)}] 抓取: {name} {dosage}")
        
        # 抓取详细信息
        manual = fetch_drug_detail(url)
        
        if manual and any(manual.values()):
            drug_data = {
                'name': name,
                'chemical_name': name.replace('※', '').replace('▲', '').strip(),
                'dosage_form': dosage,
                'specifications': [],
                'manufacturers': [],
                'manual': manual
            }
            results.append(drug_data)
            success_count += 1
            print(f"  ✓ 成功获取详细信息")
        else:
            # 创建空结构
            drug_data = {
                'name': name,
                'chemical_name': name.replace('※', '').replace('▲', '').strip(),
                'dosage_form': dosage,
                'specifications': [],
                'manufacturers': [],
                'manual': {
                    'indications': '',
                    'dosage': '',
                    'contraindications': '',
                    'adverse_reactions': '',
                    'interactions': '',
                    'pregnancy_category': '',
                    'pharmacokinetics': '',
                    'precautions': '',
                    'source': '湖南药事服务网'
                }
            }
            results.append(drug_data)
            print(f"  ⚠ 未获取到详细信息，使用空结构")
        
        time.sleep(1)  # 避免请求过快
    
    # 保存结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"处理完成: {success_count}/{len(drugs)}")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"{'='*60}")
    
    return results

if __name__ == '__main__':
    process_batch()
