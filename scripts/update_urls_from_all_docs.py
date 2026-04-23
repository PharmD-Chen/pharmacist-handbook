#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从多个文档中提取网址并更新到药品JSON文件中
"""

import json
import re
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"
SUPPLEMENTED_FILE = PROJECT_ROOT / "已补充药品网址.txt"

# 要查找的文档列表
DOC_FILES = [
    PROJECT_ROOT / "缺少详细信息的药品列表.md",
    PROJECT_ROOT / "药品网址汇总.md",
    PROJECT_ROOT / "药品网址汇总_backup.md",
    PROJECT_ROOT / "有网址但内容空缺的药品列表.md"
]

def parse_md_file(file_path):
    """解析markdown文件，提取药品名称和网址"""
    drug_urls = {}
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return drug_urls
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 方法1: 匹配表格中的链接格式 [链接](https://...) 或 [链接](url)
    table_pattern = r'\|\s*\d+\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(\d+)\s*\|\s*\[链接\]\((https://www\.hnysfww\.com/goods\.php\?id=\d+)\)'
    matches = re.findall(table_pattern, content)
    for match in matches:
        drug_name = match[0].strip()
        specification = match[1].strip()
        drug_id = match[2].strip()
        url = match[3].strip()
        
        # 清理药品名称
        clean_name = re.sub(r'[※▲\(\)（）]', '', drug_name).strip()
        
        drug_urls[clean_name] = {
            'name': drug_name,
            'id': drug_id,
            'url': url
        }
    
    # 方法2: 匹配格式: 药品名称 https://www.hnysfww.com/goods.php?id=XXX
    list_pattern = r'-\s+([^\n]+?)\s+(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    matches = re.findall(list_pattern, content)
    for match in matches:
        drug_name = match[0].strip()
        url = match[1].strip()
        
        # 清理药品名称
        clean_name = re.sub(r'[※▲\(\)（）]', '', drug_name).strip()
        
        if clean_name not in drug_urls:
            drug_urls[clean_name] = {
                'name': drug_name,
                'id': None,
                'url': url
            }
    
    # 方法3: 匹配格式: 药品名称 [ID: XXX] https://...
    id_pattern = r'([^\n]+?)\s*\[ID:\s*(\d+)\]\s*(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    matches = re.findall(id_pattern, content)
    for match in matches:
        drug_name = match[0].strip()
        drug_id = match[1].strip()
        url = match[2].strip()
        
        # 清理药品名称
        clean_name = re.sub(r'[※▲\(\)（）]', '', drug_name).strip()
        
        drug_urls[clean_name] = {
            'name': drug_name,
            'id': drug_id,
            'url': url
        }
    
    return drug_urls

def load_drugs_index():
    """加载药品索引"""
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_drug(drug_id):
    """加载药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    if not drug_file.exists():
        return None
    with open(drug_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_drug(drug_id, drug_data):
    """保存药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    with open(drug_file, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)

def update_drug_url(drug_id, drug_name, url):
    """更新单个药品的URL"""
    drug_data = load_drug(drug_id)
    
    if not drug_data:
        return False, "文件不存在"
    
    # 检查是否已有URL
    existing_url = drug_data.get('url', {})
    if existing_url.get('hnysfww') == url:
        return False, "URL已存在且相同"
    
    # 更新URL
    drug_data['url'] = {
        'hnysfww': url,
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    }
    
    # 保存文件
    save_drug(drug_id, drug_data)
    
    return True, "更新成功"

def update_supplemented_file(updates):
    """更新已补充药品网址.txt文件"""
    if not updates:
        return
    
    # 读取现有内容
    if SUPPLEMENTED_FILE.exists():
        with open(SUPPLEMENTED_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # 找到当前最大序号
    serial_pattern = r'(\d+)\.\s+.+\(ID:'
    existing_serials = re.findall(serial_pattern, content)
    max_serial = max([int(s) for s in existing_serials]) if existing_serials else 0
    
    # 准备新条目
    new_entries = []
    for i, update in enumerate(updates, 1):
        entry = f"{max_serial + i}. {update['name']} (ID: {update['id']})\n"
        entry += f"   网址: {update['url']}\n"
        entry += f"   补充日期: {datetime.now().strftime('%Y-%m-%d')}\n"
        new_entries.append(entry)
    
    new_entries_text = "\n".join(new_entries) + "\n"
    
    # 找到统计信息的位置
    stats_pattern = r'================================================================================\n统计信息\n================================================================================'
    stats_match = re.search(stats_pattern, content)
    
    if stats_match:
        # 在统计信息之前插入新条目
        insert_pos = stats_match.start()
        content = content[:insert_pos] + new_entries_text + content[insert_pos:]
    else:
        # 追加到文件末尾
        content = content + "\n" + new_entries_text
    
    # 更新统计信息
    current_count = len(re.findall(r'^\d+\.\s+.+\(ID:', content, re.MULTILINE))
    stats_pattern = r'总补充药品数: \d+个'
    content = re.sub(stats_pattern, f'总补充药品数: {current_count}个', content)
    
    # 更新最后更新时间
    date_pattern = r'最后更新: \d{4}-\d{2}-\d{2}'
    content = re.sub(date_pattern, f'最后更新: {datetime.now().strftime("%Y-%m-%d")}', content)
    
    # 保存文件
    with open(SUPPLEMENTED_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """主函数"""
    print("=" * 80)
    print("从多个文档更新药品网址")
    print("=" * 80)
    
    # 从所有文档中提取网址
    all_drug_urls = {}
    for doc_file in DOC_FILES:
        print(f"\n正在解析: {doc_file.name}")
        drug_urls = parse_md_file(doc_file)
        print(f"  找到 {len(drug_urls)} 个药品网址记录")
        all_drug_urls.update(drug_urls)
    
    print(f"\n总计找到 {len(all_drug_urls)} 个唯一药品网址记录")
    
    # 加载药品索引
    drugs_index = load_drugs_index()
    
    # 创建药品名称到ID的映射
    name_to_id = {}
    id_to_name = {}
    for drug in drugs_index:
        name = drug['name']
        drug_id = drug['id']
        # 清理名称用于匹配
        clean_name = re.sub(r'[※▲\(\)（）]', '', name).strip()
        name_to_id[clean_name] = drug_id
        id_to_name[drug_id] = clean_name
    
    # 匹配并更新
    matched = []
    updated = []
    failed = []
    already_has = []
    
    print("\n开始匹配和更新...")
    
    for clean_name, info in all_drug_urls.items():
        drug_name = info['name']
        url = info['url']
        known_id = info.get('id')
        
        # 尝试匹配药品ID
        drug_id = None
        if known_id and known_id in id_to_name:
            drug_id = known_id
        elif clean_name in name_to_id:
            drug_id = name_to_id[clean_name]
        elif drug_name in name_to_id:
            drug_id = name_to_id[drug_name]
        
        if drug_id:
            matched.append({
                'id': drug_id,
                'name': drug_name,
                'url': url
            })
            
            # 检查药品当前状态
            drug_data = load_drug(drug_id)
            if drug_data:
                existing_url = drug_data.get('url', {})
                if existing_url.get('hnysfww'):
                    already_has.append({
                        'id': drug_id,
                        'name': drug_name,
                        'url': url
                    })
                    continue
            
            # 更新药品文件
            success, message = update_drug_url(drug_id, drug_name, url)
            if success:
                updated.append({
                    'id': drug_id,
                    'name': drug_name,
                    'url': url
                })
                print(f"✓ ID {drug_id}: {drug_name}")
            else:
                failed.append({
                    'id': drug_id,
                    'name': drug_name,
                    'reason': message
                })
                if "已存在" not in message:
                    print(f"✗ ID {drug_id}: {drug_name} - {message}")
    
    # 更新已补充药品网址.txt
    print("\n更新已补充药品网址.txt...")
    update_supplemented_file(updated)
    
    # 输出统计
    print("\n" + "=" * 80)
    print("更新统计")
    print("=" * 80)
    print(f"文档中找到: {len(all_drug_urls)} 个")
    print(f"成功匹配: {len(matched)} 个")
    print(f"成功更新: {len(updated)} 个")
    print(f"已有网址: {len(already_has)} 个")
    print(f"更新失败: {len(failed)} 个")
    
    if updated:
        print("\n已更新的药品(前30个):")
        for item in updated[:30]:
            print(f"  - ID {item['id']}: {item['name']}")
        if len(updated) > 30:
            print(f"  ... 还有 {len(updated) - 30} 个")
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()
