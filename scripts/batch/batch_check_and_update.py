#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量检查并更新第352行之前的药品信息
从湖南药事服务网获取缺失的药品说明书
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path
import time

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")
LIST_FILE = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/缺少详细信息的药品列表.md")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def parse_drug_list():
    """解析药品列表文件，获取第352行之前的药品信息"""
    drugs = []
    
    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:352]  # 只读取前352行
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or not line.startswith('- '):
            continue
        
        # 解析格式: - 药品名称 ((类别)完整名称[标记]) [ID: xxx] https://...
        match = re.match(r'-\s+(.+?)\s+\((.+?)\)\s+\[ID:\s*(\d+)\]\s*(https://.+)?', line)
        
        if match:
            drug_name = match.group(1).strip()
            full_info = match.group(2).strip()
            drug_id = int(match.group(3))
            url = match.group(4).strip() if match.group(4) else None
            
            if url:  # 只处理有网址的药品
                drugs.append({
                    'id': drug_id,
                    'name': drug_name,
                    'url': url,
                    'line_num': line_num
                })
    
    return drugs

def fetch_drug_info(url):
    """从湖南药事服务网获取药品信息"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含药品信息的table
        tables = soup.find_all('table')
        
        if not tables:
            return None
        
        # 第一个table通常包含主要信息
        text = tables[0].get_text()
        
        return extract_drug_info(text)
        
    except Exception as e:
        print(f"  获取失败: {e}")
        return None

def extract_drug_info(text):
    """从文本中提取药品信息"""
    info = {
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
        'full_pregnancy_category': '',
        'pharmacokinetics': '',
        'full_pharmacokinetics': '',
        'precautions': '',
        'full_precautions': ''
    }
    
    # 提取适应证
    if '适应证' in text:
        match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_indications'] = content
            info['indications'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取药理作用（用于药代动力学）
    if '药理作用' in text:
        match = re.search(r'药理作用(.+?)(?:用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_pharmacokinetics'] = content
            info['pharmacokinetics'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取用法用量
    if '用法用量' in text or '用法与用量' in text:
        match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_dosage'] = content
            info['dosage'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取禁忌
    if '禁忌' in text:
        match = re.search(r'禁忌(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_contraindications'] = content
            info['contraindications'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取不良反应
    if '不良反应' in text:
        match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_adverse_reactions'] = content
            info['adverse_reactions'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取药物相互作用
    if '药物相互作用' in text:
        match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_interactions'] = content
            info['interactions'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取注意事项
    if '注意事项' in text:
        match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
        if match:
            content = clean_text(match.group(1))
            info['full_precautions'] = content
            info['precautions'] = content[:300] + '...' if len(content) > 300 else content
    
    # 提取妊娠分级
    if '妊娠期用药安全分级' in text:
        match = re.search(r'妊娠期用药安全分级\s*([A-Z]\s*级?)', text)
        if match:
            info['pregnancy_category'] = match.group(1)
            info['full_pregnancy_category'] = match.group(1)
    elif '妊娠' in text and '级' in text:
        match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
        if match:
            info['pregnancy_category'] = match.group(1)
            info['full_pregnancy_category'] = match.group(1)
    
    return info

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def check_drug_status(drug_id):
    """检查药品当前状态"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        
        # 检查关键字段是否为空
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions']
        empty_fields = [field for field in key_fields if not manual.get(field, '').strip()]
        
        return {
            'has_data': len(empty_fields) == 0,
            'empty_fields': empty_fields,
            'source': manual.get('source', ''),
            'file_url': data.get('url', {}).get('hnysfww', '')
        }
    except:
        return None

def update_drug_file(drug_id, drug_info, url):
    """更新药品JSON文件"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新manual字段
        if 'manual' not in data:
            data['manual'] = {}
        
        manual = data['manual']
        manual.update(drug_info)
        manual['source'] = '湖南药事服务网'
        
        # 更新URL
        if 'url' not in data:
            data['url'] = {}
        data['url']['hnysfww'] = url
        data['url']['last_updated'] = '2026-03-21'
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"  更新失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 100)
    print("批量检查并更新第352行之前的药品信息")
    print("=" * 100)
    
    # 解析药品列表
    drugs = parse_drug_list()
    print(f"\n找到 {len(drugs)} 个有网址的药品（第352行之前）\n")
    
    # 检查每个药品的状态
    need_update = []
    for drug in drugs:
        status = check_drug_status(drug['id'])
        if status and not status['has_data']:
            need_update.append({
                **drug,
                'empty_fields': status['empty_fields']
            })
    
    print(f"需要更新的药品: {len(need_update)} 个\n")
    print("-" * 100)
    
    if not need_update:
        print("所有药品信息已完整！")
        return
    
    # 更新药品信息
    success_count = 0
    fail_count = 0
    
    for i, drug in enumerate(need_update, 1):
        print(f"\n[{i}/{len(need_update)}] {drug['name']} (ID: {drug['id']})")
        print(f"  网址: {drug['url']}")
        print(f"  缺少字段: {', '.join(drug['empty_fields'])}")
        
        # 获取药品信息
        drug_info = fetch_drug_info(drug['url'])
        
        if drug_info:
            # 更新文件
            if update_drug_file(drug['id'], drug_info, drug['url']):
                print(f"  ✅ 更新成功")
                success_count += 1
            else:
                print(f"  ❌ 更新失败")
                fail_count += 1
        else:
            print(f"  ❌ 无法获取信息")
            fail_count += 1
        
        # 添加延迟
        if i < len(need_update):
            time.sleep(1)
    
    print("\n" + "=" * 100)
    print(f"更新完成: ✅ 成功 {success_count} 个 | ❌ 失败 {fail_count} 个")
    print("=" * 100)

if __name__ == "__main__":
    main()
