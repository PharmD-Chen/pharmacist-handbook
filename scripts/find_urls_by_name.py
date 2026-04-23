#!/usr/bin/env python3
"""
通过药品名称匹配，查找在报告中缺少网址但在文档中已有网址的药品
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

# 项目路径
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
REPORT_FILE = PROJECT_DIR / 'output' / 'drug_url_check_report.txt'
DOC_FILE = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'backup' / 'drugs_without_manual.txt'

def extract_missing_drugs_from_report():
    """从报告中提取缺少网址的药品"""
    missing_drugs = {}

    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配模式: ID  XXX: 药品名称 - 缺少url字段
    pattern = r'ID\s+(\d+):\s+(.+?)\s+-\s+缺少url字段'
    matches = re.findall(pattern, content)

    for drug_id, drug_name in matches:
        missing_drugs[int(drug_id)] = drug_name.strip()

    return missing_drugs


def extract_all_urls_from_doc():
    """从文档中提取所有有网址的药品"""
    doc_drugs = []

    with open(DOC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配模式: 数字. 药品名称 | 剂型 | 规格 https://www.hnysfww.com/goods.php?id=XXXX
    pattern = r'^(\d+)\.\s+([^|]+)\|[^|]+\|[^|]+https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
    matches = re.findall(pattern, content, re.MULTILINE)

    for idx, drug_name, url_id in matches:
        doc_drugs.append({
            'line_num': int(idx),
            'name': drug_name.strip(),
            'url': f"https://www.hnysfww.com/goods.php?id={url_id}"
        })

    return doc_drugs


def similarity(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a, b).ratio()


def main():
    """主函数"""
    print("=" * 80)
    print("通过名称匹配查找可补充的网址")
    print("=" * 80)

    # 提取数据
    missing_drugs = extract_missing_drugs_from_report()
    doc_drugs = extract_all_urls_from_doc()

    print(f"\n报告中显示缺少网址的药品: {len(missing_drugs)} 个")
    print(f"文档中记录有网址的药品: {len(doc_drugs)} 个")

    # 通过名称匹配
    matched_drugs = []

    for drug_id, missing_name in missing_drugs.items():
        # 清理名称（移除特殊标记）
        clean_missing_name = re.sub(r'[※▲\(\)\[\]（）]', '', missing_name).strip()

        best_match = None
        best_score = 0

        for doc_drug in doc_drugs:
            clean_doc_name = re.sub(r'[※▲\(\)\[\]（）]', '', doc_drug['name']).strip()

            # 计算相似度
            score = similarity(clean_missing_name, clean_doc_name)

            # 如果名称完全包含或高度相似
            if score > 0.8 or clean_missing_name in clean_doc_name or clean_doc_name in clean_missing_name:
                if score > best_score:
                    best_score = score
                    best_match = doc_drug

        if best_match and best_score > 0.5:
            matched_drugs.append({
                'id': drug_id,
                'name': missing_name,
                'matched_name': best_match['name'],
                'url': best_match['url'],
                'similarity': best_score
            })

    print(f"\n找到匹配的药品: {len(matched_drugs)} 个")
    print("=" * 80)

    if matched_drugs:
        # 按相似度排序
        matched_drugs.sort(key=lambda x: x['similarity'], reverse=True)

        print("\n匹配结果（前30个）:\n")
        for drug in matched_drugs[:30]:
            print(f"ID {drug['id']:>4}: {drug['name']:<35}")
            print(f"       匹配: {drug['matched_name']:<35} (相似度: {drug['similarity']:.2f})")
            print(f"       网址: {drug['url']}")
            print()

        # 保存到文件
        output_file = PROJECT_DIR / 'output' / 'matched_urls_from_doc.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("通过名称匹配找到的网址\n")
            f.write("=" * 80 + "\n\n")
            for drug in matched_drugs:
                f.write(f"ID {drug['id']}: {drug['name']}\n")
                f.write(f"  匹配文档中的: {drug['matched_name']}\n")
                f.write(f"  相似度: {drug['similarity']:.2f}\n")
                f.write(f"  网址: {drug['url']}\n\n")

        print(f"详细列表已保存到: {output_file}")

        # 询问是否更新
        print("\n是否要将这些网址更新到药品JSON文件中?")
        print("运行: python3 scripts/update_matched_urls.py")

    else:
        print("\n没有找到匹配的网址")


if __name__ == '__main__':
    main()
