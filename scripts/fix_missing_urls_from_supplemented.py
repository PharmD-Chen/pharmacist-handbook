#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从已补充药品网址.txt中提取网址并更新到药品JSON文件中
修复之前未正确更新的问题
"""

import json
import re
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"
SUPPLEMENTED_FILE = PROJECT_ROOT / "已补充药品网址.txt"

def parse_supplemented_file():
    """解析已补充药品网址.txt文件，提取药品ID和网址"""
    drug_urls = {}
    
    if not SUPPLEMENTED_FILE.exists():
        print(f"文件不存在: {SUPPLEMENTED_FILE}")
        return drug_urls
    
    with open(SUPPLEMENTED_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配格式: 序号. 药品名称 (ID: XXX)
    #    网址: https://www.hnysfww.com/goods.php?id=XXX
    pattern = r'\d+\.\s+(.+?)\s*\(ID:\s*(\d+)\)\s*\n\s*网址:\s*(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    
    matches = re.findall(pattern, content)
    for match in matches:
        drug_name = match[0].strip()
        drug_id = match[1].strip()
        url = match[2].strip()
        
        drug_urls[drug_id] = {
            'name': drug_name,
            'url': url
        }
    
    return drug_urls

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

def main():
    """主函数"""
    print("=" * 80)
    print("从已补充药品网址.txt修复药品网址")
    print("=" * 80)
    
    # 解析已补充药品网址.txt文件
    print("\n正在解析已补充药品网址.txt文件...")
    drug_urls = parse_supplemented_file()
    print(f"找到 {len(drug_urls)} 个药品网址记录")
    
    # 统计
    updated = []
    already_has = []
    failed = []
    
    print("\n开始更新...")
    
    for drug_id, info in drug_urls.items():
        drug_name = info['name']
        url = info['url']
        
        # 检查药品当前状态
        drug_data = load_drug(drug_id)
        if not drug_data:
            failed.append({
                'id': drug_id,
                'name': drug_name,
                'reason': '文件不存在'
            })
            continue
        
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
    
    # 输出统计
    print("\n" + "=" * 80)
    print("更新统计")
    print("=" * 80)
    print(f"文件中记录: {len(drug_urls)} 个")
    print(f"成功更新: {len(updated)} 个")
    print(f"已有网址: {len(already_has)} 个")
    print(f"更新失败: {len(failed)} 个")
    
    if updated:
        print("\n已更新的药品(前30个):")
        for item in updated[:30]:
            print(f"  - ID {item['id']}: {item['name']}")
        if len(updated) > 30:
            print(f"  ... 还有 {len(updated) - 30} 个")
    
    if failed:
        print("\n失败的药品:")
        for item in failed:
            print(f"  - ID {item['id']}: {item['name']} - {item['reason']}")
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()
