#!/usr/bin/env python3
"""
更新已补充药品网址.txt文件，添加从文档中提取的网址
"""

import json
from pathlib import Path
from datetime import datetime

# 项目路径
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'
OUTPUT_FILE = PROJECT_DIR / '已补充药品网址.txt'

def get_drug_info(drug_id):
    """获取药品信息"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'

    if not drug_file.exists():
        return None, None

    try:
        with open(drug_file, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)

        name = drug_data.get('name', f'药品{drug_id}')
        url = drug_data.get('url', {}).get('hnysfww', '')

        return name, url
    except:
        return None, None


def main():
    """主函数"""
    print("=" * 60)
    print("更新已补充药品网址.txt文件")
    print("=" * 60)

    # 读取药品索引
    index_file = DRUGS_DIR / 'index.json'
    with open(index_file, 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)

    # 收集有网址的药品
    supplemented_drugs = []

    for drug in drugs_index:
        drug_id = drug['id']
        drug_name = drug['name']

        drug_file = DRUGS_DIR / f'{drug_id}.json'
        if not drug_file.exists():
            continue

        try:
            with open(drug_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)

            url = drug_data.get('url', {}).get('hnysfww', '')
            if url:
                supplemented_drugs.append({
                    'id': drug_id,
                    'name': drug_name,
                    'url': url
                })
        except:
            continue

    print(f"找到 {len(supplemented_drugs)} 个有网址的药品")

    # 生成文件内容
    today = datetime.now().strftime('%Y-%m-%d')

    content_lines = [
        "=" * 80,
        "已补充药品手册网址记录",
        "=" * 80,
        "",
        "本文件记录已从湖南药事服务网补充完整手册信息的药品",
        "",
        "=" * 80,
        "已补充药品列表",
        "=" * 80,
        "",
    ]

    for i, drug in enumerate(supplemented_drugs, 1):
        content_lines.append(f"{i}. {drug['name']} (ID: {drug['id']})")
        content_lines.append(f"   网址: {drug['url']}")
        content_lines.append(f"   补充日期: {today}")
        content_lines.append("")

    content_lines.extend([
        "=" * 80,
        "统计信息",
        "=" * 80,
        "",
        f"总补充药品数: {len(supplemented_drugs)}个",
        "",
        f"最后更新: {today}",
        "",
        "=" * 80,
    ])

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))

    print(f"\n已更新文件: {OUTPUT_FILE}")
    print(f"总共记录了 {len(supplemented_drugs)} 个药品的网址")


if __name__ == '__main__':
    main()
