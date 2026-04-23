#!/usr/bin/env python3
"""
从多个文档文件中提取药品网址并更新到药品JSON文件中
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# 项目路径
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'

# 要读取的文档文件
DOC_FILES = [
    PROJECT_DIR / '缺少详细信息的药品列表.md',
    PROJECT_DIR / '药品网址汇总_backup.md',
    PROJECT_DIR / '药品网址汇总.md',
    PROJECT_DIR / '已补充药品网址.txt',
    PROJECT_DIR / '有网址但内容空缺的药品列表.md',
    PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'backup' / 'drugs_without_manual.txt',
]

def extract_urls_from_file(file_path):
    """从文件中提取药品ID和网址的映射关系"""
    urls_map = {}

    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return urls_map

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 匹配模式1: [ID: XXX] 后面跟着网址
        pattern1 = r'\[ID:\s*(\d+)\][^\n]*https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
        matches1 = re.findall(pattern1, content)
        for drug_id, url_id in matches1:
            urls_map[int(drug_id)] = f"https://www.hnysfww.com/goods.php?id={url_id}"

        # 匹配模式2: 行中包含ID和网址
        pattern2 = r'([^|\n]*)\|\s*(\d+)\s*\|[^|]*\|[^|]*\|[^|]*\|\s*https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
        matches2 = re.findall(pattern2, content)
        for _, drug_id, url_id in matches2:
            urls_map[int(drug_id)] = f"https://www.hnysfww.com/goods.php?id={url_id}"

        # 匹配模式3: 药品名称 (ID: XXX) 后面跟着网址
        pattern3 = r'\(ID:\s*(\d+)\)[^\n]*https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
        matches3 = re.findall(pattern3, content)
        for drug_id, url_id in matches3:
            urls_map[int(drug_id)] = f"https://www.hnysfww.com/goods.php?id={url_id}"

        # 匹配模式4: 数字编号开头，后面跟着药品名称和网址
        pattern4 = r'^\s*(\d+)\.\s+[^|]+\|[^|]+\|[^|]+\s+https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
        matches4 = re.findall(pattern4, content, re.MULTILINE)
        for drug_id, url_id in matches4:
            urls_map[int(drug_id)] = f"https://www.hnysfww.com/goods.php?id={url_id}"

        # 匹配模式5: 从文本中提取ID和网址（用于drugs_without_manual.txt）
        pattern5 = r'(\d+)\.\s+[^|]+\|[^|]+\|[^|]+https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
        matches5 = re.findall(pattern5, content)
        for drug_id, url_id in matches5:
            urls_map[int(drug_id)] = f"https://www.hnysfww.com/goods.php?id={url_id}"

        print(f"从 {file_path.name} 提取了 {len(urls_map)} 个网址")
        return urls_map

    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return urls_map


def get_all_urls_from_docs():
    """从所有文档中提取网址"""
    all_urls = {}

    for doc_file in DOC_FILES:
        urls = extract_urls_from_file(doc_file)
        all_urls.update(urls)

    print(f"\n总共提取了 {len(all_urls)} 个唯一网址")
    return all_urls


def update_drug_json_files(urls_map):
    """更新药品JSON文件中的网址"""
    updated_count = 0
    skipped_count = 0
    error_count = 0

    for drug_id, url in urls_map.items():
        drug_file = DRUGS_DIR / f'{drug_id}.json'

        if not drug_file.exists():
            print(f"药品文件不存在: {drug_file}")
            skipped_count += 1
            continue

        try:
            with open(drug_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)

            # 检查是否需要更新
            current_url = drug_data.get('url', {}).get('hnysfww', '')

            if current_url == url:
                skipped_count += 1
                continue

            # 更新网址
            if 'url' not in drug_data:
                drug_data['url'] = {}

            drug_data['url']['hnysfww'] = url

            # 保存文件
            with open(drug_file, 'w', encoding='utf-8') as f:
                json.dump(drug_data, f, ensure_ascii=False, indent=2)

            updated_count += 1
            print(f"已更新药品 {drug_id}: {url}")

        except Exception as e:
            print(f"更新药品 {drug_id} 时出错: {e}")
            error_count += 1

    return updated_count, skipped_count, error_count


def main():
    """主函数"""
    print("=" * 60)
    print("从文档中提取药品网址并更新到JSON文件")
    print("=" * 60)

    # 从所有文档中提取网址
    urls_map = get_all_urls_from_docs()

    if not urls_map:
        print("未找到任何网址信息")
        return

    # 显示前10个提取的网址
    print("\n提取的网址示例（前10个）:")
    for i, (drug_id, url) in enumerate(list(urls_map.items())[:10]):
        print(f"  药品ID {drug_id}: {url}")

    # 更新药品JSON文件
    print("\n" + "=" * 60)
    print("开始更新药品JSON文件...")
    print("=" * 60)

    updated, skipped, errors = update_drug_json_files(urls_map)

    print("\n" + "=" * 60)
    print("更新完成!")
    print("=" * 60)
    print(f"已更新: {updated} 个药品")
    print(f"已存在/跳过: {skipped} 个药品")
    print(f"错误: {errors} 个药品")


if __name__ == '__main__':
    main()
