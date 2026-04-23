#!/usr/bin/env python3
"""
查找在 drug_url_check_report.txt 中显示缺少网址，
但在 drugs_without_manual.txt 中实际上已有网址的药品
"""

import re
from pathlib import Path

# 项目路径
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
REPORT_FILE = PROJECT_DIR / 'output' / 'drug_url_check_report.txt'
DOC_FILE = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'backup' / 'drugs_without_manual.txt'

def extract_missing_ids_from_report():
    """从报告中提取缺少网址的药品ID"""
    missing_ids = {}

    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配模式: ID  XXX: 药品名称 - 缺少url字段
    pattern = r'ID\s+(\d+):\s+(.+?)\s+-\s+缺少url字段'
    matches = re.findall(pattern, content)

    for drug_id, drug_name in matches:
        missing_ids[int(drug_id)] = drug_name.strip()

    return missing_ids


def extract_urls_from_doc():
    """从文档中提取药品ID和网址"""
    urls_map = {}

    with open(DOC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配模式: 数字. 药品名称 | 剂型 | 规格 https://www.hnysfww.com/goods.php?id=XXXX
    pattern = r'^(\d+)\.\s+([^|]+)\|[^|]+\|[^|]+https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
    matches = re.findall(pattern, content, re.MULTILINE)

    for idx, drug_name, url_id in matches:
        # 文档中的行号对应药品ID（通常是行号）
        drug_id = int(idx)
        urls_map[drug_id] = {
            'name': drug_name.strip(),
            'url': f"https://www.hnysfww.com/goods.php?id={url_id}"
        }

    return urls_map


def main():
    """主函数"""
    print("=" * 80)
    print("查找在报告中显示缺少网址，但在文档中已有网址的药品")
    print("=" * 80)

    # 提取数据
    missing_ids = extract_missing_ids_from_report()
    doc_urls = extract_urls_from_doc()

    print(f"\n报告中显示缺少网址的药品: {len(missing_ids)} 个")
    print(f"文档中记录有网址的药品: {len(doc_urls)} 个")

    # 找出差异
    found_in_doc = []

    for drug_id, drug_name in missing_ids.items():
        if drug_id in doc_urls:
            found_in_doc.append({
                'id': drug_id,
                'name': drug_name,
                'url': doc_urls[drug_id]['url']
            })

    print(f"\n在文档中找到网址的药品: {len(found_in_doc)} 个")
    print("=" * 80)

    if found_in_doc:
        print("\n这些药品可以补充网址:\n")
        for drug in found_in_doc[:50]:  # 显示前50个
            print(f"ID {drug['id']:>4}: {drug['name']:<40} -> {drug['url']}")

        if len(found_in_doc) > 50:
            print(f"\n... 还有 {len(found_in_doc) - 50} 个药品")

        # 保存到文件
        output_file = PROJECT_DIR / 'output' / 'urls_found_in_doc.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("在 drugs_without_manual.txt 中找到的网址\n")
            f.write("=" * 80 + "\n\n")
            for drug in found_in_doc:
                f.write(f"ID {drug['id']}: {drug['name']}\n")
                f.write(f"  网址: {drug['url']}\n\n")

        print(f"\n详细列表已保存到: {output_file}")
    else:
        print("\n没有找到可以补充的网址")


if __name__ == '__main__':
    main()
