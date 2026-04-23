#!/usr/bin/env python3
"""
检查药品手册内容和网址情况
生成全面的统计报告
"""

import json
from pathlib import Path
from datetime import datetime

# 项目路径
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_DIR = PROJECT_ROOT / "pharmacist-handbook" / "data" / "drugs"
OUTPUT_DIR = PROJECT_ROOT / "output"

def load_index():
    """加载药品索引"""
    index_file = DATA_DIR / "index.json"
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_drug_json(drug_id):
    """加载单个药品JSON"""
    json_file = DATA_DIR / f"{drug_id}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def check_drug_status(drug):
    """检查单个药品的状态"""
    drug_id = drug['id']
    name = drug['name']
    dosage_form = drug.get('dosage_form', '')

    drug_data = load_drug_json(drug_id)

    if not drug_data:
        return {
            'id': drug_id,
            'name': name,
            'dosage_form': dosage_form,
            'has_json': False,
            'has_url': False,
            'has_manual': False,
            'manual_fields': []
        }

    # 检查URL
    has_url = bool(drug_data.get('url', {}).get('hnysfww'))
    url = drug_data.get('url', {}).get('hnysfww', '')

    # 检查手册内容
    manual = drug_data.get('manual', {})

    # 检查详细版字段
    detail_fields = [
        'full_indications',
        'full_dosage',
        'full_contraindications',
        'full_adverse_reactions',
        'full_precautions',
        'full_pharmacokinetics',
        'full_interactions'
    ]

    # 检查精简版字段
    simple_fields = [
        'indications',
        'dosage',
        'contraindications',
        'adverse_reactions',
        'precautions',
        'pharmacokinetics',
        'interactions',
        'pregnancy_category'
    ]

    has_full_indications = bool(manual.get('full_indications'))
    has_simple_indications = bool(manual.get('indications'))

    # 统计完整字段数
    detail_count = sum(1 for f in detail_fields if manual.get(f))
    simple_count = sum(1 for f in simple_fields if manual.get(f))

    return {
        'id': drug_id,
        'name': name,
        'dosage_form': dosage_form,
        'has_json': True,
        'has_url': has_url,
        'url': url,
        'has_manual': has_full_indications or has_simple_indications,
        'has_full_content': has_full_indications,
        'has_simple_content': has_simple_indications,
        'detail_fields_count': detail_count,
        'simple_fields_count': simple_count,
        'types': drug.get('types', [])
    }

def categorize_drugs(results):
    """分类药品"""
    categories = {
        'with_url_and_content': [],      # 有网址有内容
        'with_url_no_content': [],       # 有网址无内容
        'no_url_with_content': [],       # 无网址有内容
        'no_url_no_content': [],         # 无网址无内容
        'no_json': []                     # 无JSON文件
    }

    for result in results:
        if not result['has_json']:
            categories['no_json'].append(result)
        elif result['has_url'] and result['has_full_content']:
            categories['with_url_and_content'].append(result)
        elif result['has_url'] and not result['has_full_content']:
            categories['with_url_no_content'].append(result)
        elif not result['has_url'] and result['has_full_content']:
            categories['no_url_with_content'].append(result)
        else:
            categories['no_url_no_content'].append(result)

    return categories

