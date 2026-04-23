#!/usr/bin/env python3
"""
更新63个无网址且无内容的药品网址
从"仍缺少网址的药品清单_最新.md"中提取网址
"""

import json
import re
from pathlib import Path

# 项目路径
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_DIR = PROJECT_ROOT / "pharmacist-handbook" / "data" / "drugs"
LIST_FILE = PROJECT_ROOT / "output" / "仍缺少网址的药品清单_最新.md"

# 63个目标药品ID
TARGET_IDS = [473, 531, 543, 553, 561, 573, 577, 583, 590, 597, 605, 632, 643, 646, 652, 654, 667, 672, 683, 687, 692, 697, 699, 723, 730, 732, 750, 758, 769, 783]

def parse_list_file():
    """解析清单文件，提取所有有网址的药品"""
    drug_urls = {}

    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配表格行，提取ID和网址
    # 格式: | 序号 | ID | 药品名称 | 剂型 | 备注 | 网址
    pattern = r'\|\s*\d+\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(https://[^\s|]+)'
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

def update_drug_url(drug_id, url, name):
    """更新药品的URL"""
    drug_data = load_drug_json(drug_id)
    if not drug_data:
        print(f"  [缺失] ID:{drug_id} {name} (无JSON文件)")
        return False, "no_json"

    # 检查是否已有URL
    existing_url = drug_data.get('url', {}).get('hnysfww', '')
    if existing_url:
        print(f"  [跳过] ID:{drug_id} {name} (已有网址)")
        return True, "has_url"

    # 更新URL
    if 'url' not in drug_data:
        drug_data['url'] = {}

    drug_data['url']['hnysfww'] = url

    # 保存
    save_drug_json(drug_id, drug_data)
    print(f"  [更新] ID:{drug_id} {name} -> {url}")
    return True, "updated"

def main():
    print("=" * 80)
    print("更新63个无网址且无内容的药品")
    print("=" * 80)

    # 解析清单文件
    print("\n解析清单文件...")
    drug_urls = parse_list_file()
    print(f"  找到 {len(drug_urls)} 个有网址的药品")

    # 更新目标药品
    print(f"\n检查 {len(TARGET_IDS)} 个目标药品...")

    updated_count = 0
    skip_count = 0
    not_found_count = 0
    no_url_in_list = 0

    for drug_id in TARGET_IDS:
        if drug_id in drug_urls:
            drug_info = drug_urls[drug_id]
            success, status = update_drug_url(drug_id, drug_info['url'], drug_info['name'])

            if status == "updated":
                updated_count += 1
            elif status == "has_url":
                skip_count += 1
            else:
                not_found_count += 1
        else:
            print(f"  [清单无网址] ID:{drug_id}")
            no_url_in_list += 1

    print(f"\n{'=' * 80}")
    print("更新完成!")
    print(f"  - 成功更新: {updated_count}个")
    print(f"  - 跳过(已有网址): {skip_count}个")
    print(f"  - 无JSON文件: {not_found_count}个")
    print(f"  - 清单中无网址: {no_url_in_list}个")
    print("=" * 80)

if __name__ == "__main__":
    main()
