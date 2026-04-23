#!/usr/bin/env python3
"""
手动更新剩余15个无网址但有内容的药品
"""

import json
from pathlib import Path

# 项目路径
DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 剩余的15个药品及其网址（从清单文件中提取）
REMAINING_DRUGS = {
    504: {"name": "板蓝根", "url": "https://www.hnysfww.com/goods.php?id=4088"},
    516: {"name": "参松养心", "url": "https://www.hnysfww.com/goods.php?id=6855"},
    525: {"name": "未确瑞基奥仑赛", "url": "https://www.hnysfww.com/goods.php?id=13214"},
    566: {"name": "托拉塞米", "url": "https://www.hnysfww.com/goods.php?id=1728"},
    717: {"name": "五酯", "url": "https://www.hnysfww.com/goods.php?id=8019"},
    719: {"name": "稳心", "url": "https://www.hnysfww.com/goods.php?id=6830"},
    763: {"name": "注射用头孢曲松钠", "url": "https://www.hnysfww.com/goods.php?id=1907"},
    856: {"name": "清咳平喘", "url": "https://www.hnysfww.com/goods.php?id=6254"},
    894: {"name": "天麻素", "url": "https://www.hnysfww.com/goods.php?id=737"},
    930: {"name": "宫血宁", "url": "https://www.hnysfww.com/goods.php?id=13214"},  # 需要确认
    944: {"name": "头孢拉定", "url": "https://www.hnysfww.com/goods.php?id=1886"},  # 需要确认
    972: {"name": "甲钴胺", "url": "https://www.hnysfww.com/goods.php?id=3075"},  # 需要确认
    977: {"name": "维生素B1", "url": "https://www.hnysfww.com/goods.php?id=3075"},  # 需要确认
    980: {"name": "头孢克洛", "url": "https://www.hnysfww.com/goods.php?id=1917"},  # 需要确认
    991: {"name": "阿莫西林", "url": "https://www.hnysfww.com/goods.php?id=1846"},  # 需要确认
}

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
        return False

    # 检查是否已有URL
    existing_url = drug_data.get('url', {}).get('hnysfww', '')
    if existing_url:
        print(f"  [跳过] ID:{drug_id} {name} (已有网址: {existing_url})")
        return True

    # 更新URL
    if 'url' not in drug_data:
        drug_data['url'] = {}

    drug_data['url']['hnysfww'] = url

    # 保存
    save_drug_json(drug_id, drug_data)
    print(f"  [更新] ID:{drug_id} {name} -> {url}")
    return True

def main():
    print("=" * 80)
    print("更新剩余15个无网址但有内容的药品")
    print("=" * 80)

    updated_count = 0
    skip_count = 0
    not_found_count = 0

    for drug_id in sorted(REMAINING_DRUGS.keys()):
        drug_info = REMAINING_DRUGS[drug_id]
        if update_drug_url(drug_id, drug_info['url'], drug_info['name']):
            updated_count += 1
        else:
            not_found_count += 1

    print(f"\n{'=' * 80}")
    print("更新完成!")
    print(f"  - 成功更新: {updated_count}个")
    print(f"  - 跳过(已有网址): {skip_count}个")
    print(f"  - 无JSON文件: {not_found_count}个")
    print("=" * 80)

if __name__ == "__main__":
    main()
