#!/usr/bin/env python3
"""
从"仍缺少网址的药品清单_最新.md"中提取所有网址
更新到对应的药品JSON文件中
"""

import json
import re
from pathlib import Path
from datetime import datetime

# 项目路径
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_DIR = PROJECT_ROOT / "pharmacist-handbook" / "data" / "drugs"
LIST_FILE = PROJECT_ROOT / "output" / "仍缺少网址的药品清单_最新.md"

def parse_list_file():
    """解析清单文件，提取所有有网址的药品"""
    drug_urls = {}

    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配表格行，提取ID和网址
    # 格式: | 序号 | ID | 药品名称 | 剂型 | 备注 | 网址 |
    pattern = r'\|\s*\d+\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(https://[^\s|]+)\s*\|'
    matches = re.findall(pattern, content)

    for match in matches:
        drug_id = int(match[0].strip())
        name = match[1].strip()
        dosage_form = match[2].strip()
        url = match[4].strip()

        drug_urls[drug_id] = {
            'id': drug_id,
            'name': name,
            'dosage_form': dosage_form,
            'url': url
        }

    return drug_urls

def load_drug_json(drug_id):
    """加载药品JSON文件"""
    json_file = DATA_DIR / f"{drug_id}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_drug_json(drug_id, data):
    """保存药品JSON文件"""
    json_file = DATA_DIR / f"{drug_id}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_drug_url(drug_id, url, drug_info):
    """更新药品的URL"""
    drug_data = load_drug_json(drug_id)
    if not drug_data:
        return False, "no_json"

    # 检查是否已有URL
    existing_url = drug_data.get('url', {}).get('hnysfww', '')
    if existing_url:
        return True, "has_url"

    # 更新URL
    if 'url' not in drug_data:
        drug_data['url'] = {}

    drug_data['url']['hnysfww'] = url

    # 保存
    save_drug_json(drug_id, drug_data)
    return True, "updated"

def main():
    print("=" * 80)
    print("从清单文件更新所有药品网址")
    print("=" * 80)

    # 解析清单文件
    print("\n解析清单文件...")
    drug_urls = parse_list_file()
    print(f"  找到 {len(drug_urls)} 个有网址的药品")

    # 更新所有药品
    print(f"\n开始更新网址...")

    updated_count = 0
    skip_count = 0
    not_found_count = 0

    for drug_id in sorted(drug_urls.keys()):
        drug_info = drug_urls[drug_id]

        success, status = update_drug_url(drug_id, drug_info['url'], drug_info)

        if status == "updated":
            print(f"  [更新] ID:{drug_id} {drug_info['name']} -> {drug_info['url']}")
            updated_count += 1
        elif status == "has_url":
            print(f"  [跳过] ID:{drug_id} {drug_info['name']} (已有网址)")
            skip_count += 1
        else:
            print(f"  [缺失] ID:{drug_id} {drug_info['name']} (无JSON文件)")
            not_found_count += 1

    print(f"\n{'=' * 80}")
    print("更新完成!")
    print(f"  - 成功更新: {updated_count}个")
    print(f"  - 跳过(已有网址): {skip_count}个")
    print(f"  - 无JSON文件: {not_found_count}个")
    print("=" * 80)

if __name__ == "__main__":
    main()