def generate_report(categories, total_count):
    """生成检查报告"""

    today = datetime.now().strftime('%Y-%m-%d')

    # 计算统计信息
    with_url = len(categories['with_url_and_content']) + len(categories['with_url_no_content'])
    with_content = len(categories['with_url_and_content']) + len(categories['no_url_with_content'])
    complete = len(categories['with_url_and_content'])

    report = f"""# 药品手册内容和网址情况检查报告

**生成日期**: {today}

## 一、总体统计

| 指标 | 数量 | 占比 |
|------|-----|------|
| **总药品数** | {total_count} | 100% |
| **有网址** | {with_url} | {with_url/total_count*100:.1f}% |
| **有完整内容** | {with_content} | {with_content/total_count*100:.1f}% |
| **网址+内容完整** | {complete} | {complete/total_count*100:.1f}% |

## 二、分类详情

### 1. 有网址且有完整内容 ✅ ({len(categories['with_url_and_content'])}个)

这些药品已完成所有信息补充，包括网址和精简版/详细版手册内容。

| ID | 药品名称 | 剂型 | 网址 |
|----|---------|------|------|
"""

    for drug in sorted(categories['with_url_and_content'], key=lambda x: x['id'])[:50]:  # 只显示前50个
        url_short = drug['url'][:50] + '...' if len(drug['url']) > 50 else drug['url']
        report += f"| {drug['id']} | {drug['name']} | {drug['dosage_form']} | [链接]({drug['url']}) |\n"

    if len(categories['with_url_and_content']) > 50:
        report += f"\n... 还有 {len(categories['with_url_and_content']) - 50} 个药品\n"

    report += f"""

### 2. 有网址但无完整内容 ⚠️ ({len(categories['with_url_no_content'])}个)

这些药品有网址，但尚未提取详细内容。需要运行脚本补充内容。

| ID | 药品名称 | 剂型 | 网址 |
|----|---------|------|------|
"""

    for drug in sorted(categories['with_url_no_content'], key=lambda x: x['id']):
        report += f"| {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['url']} |\n"

    report += f"""

### 3. 无网址但有内容 ⚠️ ({len(categories['no_url_with_content'])}个)

这些药品有手册内容，但缺少湖南药事服务网网址。需要补充网址。

| ID | 药品名称 | 剂型 |
|----|---------|------|
"""

    for drug in sorted(categories['no_url_with_content'], key=lambda x: x['id']):
        report += f"| {drug['id']} | {drug['name']} | {drug['dosage_form']} |\n"

    report += f"""

### 4. 无网址且无内容 ❌ ({len(categories['no_url_no_content'])}个)

这些药品既无网址也无手册内容，需要优先处理。

| ID | 药品名称 | 剂型 | 类型 |
|----|---------|------|------|
"""

    for drug in sorted(categories['no_url_no_content'], key=lambda x: x['id'])[:30]:  # 只显示前30个
        types = ','.join(drug.get('types', []))
        report += f"| {drug['id']} | {drug['name']} | {drug['dosage_form']} | {types} |\n"

    if len(categories['no_url_no_content']) > 30:
        report += f"\n... 还有 {len(categories['no_url_no_content']) - 30} 个药品\n"

    report += f"""

### 5. 无JSON文件 ❌ ({len(categories['no_json'])}个)

这些药品在索引中存在，但没有对应的JSON文件。

| ID | 药品名称 | 剂型 |
|----|---------|------|
"""

    for drug in sorted(categories['no_json'], key=lambda x: x['id']):
        report += f"| {drug['id']} | {drug['name']} | {drug['dosage_form']} |\n"

    report += f"""

## 三、优先处理建议

### 高优先级（无网址无内容）
需要到湖南药事服务网搜索并补充：
1. 先补充网址
2. 再提取详细内容生成精简版

### 中优先级（有网址无内容）
运行以下命令自动补充内容：
```bash
cd /Users/chenheng/Projects_AI/Project_Pharmacist
python3 scripts/process_missing_url_list.py
```

### 低优先级（无网址有内容）
查找并补充湖南药事服务网网址，确保内容来源可追溯。

---

*报告生成时间: {today}*
"""

    return report

def main():
    print("=" * 80)
    print("检查药品手册内容和网址情况")
    print("=" * 80)

    # 加载索引
    print("\n加载药品索引...")
    index = load_index()
    total_count = len(index)
    print(f"  总药品数: {total_count}")

    # 检查每个药品
    print("\n检查每个药品状态...")
    results = []
    for i, drug in enumerate(index, 1):
        if i % 100 == 0:
            print(f"  已检查: {i}/{total_count}")
        result = check_drug_status(drug)
        results.append(result)

    # 分类
    print("\n分类统计...")
    categories = categorize_drugs(results)

    print(f"\n统计结果:")
    print(f"  ✅ 有网址有内容: {len(categories['with_url_and_content'])}个")
    print(f"  ⚠️  有网址无内容: {len(categories['with_url_no_content'])}个")
    print(f"  ⚠️  无网址有内容: {len(categories['no_url_with_content'])}个")
    print(f"  ❌ 无网址无内容: {len(categories['no_url_no_content'])}个")
    print(f"  ❌ 无JSON文件: {len(categories['no_json'])}个")

    # 生成报告
    print("\n生成检查报告...")
    report = generate_report(categories, total_count)

    # 保存报告
    report_file = OUTPUT_DIR / "药品手册内容和网址检查报告.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"  报告已保存: {report_file}")

    print("\n" + "=" * 80)
    print("检查完成!")
    print("=" * 80)

if __name__ == "__main__":
    main()
