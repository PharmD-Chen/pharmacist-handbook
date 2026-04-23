#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合所有药品网址来源，更新JSON文件，并填充空缺内容
"""

import pandas as pd
import json
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
from datetime import datetime

# 路径配置
PROJECT_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_DIR = PROJECT_DIR / "pharmacist-handbook/data/drugs"
EXCEL_FILE = PROJECT_DIR / "原始材料/药品目录 20260318.xlsx"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 网址来源文件
URL_SOURCES = [
    PROJECT_DIR / "缺少详细信息的药品列表.md",
    PROJECT_DIR / "药品网址汇总.md",
    PROJECT_DIR / "药品网址汇总_backup.md",
    PROJECT_DIR / "已补充药品网址.txt",
    PROJECT_DIR / "有网址但内容空缺的药品列表.md",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def extract_urls_from_markdown(file_path):
    """从markdown文件中提取药品ID和网址"""
    urls = {}
    
    if not file_path.exists():
        return urls
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配格式: [ID: xxx] https://... 或 | xxx | ... | https://... |
    patterns = [
        r'\[ID:\s*(\d+)\].*?(https://www\.hnysfww\.com/goods\.php\?id=\d+)',
        r'\|\s*(\d+)\s*\|.*?(https://www\.hnysfww\.com/goods\.php\?id=\d+)',
        r'https://www\.hnysfww\.com/goods\.php\?id=(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                drug_id = int(match[0])
                url = match[1] if len(match) > 1 else f"https://www.hnysfww.com/goods.php?id={match[0]}"
            else:
                drug_id = int(match)
                url = f"https://www.hnysfww.com/goods.php?id={match}"
            urls[drug_id] = url
    
    return urls

def load_excel_data():
    """加载Excel数据"""
    df = pd.read_excel(EXCEL_FILE)
    
    # 创建药品字典
    drugs = {}
    for _, row in df.iterrows():
        drug_code = row['药品代码']
        drug_name = row['药品名称']
        chemical_name = row['药品化学名']
        spec = row['药品规格']
        manufacturer = row['厂家名称']
        
        # 从药品代码提取ID
        match = re.search(r'[CX](\d+)', str(drug_code))
        if match:
            drug_id = int(match.group(1))
            drugs[drug_id] = {
                'id': drug_id,
                'code': drug_code,
                'name': drug_name,
                'chemical_name': chemical_name,
                'specification': spec,
                'manufacturer': manufacturer,
            }
    
    return drugs

def integrate_urls():
    """整合所有网址来源"""
    all_urls = {}
    
    for source_file in URL_SOURCES:
        urls = extract_urls_from_markdown(source_file)
        all_urls.update(urls)
        print(f"从 {source_file.name} 提取了 {len(urls)} 个网址")
    
    print(f"\n总共整合了 {len(all_urls)} 个药品网址")
    return all_urls

def check_drug_content(drug_id):
    """检查药品内容是否完整"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return None, "文件不存在"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions']
        
        empty_fields = []
        for field in key_fields:
            value = manual.get(field, '')
            if not value or not str(value).strip():
                empty_fields.append(field)
        
        has_url = bool(data.get('url', {}).get('hnysfww', ''))
        
        return {
            'has_content': len(empty_fields) == 0,
            'empty_fields': empty_fields,
            'has_url': has_url,
            'url': data.get('url', {}).get('hnysfww', ''),
            'source': manual.get('source', '')
        }, None
        
    except Exception as e:
        return None, str(e)

