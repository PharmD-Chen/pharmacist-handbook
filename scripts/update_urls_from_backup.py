#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从drugs_without_manual.txt中提取网址并更新到药品JSON文件中
"""

import json
import re
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"
BACKUP_FILE = PROJECT_ROOT / "pharmacist-handbook/data/backup/drugs_without_manual.txt"
SUPPLEMENTED_FILE = PROJECT_ROOT / "已补充药品网址.txt"

def parse_drugs_without_manual():
    """解析drugs_without_manual.txt文件，提取药品名称和网址"""
    drug_urls = {}
    
    with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配格式: 序号. 药品名称 | 剂型 | 规格信息 https://www.hnysfww.com/goods.php?id=XXX
    pattern = r'\d+\.\s+(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    
    matches = re.findall(pattern, content)
    
    for match in matches:
        drug_name = match[0].strip()
        dosage_form = match[1].strip()
        specification = match[2].strip()
        url = match[3].strip()
        
        # 清理药品名称（去除特殊标记）
        clean_name = re.sub(r'[※▲\(\)（）]', '', drug_name).strip()
        
        drug_urls[clean_name] = {
            'name': drug_name,
            'dosage_form': dosage_form,
            'specification': specification,
            'url': url
        }
    
    return drug_urls

def load_drugs_index():
    """加载药品索引"""
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def update_drug_url(drug_id, drug_name, url):
    """更新单个药品的URL"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    
    if not drug_file.exists():
        return False, "文件不存在"
    
    try:
        with open(drug_file, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
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
        with open(drug_file, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        return True, "更新成功"
        
    except Exception as e:
        return False, f"错误: {str(e)}"

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
    
    # 找到统计信息的位置
    stats_pattern = r'================================================================================\n统计信息\n================================================================================'
    stats_match = re.search(stats_pattern, content)
    
    # 准备新条目
    new_entries = []
    for update in updates:
        entry = f"{update['serial']}. {update['name']} (ID: {update['id']})\n"
        entry += f"   网址: {update['url']}\n"
        entry += f"   补充日期: {datetime.now().strftime('%Y-%m-%d')}\n"
        new_entries.append(entry)
    
    new_entries_text = "\n".join(new_entries) + "\n"
    
    if stats_match:
        # 在统计信息之前插入新条目
        insert_pos = stats_match.start()
        content = content[:insert_pos] + new_entries_text + content[insert_pos:]
    else:
        # 追加到文件末尾
        content = content + "\n" + new_entries_text
    
    # 更新统计信息
    # 计算新的总数
    current_count = len(re.findall(r'^\d+\.\s+.+\(ID:', content, re.MULTILINE))
    
    # 更新统计信息
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
    print("从备份文件更新药品网址")
    print("=" * 80)
    
    # 解析备份文件
    print("\n正在解析备份文件...")
    drug_urls = parse_drugs_without_manual()
    print(f"找到 {len(drug_urls)} 个药品网址记录")
    
    # 加载药品索引
    drugs_index = load_drugs_index()
    
    # 创建药品名称到ID的映射
    name_to_id = {}
    for drug in drugs_index:
        name = drug['name']
        # 清理名称用于匹配
        clean_name = re.sub(r'[※▲\(\)（）]', '', name).strip()
        name_to_id[clean_name] = drug['id']
        # 同时保存原始名称
        name_to_id[name] = drug['id']
    
    # 匹配并更新
    matched = []
    updated = []
    failed = []
    
    print("\n开始匹配和更新...")
    
    for clean_name, info in drug_urls.items():
        drug_name = info['name']
        url = info['url']
        
        # 尝试匹配药品ID
        drug_id = None
        if clean_name in name_to_id:
            drug_id = name_to_id[clean_name]
        elif drug_name in name_to_id:
            drug_id = name_to_id[drug_name]
        
        if drug_id:
            matched.append({
                'id': drug_id,
                'name': drug_name,
                'url': url
            })
            
            # 更新药品文件
            success, message = update_drug_url(drug_id, drug_name, url)
            if success:
                updated.append({
                    'id': drug_id,
                    'name': drug_name,
                    'url': url
                })
                print(f"✓ ID {drug_id}: {drug_name} - {message}")
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
    
    # 获取当前序号
    current_serial = 718  # 从现有记录数开始
    updates_for_file = []
    for i, update in enumerate(updated, 1):
        updates_for_file.append({
            'serial': current_serial + i,
            'id': update['id'],
            'name': update['name'],
            'url': update['url']
        })
    
    update_supplemented_file(updates_for_file)
    
    # 输出统计
    print("\n" + "=" * 80)
    print("更新统计")
    print("=" * 80)
    print(f"备份文件中记录: {len(drug_urls)} 个")
    print(f"成功匹配: {len(matched)} 个")
    print(f"成功更新: {len(updated)} 个")
    print(f"更新失败: {len(failed)} 个")
    
    if failed:
        print("\n失败的药品:")
        for item in failed:
            print(f"  - ID {item['id']}: {item['name']} - {item['reason']}")
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()
