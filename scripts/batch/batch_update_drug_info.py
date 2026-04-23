#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新药品详细信息
从湖南药事服务网获取药品信息并更新到JSON文件
"""

import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 药品数据目录
DRUGS_DIR = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs'
SUMMARY_FILE = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md'

def fetch_drug_info_from_hnysfww(url):
    """从湖南药事服务网获取药品信息"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"  ❌ 无法访问网址: {url}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取药品信息
        drug_info = {
            'black_box_warning': '',
            'indications': '',
            'full_indications': '',
            'dosage': '',
            'full_dosage': '',
            'contraindications': '',
            'full_contraindications': '',
            'adverse_reactions': '',
            'full_adverse_reactions': '',
            'interactions': '',
            'full_interactions': '',
            'pregnancy_category': '',
            'pharmacokinetics': '',
            'precautions': '',
            'full_precautions': '',
            'source': '湖南药事服务网'
        }
        
        # 提取黑框警告
        black_box = soup.find('div', class_='black-box-warning')
        if black_box:
            drug_info['black_box_warning'] = black_box.get_text(strip=True)
        
        # 提取适应症
        indications_section = soup.find('div', string=re.compile('适应证|适应症'))
        if indications_section:
            parent = indications_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('适应证', '').replace('适应症', '').strip()
                drug_info['indications'] = content[:200] + '...' if len(content) > 200 else content
                drug_info['full_indications'] = content
        
        # 提取用法用量
        dosage_section = soup.find('div', string=re.compile('用法用量'))
        if dosage_section:
            parent = dosage_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('用法用量', '').strip()
                drug_info['dosage'] = content[:200] + '...' if len(content) > 200 else content
                drug_info['full_dosage'] = content
        
        # 提取禁忌症
        contraindications_section = soup.find('div', string=re.compile('禁忌症|禁忌'))
        if contraindications_section:
            parent = contraindications_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('禁忌症', '').replace('禁忌', '').strip()
                drug_info['contraindications'] = content[:200] + '...' if len(content) > 200 else content
                drug_info['full_contraindications'] = content
        
        # 提取不良反应
        adverse_section = soup.find('div', string=re.compile('不良反应'))
        if adverse_section:
            parent = adverse_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('不良反应', '').strip()
                drug_info['adverse_reactions'] = content[:200] + '...' if len(content) > 200 else content
                drug_info['full_adverse_reactions'] = content
        
        # 提取药物相互作用
        interactions_section = soup.find('div', string=re.compile('药物相互作用|相互作用'))
        if interactions_section:
            parent = interactions_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('药物相互作用', '').replace('相互作用', '').strip()
                drug_info['interactions'] = content[:200] + '...' if len(content) > 200 else content
                drug_info['full_interactions'] = content
        
        # 提取注意事项
        precautions_section = soup.find('div', string=re.compile('注意事项'))
        if precautions_section:
            parent = precautions_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('注意事项', '').strip()
                drug_info['precautions'] = content[:200] + '...' if len(content) > 200 else content
                drug_info['full_precautions'] = content
        
        # 提取药理作用
        pharmacology_section = soup.find('div', string=re.compile('药理作用'))
        if pharmacology_section:
            parent = pharmacology_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('药理作用', '').strip()
                drug_info['pharmacokinetics'] = content
        
        # 提取妊娠分级
        pregnancy_section = soup.find('div', string=re.compile('妊娠期用药安全分级|妊娠'))
        if pregnancy_section:
            parent = pregnancy_section.find_parent('div', class_='section')
            if parent:
                content = parent.get_text(strip=True).replace('妊娠期用药安全分级', '').replace('妊娠', '').strip()
                drug_info['pregnancy_category'] = content
        
        return drug_info
        
    except Exception as e:
        print(f"  ❌ 获取信息失败: {e}")
        return None

def update_drug_json(drug_id, drug_info):
    """更新药品JSON文件"""
    json_path = os.path.join(DRUGS_DIR, f'{drug_id}.json')
    
    if not os.path.exists(json_path):
        print(f"  ❌ 药品文件不存在: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 更新manual字段
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        # 只更新非空字段
        for key, value in drug_info.items():
            if value and value.strip():
                drug_data['manual'][key] = value
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 更新JSON失败: {e}")
        return False

def parse_drug_list_line(line):
    """解析药品列表行，提取ID和URL"""
    # 匹配格式: - 药品名 [ID: xxx] https://www.hnysfww.com/goods.php?id=xxx
    match = re.search(r'\[ID:\s*(\d+)\]\s*(https://www\.hnysfww\.com/goods\.php\?id=\d+)', line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def main():
    """主函数"""
    # 读取缺少详细信息的药品列表
    missing_info_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/缺少详细信息的药品列表.md'
    
    if not os.path.exists(missing_info_file):
        print(f"❌ 文件不存在: {missing_info_file}")
        return
    
    with open(missing_info_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取片剂部分（从"### 片"开始到下一个"###"或文件结束）
    tablet_section = re.search(r'### 片.*?\n(.*?)(?=###|$)', content, re.DOTALL)
    if not tablet_section:
        print("❌ 未找到片剂部分")
        return
    
    tablet_lines = tablet_section.group(1).strip().split('\n')
    
    print(f"📋 找到 {len(tablet_lines)} 个片剂药品需要更新")
    print("=" * 60)
    
    updated_count = 0
    failed_count = 0
    
    for i, line in enumerate(tablet_lines, 1):
        line = line.strip()
        if not line or not line.startswith('-'):
            continue
        
        drug_id, url = parse_drug_list_line(line)
        if not drug_id or not url:
            continue
        
        # 提取药品名称
        name_match = re.search(r'-\s*(.+?)\s*\[', line)
        drug_name = name_match.group(1) if name_match else f"药品{drug_id}"
        
        print(f"\n[{i}/{len(tablet_lines)}] 正在更新: {drug_name} (ID: {drug_id})")
        print(f"  URL: {url}")
        
        # 获取药品信息
        drug_info = fetch_drug_info_from_hnysfww(url)
        
        if drug_info:
            # 更新JSON文件
            if update_drug_json(drug_id, drug_info):
                print(f"  ✅ 更新成功")
                updated_count += 1
            else:
                print(f"  ❌ 更新失败")
                failed_count += 1
        else:
            print(f"  ❌ 无法获取信息")
            failed_count += 1
        
        # 添加延迟，避免请求过快
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"✅ 更新完成: {updated_count} 个成功, {failed_count} 个失败")
    print("=" * 60)

if __name__ == '__main__':
    main()
