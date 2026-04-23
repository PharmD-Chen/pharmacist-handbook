#!/usr/bin/env python3
"""
从"仍缺少网址的药品清单_最新.md"中提取网址
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
    """解析清单文件，提取有网址的药品"""
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
        url = match[4].strip()

        drug_urls[drug_id] = {
            'id': drug_id,
            'name': name,
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
        print(f"  警告: 找不到药品JSON文件: {drug_id}.json")
        return False

    # 检查是否已有URL
    existing_url = drug_data.get('url', {}).get('hnysfww', '')
    if existing_url:
        print(f"  已有网址，跳过: {drug_info['name']}")
        return True

    # 更新URL
    if 'url' not in drug_data:
        drug_data['url'] = {}

    drug_data['url']['hnysfww'] = url

    # 保存
    save_drug_json(drug_id, drug_data)
    print(f"  成功更新网址: {drug_info['name']} -> {url}")
    return True

def main():
    print("=" * 80)
    print("从清单文件更新药品网址")
    print("=" * 80)

    # 解析清单文件
    print("\n解析清单文件...")
    drug_urls = parse_list_file()
    print(f"  找到 {len(drug_urls)} 个有网址的药品")

    # 需要更新的21个药品ID（无网址但有内容）
    target_ids = [372, 441, 504, 516, 525, 566, 636, 660, 717, 719, 763, 764, 841, 856, 894, 930, 944, 972, 977, 980, 991]

    print(f"\n检查 {len(target_ids)} 个目标药品...")

    updated_count = 0
    skip_count = 0
    not_found_count = 0

    for drug_id in target_ids:
        if drug_id in drug_urls:
            drug_info = drug_urls[drug_id]
            print(f"\n[{drug_id}] {drug_info['name']}")

            if update_drug_url(drug_id, drug_info['url'], drug_info):
                updated_count += 1
            else:
                not_found_count += 1
        else:
            print(f"\n[{drug_id}] 在清单中未找到网址")
            not_found_count += 1

    print(f"\n{'=' * 80}")
    print("更新完成!")
    print(f"  - 成功更新: {updated_count}个")
    print(f"  - 跳过(已有网址): {skip_count}个")
    print(f"  - 未找到: {not_found_count}个")
    print("=" * 80)

if __name__ == "__main__":
    main()