def fetch_drug_info(url):
    """从湖南药事服务网获取药品信息"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        if not tables:
            return None
        
        text = tables[0].get_text()
        return extract_drug_fields(text)
        
    except Exception as e:
        print(f"  获取失败: {e}")
        return None

def extract_drug_fields(text):
    """提取药品各字段"""
    info = {}
    
    # 适应证
    match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_indications'] = content
        info['indications'] = content[:300] + '...' if len(content) > 300 else content
    
    # 药理作用
    match = re.search(r'药理作用(.+?)(?:用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_pharmacokinetics'] = content
        info['pharmacokinetics'] = content[:300] + '...' if len(content) > 300 else content
    
    # 用法用量
    match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_dosage'] = content
        info['dosage'] = content[:300] + '...' if len(content) > 300 else content
    
    # 禁忌
    match = re.search(r'禁忌(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_contraindications'] = content
        info['contraindications'] = content[:300] + '...' if len(content) > 300 else content
    
    # 不良反应
    match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_adverse_reactions'] = content
        info['adverse_reactions'] = content[:300] + '...' if len(content) > 300 else content
    
    # 药物相互作用
    match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_interactions'] = content
        info['interactions'] = content[:300] + '...' if len(content) > 300 else content
    
    # 注意事项
    match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['full_precautions'] = content
        info['precautions'] = content[:300] + '...' if len(content) > 300 else content
    
    # 妊娠分级
    match = re.search(r'妊娠期用药安全分级\s*([A-Z]\s*级?)', text)
    if match:
        info['pregnancy_category'] = match.group(1)
        info['full_pregnancy_category'] = match.group(1)
    elif '妊娠' in text and '级' in text:
        match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
        if match:
            info['pregnancy_category'] = match.group(1)
            info['full_pregnancy_category'] = match.group(1)
    
    info['source'] = '湖南药事服务网'
    return info

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def update_drug_file(drug_id, drug_info, url):
    """更新药品JSON文件"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return False
    
    try:
        if 'manual' not in data:
            data['manual'] = {}
        
        data['manual'].update(drug_info)
        
        if 'url' not in data:
            data['url'] = {}
        data['url']['hnysfww'] = url
        data['url']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"  更新失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("药品信息整合与更新工具")
    print("=" * 80)
    
    # 1. 整合所有网址
    print("\n【步骤1】整合所有网址来源...")
    all_urls = integrate_urls()
    
    # 2. 检查有网址但内容空缺的药品
    print("\n【步骤2】检查有网址但内容空缺的药品...")
    drugs_need_update = []
    
    for drug_id, url in all_urls.items():
        status, error = check_drug_content(drug_id)
        if status and not status['has_content']:
            drugs_need_update.append({
                'id': drug_id,
                'url': url,
                'empty_fields': status['empty_fields']
            })
    
    print(f"找到 {len(drugs_need_update)} 个需要更新的药品")
    
    # 3. 更新药品内容
    print("\n【步骤3】从湖南药事服务网获取并更新药品内容...")
    success_count = 0
    fail_count = 0
    
    for i, drug in enumerate(drugs_need_update, 1):
        print(f"\n[{i}/{len(drugs_need_update)}] ID: {drug['id']}")
        print(f"  网址: {drug['url']}")
        print(f"  空缺字段: {', '.join(drug['empty_fields'])}")
        
        drug_info = fetch_drug_info(drug['url'])
        
        if drug_info and any(drug_info.values()):
            if update_drug_file(drug['id'], drug_info, drug['url']):
                print(f"  ✅ 更新成功")
                success_count += 1
            else:
                print(f"  ❌ 更新失败")
                fail_count += 1
        else:
            print(f"  ⚠️ 无法获取信息或信息为空")
            fail_count += 1
        
        if i < len(drugs_need_update):
            time.sleep(0.5)
    
    # 4. 生成最终报告
    print("\n" + "=" * 80)
    print("更新完成！")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print("=" * 80)
    
    # 5. 生成仍空缺的药品列表
    print("\n【步骤4】生成仍内容空缺的药品列表...")
    still_empty = []
    
    for drug_id, url in all_urls.items():
        status, error = check_drug_content(drug_id)
        if status and not status['has_content']:
            still_empty.append({
                'id': drug_id,
                'url': url,
                'empty_fields': status['empty_fields']
            })
    
    # 保存到文件
    report_file = OUTPUT_DIR / f"仍内容空缺的药品列表_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 仍内容空缺的药品列表\n\n")
        f.write(f"> 生成日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"> 空缺药品数: {len(still_empty)}\n\n")
        f.write("| ID | 网址 | 空缺字段 |\n")
        f.write("|----|------|----------|\n")
        
        for drug in still_empty:
            f.write(f"| {drug['id']} | {drug['url']} | {', '.join(drug['empty_fields'])} |\n")
    
    print(f"已保存到: {report_file}")
    print(f"\n仍有 {len(still_empty)} 个药品内容空缺")

if __name__ == "__main__":
    main()
