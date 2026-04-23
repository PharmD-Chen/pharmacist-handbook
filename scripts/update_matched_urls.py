#!/usr/bin/env python3
"""
将匹配到的网址更新到药品JSON文件中
"""

import json
import re
from pathlib import Path
from difflib import SequenceMatcher

# 项目路径
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'
REPORT_FILE = PROJECT_DIR / 'output' / 'drug_url_check_report.txt'
DOC_FILE = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'backup' / 'drugs_without_manual.txt'

def extract_missing_drugs_from_report():
    """从报告中提取缺少网址的药品"""
    missing_drugs = {}

    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'ID\s+(\d+):\s+(.+?)\s+-\s+缺少url字段'
    matches = re.findall(pattern, content)

    for drug_id, drug_name in matches:
        missing_drugs[int(drug_id)] = drug_name.strip()

    return missing_drugs


def extract_all_urls_from_doc():
    """从文档中提取所有有网址的药品"""
    doc_drugs = {}

    with open(DOC_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'^(\d+)\.\s+([^|]+)\|[^|]+\|[^|]+https://www\.hnysfww\.com/goods\.php\?id=(\d+)'
    matches = re.findall(pattern, content, re.MULTILINE)

    for idx, drug_name, url_id in matches:
        doc_drugs[int(idx)] = {
            'name': drug_name.strip(),
            'url': f"https://www.hnysfww.com/goods.php?id={url_id}"
        }

    return doc_drugs


def similarity(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a, b).ratio()


def update_drug_url(drug_id, url):
    """更新药品JSON文件中的网址"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'

    if not drug_file.exists():
        return False, "文件不存在"

    try:
        with open(drug_file, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)

        # 更新网址
        if 'url' not in drug_data:
            drug_data['url'] = {}

        drug_data['url']['hnysfww'] = url
        drug_data['url']['last_updated'] = "2026-03-22"

        # 保存文件
        with open(drug_file, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)

        return True, "成功"

    except Exception as e:
        return False, str(e)


def main():
    """主函数"""
    print("=" * 80)
    print("更新匹配到的网址到药品JSON文件")
    print("=" * 80)

    # 提取数据
    missing_drugs = extract_missing_drugs_from_report()
    doc_drugs = extract_all_urls_from_doc()

    print(f"\n报告中显示缺少网址的药品: {len(missing_drugs)} 个")
    print(f"文档中记录有网址的药品: {len(doc_drugs)} 个")

    # 通过名称匹配
    matched_drugs = []

    for drug_id, missing_name in missing_drugs.items():
        clean_missing_name = re.sub(r'[※▲\(\)\[\]（）]', '', missing_name).strip()

        best_match = None
        best_score = 0

        for doc_id, doc_drug in doc_drugs.items():
            clean_doc_name = re.sub(r'[※▲\(\)\[\]（）]', '', doc_drug['name']).strip()

            score = similarity(clean_missing_name, clean_doc_name)

            if score > 0.8 or clean_missing_name in clean_doc_name or clean_doc_name in clean_missing_name:
                if score > best_score:
                    best_score = score
                    best_match = doc_drug

        if best_match and best_score > 0.5:
            matched_drugs.append({
                'id': drug_id,
                'name': missing_name,
                'url': best_match['url'],
                'similarity': best_score
            })

    print(f"\n找到匹配的药品: {len(matched_drugs)} 个")
    print("=" * 80)

    if not matched_drugs:
        print("没有找到可以更新的网址")
        return

    # 更新药品JSON文件
    updated_count = 0
    error_count = 0

    print("\n开始更新...")
    for drug in matched_drugs:
        success, msg = update_drug_url(drug['id'], drug['url'])
        if success:
            updated_count += 1
            print(f"✓ ID {drug['id']:>4}: {drug['name'][:30]:<30} -> {drug['url']}")
        else:
            error_count += 1
            print(f"✗ ID {drug['id']:>4}: {drug['name'][:30]:<30} - 错误: {msg}")

    print("\n" + "=" * 80)
    print("更新完成!")
    print("=" * 80)
    print(f"成功更新: {updated_count} 个药品")
    print(f"更新失败: {error_count} 个药品")

    # 更新已补充药品网址.txt文件
    print("\n正在更新 已补充药品网址.txt 文件...")

    supplemented_file = PROJECT_DIR / '已补充药品网址.txt'
    today = "2026-03-22"

    # 读取现有内容
    existing_entries = []
    if supplemented_file.exists():
        with open(supplemented_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取已有的药品ID
            existing_ids = set(re.findall(r'\(ID:\s*(\d+)\)', content))
    else:
        existing_ids = set()

    # 准备新条目
    new_entries = []
    for drug in matched_drugs:
        if str(drug['id']) not in existing_ids:
            new_entries.append(drug)

    if new_entries:
        # 追加到文件
        with open(supplemented_file, 'a', encoding='utf-8') as f:
            for drug in new_entries:
                f.write(f"\n{drug['name']} (ID: {drug['id']})\n")
                f.write(f"   网址: {drug['url']}\n")
                f.write(f"   补充日期: {today}\n")

        print(f"已向 已补充药品网址.txt 添加 {len(new_entries)} 个新条目")
    else:
        print("没有新条目需要添加到 已补充药品网址.txt")


if __name__ == '__main__':
    main()
