#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量抓取60个片剂药品的详细说明书内容
从湖南药事服务网抓取并更新到JSON文件
"""

import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = BASE_DIR / "pharmacist-handbook/data/drugs"
MISSING_LIST_FILE = BASE_DIR / "缺少详细信息的药品列表.md"

def get_empty_manual_drugs():
    """获取内容空缺的60个药品信息"""
    drugs = []
    
    with open(MISSING_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 第16-220行（索引15-219）
    for i in range(15, min(220, len(lines))):
        line = lines[i].strip()
        if line.startswith('-'):
            # 解析行
            pattern = r'-\s*(.+?)\s*\((.+?)\)\s*\[ID:\s*(\d+)\]\s*(https://www\.hnysfww\.com/goods\.php\?id=\d+)?'
            match = re.match(pattern, line)
            
            if match:
                drug_id = int(match.group(3))
                url = match.group(4) if match.group(4) else None
                
                # 只处理有网址的药品
                if url:
                    # 检查内容是否空缺
                    json_path = DRUGS_DIR / f'{drug_id}.json'
                    if json_path.exists():
                        with open(json_path, 'r', encoding='utf-8') as f:
                            drug_data = json.load(f)
                        
                        # 检查manual字段是否为空
                        if 'manual' in drug_data:
                            manual = drug_data['manual']
                            key_fields = ['indications', 'dosage', 'contraindications', 
                                         'adverse_reactions', 'interactions', 'precautions']
                            empty_count = sum(1 for f in key_fields if not manual.get(f))
                            
                            if empty_count >= 4:  # 如果4个或以上字段为空，认为内容空缺
                                drugs.append({
                                    'id': drug_id,
                                    'name': match.group(1).strip(),
                                    'spec': match.group(2).strip(),
                                    'url': url
                                })
    
    return drugs

def fetch_webpage_content(url):
    """抓取网页内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
        return None

