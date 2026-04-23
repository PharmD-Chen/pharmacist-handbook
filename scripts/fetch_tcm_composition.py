#!/usr/bin/env python3
"""
自动抓取中成药成份信息
从湖南药事服务网获取所有中成药的成份字段
"""

import json
import re
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}


def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()


def is_tcm_drug(drug_data):
    """判断是否为中成药"""
    # 根据批准文号判断
    for spec in drug_data.get('specifications', []):
        approval = spec.get('approval_number', '')
        if '国药准字Z' in approval:
            return True
    return False


def fetch_composition_from_url(url):
    """从网页获取成份信息"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if not tables:
            return None
        
        text = tables[0].get_text()
        
        # 提取成份 - 中成药通常使用"成份/药理作用"字段
        composition = ""
        
        # 方法1：匹配"成份/药理作用"（最常见）
        match = re.search(r'成份/药理作用\s*\n\s*([^\n]+(?:\n(?!(?:功能主治|用法|不良反应|禁忌|注意事项|药物相互作用|贮藏))[^\n]+)*)', text)
        if match:
            composition = clean_text(match.group(1))
            # 只保留第一行（成份部分），去除药理作用描述
            lines = composition.split('\n')
            if lines:
                composition = lines[0].strip()
        else:
            # 方法2：匹配单独的"成份"字段
            match = re.search(r'成份\s*\n\s*([^\n]+(?:\n(?!(?:性状|功能主治|用法|不良反应|禁忌|注意事项|贮藏))[^\n]+)*)', text)
            if match:
                composition = clean_text(match.group(1))
        
        # 如果成份太长，可能是包含了药理作用，只保留第一行
        if len(composition) > 200:
            lines = composition.split('。')
            if lines:
                composition = lines[0].strip() + '。'
        
        return composition if composition else None
        
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        return None


def update_drug_composition(drug_file, composition):
    """更新药品JSON文件，添加composition字段"""
    try:
        with open(drug_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加到manual中
        if 'manual' not in data:
            data['manual'] = {}
        
        data['manual']['composition'] = composition
        
        # 写回文件
        with open(drug_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"  ❌ 更新文件失败: {e}")
        return False


def main():
    print('🔍 开始处理中成药成份信息...\n')
    
    # 读取index.json
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # 筛选中成药
    tcm_drugs = []
    for drug in index:
        drug_id = drug['id']
        json_file = DATA_DIR / f'{drug_id}.json'
        
        if not json_file.exists():
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if is_tcm_drug(data):
            # 检查是否已有composition字段
            manual = data.get('manual', {})
            if not manual.get('composition'):
                tcm_drugs.append({
                    'id': drug_id,
                    'name': drug['name'],
                    'file': json_file,
                    'url': data.get('url', {}).get('hnysfww', '')
                })
    
    print(f'📊 找到 {len(tcm_drugs)} 个需要补充成份的中成药\n')
    
    # 统计
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    # 处理每个中成药
    for i, drug in enumerate(tcm_drugs, 1):
        print(f'[{i}/{len(tcm_drugs)}] {drug["name"]} (ID: {drug["id"]})')
        
        if not drug['url']:
            print('  ⚠️ 无网址，跳过')
            skip_count += 1
            continue
        
        # 获取成份
        composition = fetch_composition_from_url(drug['url'])
        
        if composition:
            print(f'  ✅ 获取到成份: {composition[:50]}...')
            # 更新文件
            if update_drug_composition(drug['file'], composition):
                success_count += 1
            else:
                fail_count += 1
        else:
            print('  ⚠️ 未找到成份信息')
            skip_count += 1
        
        # 延迟，避免请求过快
        time.sleep(1)
    
    print(f'\n📈 处理完成！')
    print(f'  ✅ 成功: {success_count}')
    print(f'  ❌ 失败: {fail_count}')
    print(f'  ⚠️ 跳过: {skip_count}')


if __name__ == '__main__':
    main()