def parse_drug_manual(html_content, drug_name):
    """解析网页内容，提取药品说明书信息"""
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    manual = {
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
        'full_pharmacokinetics': '',
        'precautions': '',
        'full_precautions': '',
        'source': '湖南药事服务网',
        'url_added': True
    }
    
    # 查找说明书内容区域
    # 尝试多种可能的选择器
    content_div = None
    
    # 方法1: 查找特定的div
    content_div = soup.find('div', class_='goods_desc') or \
                  soup.find('div', id='goods_desc') or \
                  soup.find('div', class_='description')
    
    # 方法2: 查找包含说明书内容的区域
    if not content_div:
        for div in soup.find_all('div'):
            text = div.get_text()
            if '【适应证】' in text or '【适应症】' in text or '【用法与用量】' in text:
                content_div = div
                break
    
    # 方法3: 查找table中的内容
    if not content_div:
        for table in soup.find_all('table'):
            text = table.get_text()
            if '【适应证】' in text or '【适应症】' in text:
                content_div = table
                break
    
    if content_div:
        text = content_div.get_text(separator='\n', strip=True)
        
        # 提取适应症
        for pattern in [r'【适应证】\s*(.+?)(?=【|$)', r'【适应症】\s*(.+?)(?=【|$)']:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                manual['full_indications'] = match.group(1).strip()
                manual['indications'] = condense_indications(manual['full_indications'])
                break
        
        # 提取用法用量
        match = re.search(r'【用法与用量】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['full_dosage'] = match.group(1).strip()
            manual['dosage'] = condense_dosage(manual['full_dosage'])
        
        # 提取禁忌症
        match = re.search(r'【禁忌症?】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['full_contraindications'] = match.group(1).strip()
            manual['contraindications'] = condense_contraindications(manual['full_contraindications'])
        
        # 提取不良反应
        match = re.search(r'【不良反应】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['full_adverse_reactions'] = match.group(1).strip()
            manual['adverse_reactions'] = condense_adverse_reactions(manual['full_adverse_reactions'])
        
        # 提取药物相互作用
        match = re.search(r'【药物相互作用】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['full_interactions'] = match.group(1).strip()
            manual['interactions'] = condense_interactions(manual['full_interactions'])
        
        # 提取妊娠分级
        match = re.search(r'【FDA妊娠分级】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['pregnancy_category'] = match.group(1).strip()
        
        # 提取药代动力学/药理作用
        match = re.search(r'【药理作用】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['full_pharmacokinetics'] = match.group(1).strip()
            manual['pharmacokinetics'] = extract_pharmacokinetics(manual['full_pharmacokinetics'])
        
        # 提取注意事项
        match = re.search(r'【注意事项】\s*(.+?)(?=【|$)', text, re.DOTALL)
        if match:
            manual['full_precautions'] = match.group(1).strip()
            manual['precautions'] = condense_precautions(manual['full_precautions'])
    
    # 如果没有找到适应症，返回None
    if not manual['indications']:
        return None
    
    return manual

def condense_indications(text):
    """精简适应症"""
    if not text:
        return ""
    text = re.sub(r'本品适用于治疗', '用于', text)
    text = re.sub(r'本品用于', '用于', text)
    text = re.sub(r'请?', '', text)
    text = re.sub(r'。', '；', text)
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def condense_dosage(text):
    """精简用法用量"""
    if not text:
        return ""
    lines = text.split('\n')
    condensed = []
    for line in lines:
        line = line.strip()
        if any(kw in line for kw in ['口服', '一次', '一日', 'mg', 'g', 'ml', '静脉', '皮下', '肌内']):
            condensed.append(line)
    result = ' '.join(condensed[:2])
    if len(result) > 150:
        result = result[:147] + "..."
    return result if result else text[:150]

def condense_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    text = re.sub(r'因为.*?(?=；|$)', '', text)
    text = re.sub(r'由于.*?(?=；|$)', '', text)
    text = re.sub(r'。', '；', text)
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def condense_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    lines = text.split('\n')
    condensed = []
    for line in lines:
        line = line.strip()
        if any(kw in line for kw in ['常见', '偶见', '罕见', '十分罕见']):
            condensed.append(line)
    result = ' '.join(condensed[:3])
    if len(result) > 150:
        result = result[:147] + "..."
    return result if result else text[:150]

def condense_interactions(text):
    """精简药物相互作用"""
    if not text or '尚未' in text or '暂无' in text or '不明确' in text:
        return "暂未发现有临床意义的药物相互作用。"
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def extract_pharmacokinetics(text):
    """提取药代动力学关键参数"""
    if not text:
        return ""
    
    params = []
    
    tmax_match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', text)
    if tmax_match:
        params.append(f"达峰时间{tmax_match.group(1)}h")
    
    half_life_match = re.search(r'半衰期.*?([\d\.]+)\s*小时', text)
    if half_life_match:
        params.append(f"半衰期{half_life_match.group(1)}h")
    
    bio_match = re.search(r'生物利用度.*?([\d\.]+)%', text)
    if bio_match:
        params.append(f"生物利用度{bio_match.group(1)}%")
    
    return '，'.join(params) if params else ""

def condense_precautions(text):
    """精简注意事项"""
    if not text:
        return ""
    text = re.sub(r'建议.*?(?=；|$)', '', text)
    text = re.sub(r'。', '；', text)
    if len(text) > 150:
        text = text[:147] + "..."
    return text

def update_drug_json(drug_id, manual):
    """更新药品JSON文件"""
    json_path = DRUGS_DIR / f'{drug_id}.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    drug_data['manual'] = manual
    
    if 'url' not in drug_data:
        drug_data['url'] = {}
    drug_data['url']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    return True

def main():
    print("=" * 70)
    print("批量抓取60个片剂药品说明书内容")
    print("=" * 70)
    
    # 1. 获取需要处理的药品
    print("\n📋 步骤1: 读取内容空缺的药品列表...")
    drugs = get_empty_manual_drugs()
    print(f"   找到 {len(drugs)} 个内容空缺的药品")
    
    if not drugs:
        print("   ✅ 所有药品内容已完整，无需处理")
        return
    
    # 2. 批量处理
    print("\n🌐 步骤2: 开始抓取网页内容...")
    success_count = 0
    failed_count = 0
    failed_drugs = []
    
    for i, drug in enumerate(drugs, 1):
        print(f"\n[{i}/{len(drugs)}] 处理药品 ID: {drug['id']}")
        print(f"  📄 {drug['name']}")
        print(f"  🔗 {drug['url']}")
        
        # 抓取网页
        html_content = fetch_webpage_content(drug['url'])
        if not html_content:
            print(f"  ❌ 抓取失败")
            failed_count += 1
            failed_drugs.append(drug)
            time.sleep(1)
            continue
        
        # 解析内容
        manual = parse_drug_manual(html_content, drug['name'])
        if not manual:
            print(f"  ❌ 未找到说明书内容")
            failed_count += 1
            failed_drugs.append(drug)
            time.sleep(1)
            continue
        
        # 显示提取的内容摘要
        print(f"  ✓ 适应症: {manual['indications'][:50]}...")
        print(f"  ✓ 用法用量: {manual['dosage'][:50]}...")
        
        # 更新JSON
        if update_drug_json(drug['id'], manual):
            print(f"  ✅ 更新成功")
            success_count += 1
        else:
            print(f"  ❌ 更新失败")
            failed_count += 1
            failed_drugs.append(drug)
        
        # 延迟
        time.sleep(1.5)
    
    # 3. 生成报告
    print("\n" + "=" * 70)
    print("📊 处理结果汇总")
    print("=" * 70)
    print(f"总药品数: {len(drugs)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    
    if failed_drugs:
        print(f"\n❌ 失败的药品:")
        for drug in failed_drugs:
            print(f"   - [{drug['id']}] {drug['name']}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
