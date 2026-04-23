#!/usr/bin/env python3
"""
更新仍缺少网址的药品清单
重新分析并区分有网址和无网址的药品
"""

import json
import re
from pathlib import Path
from datetime import datetime

# 项目路径
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_DIR = PROJECT_ROOT / "pharmacist-handbook" / "data" / "drugs"
OUTPUT_DIR = PROJECT_ROOT / "output"
LIST_FILE = OUTPUT_DIR / "仍缺少网址的药品清单_最新.md"

def load_drug_json(drug_id):
    """加载药品JSON文件"""
    json_file = DATA_DIR / f"{drug_id}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def parse_current_list():
    """解析当前的清单文件"""
    with open(LIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取西药部分
    western_drugs = []
    tcm_drugs = []

    # 匹配西药表格
    western_section = re.search(r'### 西药.*?\n\n(### 中成药|##)', content, re.DOTALL)
    if western_section:
        western_text = western_section.group(0)
        pattern = r'\|\s*\d+\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|'
        matches = re.findall(pattern, western_text)
        for match in matches:
            drug_id = int(match[0].strip())
            name = match[1].strip()
            dosage_form = match[2].strip()
            notes = match[3].strip()
            url = match[4].strip() if len(match) > 4 else ""

            western_drugs.append({
                'id': drug_id,
                'name': name,
                'dosage_form': dosage_form,
                'notes': notes,
                'url': url if url.startswith('http') else None
            })

    # 匹配中成药表格
    tcm_section = re.search(r'### 中成药.*?\n\n(## |---)', content, re.DOTALL)
    if tcm_section:
        tcm_text = tcm_section.group(0)
        pattern = r'\|\s*\d+\s*\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|'
        matches = re.findall(pattern, tcm_text)
        for match in matches:
            drug_id = int(match[0].strip())
            name = match[1].strip()
            dosage_form = match[2].strip()
            notes = match[3].strip()
            url = match[4].strip() if len(match) > 4 else ""

            tcm_drugs.append({
                'id': drug_id,
                'name': name,
                'dosage_form': dosage_form,
                'notes': notes,
                'url': url if url.startswith('http') else None
            })

    return western_drugs, tcm_drugs

def check_manual_completeness(drug_id):
    """检查药品手册内容完整性"""
    drug_data = load_drug_json(drug_id)
    if not drug_data:
        return False, False

    manual = drug_data.get('manual', {})
    has_url = bool(drug_data.get('url', {}).get('hnysfww'))
    has_content = bool(manual.get('full_indications'))

    return has_url, has_content

def generate_updated_list(western_drugs, tcm_drugs):
    """生成更新后的清单"""

    # 分类药品
    western_with_url_no_content = []
    western_with_url_with_content = []
    western_no_url = []

    tcm_with_url_no_content = []
    tcm_with_url_with_content = []
    tcm_no_url = []

    # 处理西药
    for drug in western_drugs:
        has_url, has_content = check_manual_completeness(drug['id'])
        if drug['url']:
            if has_content:
                western_with_url_with_content.append(drug)
            else:
                western_with_url_no_content.append(drug)
        else:
            western_no_url.append(drug)

    # 处理中成药
    for drug in tcm_drugs:
        has_url, has_content = check_manual_completeness(drug['id'])
        if drug['url']:
            if has_content:
                tcm_with_url_with_content.append(drug)
            else:
                tcm_with_url_no_content.append(drug)
        else:
            tcm_no_url.append(drug)

    return {
        'western_with_url_no_content': western_with_url_no_content,
        'western_with_url_with_content': western_with_url_with_content,
        'western_no_url': western_no_url,
        'tcm_with_url_no_content': tcm_with_url_no_content,
        'tcm_with_url_with_content': tcm_with_url_with_content,
        'tcm_no_url': tcm_no_url
    }

def write_updated_list(categories):
    """写入更新后的清单文件"""

    today = datetime.now().strftime('%Y-%m-%d')

    content = f"""# 仍缺少网址的药品清单（最新更新）

**生成日期**: {today}

## 统计信息

### 总体情况
- **总药品数**: 1032个
- **有湖南药事服务网网址**: 906个
- **缺少网址**: {len(categories['western_no_url']) + len(categories['tcm_no_url'])}个
- **覆盖率**: 87.8%

### 分类统计
| 类别 | 有网址有内容 | 有网址无内容 | 无网址 |
|------|-------------|-------------|--------|
| 西药 | {len(categories['western_with_url_with_content'])} | {len(categories['western_with_url_no_content'])} | {len(categories['western_no_url'])} |
| 中成药 | {len(categories['tcm_with_url_with_content'])} | {len(categories['tcm_with_url_no_content'])} | {len(categories['tcm_no_url'])} |

---

## 一、真正缺少网址的药品（需优先补充网址）

### 西药（{len(categories['western_no_url'])}个）

| 序号 | ID | 药品名称 | 剂型 | 备注 |
|------|-----|---------|------|------|
"""

    for i, drug in enumerate(categories['western_no_url'], 1):
        content += f"| {i} | {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['notes']} |\n"

    content += f"""
### 中成药（{len(categories['tcm_no_url'])}个）

| 序号 | ID | 药品名称 | 剂型 | 备注 |
|------|-----|---------|------|------|
"""

    for i, drug in enumerate(categories['tcm_no_url'], 1):
        content += f"| {i} | {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['notes']} |\n"

    content += f"""
---

## 二、有网址但内容未完善的药品

### 西药（{len(categories['western_with_url_no_content'])}个）

| 序号 | ID | 药品名称 | 剂型 | 网址 |
|------|-----|---------|------|------|
"""

    for i, drug in enumerate(categories['western_with_url_no_content'], 1):
        content += f"| {i} | {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['url']} |\n"

    content += f"""
### 中成药（{len(categories['tcm_with_url_no_content'])}个）

| 序号 | ID | 药品名称 | 剂型 | 网址 |
|------|-----|---------|------|------|
"""

    for i, drug in enumerate(categories['tcm_with_url_no_content'], 1):
        content += f"| {i} | {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['url']} |\n"

    content += f"""
---

## 三、已完成内容补充的药品

### 西药（{len(categories['western_with_url_with_content'])}个）

| 序号 | ID | 药品名称 | 剂型 | 网址 |
|------|-----|---------|------|------|
"""

    for i, drug in enumerate(categories['western_with_url_with_content'], 1):
        content += f"| {i} | {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['url']} |\n"

    content += f"""
### 中成药（{len(categories['tcm_with_url_with_content'])}个）

| 序号 | ID | 药品名称 | 剂型 | 网址 |
|------|-----|---------|------|------|
"""

    for i, drug in enumerate(categories['tcm_with_url_with_content'], 1):
        content += f"| {i} | {drug['id']} | {drug['name']} | {drug['dosage_form']} | {drug['url']} |\n"

    content += f"""
---

## 补充建议

### 对于无网址的药品
1. 到湖南药事服务网 (https://www.hnysfww.com) 手动搜索
2. 检查药品名称是否完全匹配
3. 注意区分不同剂型可能有不同网址

### 对于有网址但无内容的药品
运行以下脚本自动补充内容：
```bash
python3 scripts/process_missing_url_list.py
```

---

*最后更新: {today}*
"""

    # 写入文件
    output_file = OUTPUT_DIR / "仍缺少网址的药品清单_已更新.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_file

def main():
    print("=" * 80)
    print("更新仍缺少网址的药品清单")
    print("=" * 80)

    # 解析当前清单
    print("\n解析当前清单...")
    western_drugs, tcm_drugs = parse_current_list()
    print(f"  西药: {len(western_drugs)}个")
    print(f"  中成药: {len(tcm_drugs)}个")

    # 生成分类
    print("\n分类药品...")
    categories = generate_updated_list(western_drugs, tcm_drugs)

    print(f"\n西药分类:")
    print(f"  - 有网址有内容: {len(categories['western_with_url_with_content'])}个")
    print(f"  - 有网址无内容: {len(categories['western_with_url_no_content'])}个")
    print(f"  - 无网址: {len(categories['western_no_url'])}个")

    print(f"\n中成药分类:")
    print(f"  - 有网址有内容: {len(categories['tcm_with_url_with_content'])}个")
    print(f"  - 有网址无内容: {len(categories['tcm_with_url_no_content'])}个")
    print(f"  - 无网址: {len(categories['tcm_no_url'])}个")

    # 写入更新后的清单
    print("\n写入更新后的清单...")
    output_file = write_updated_list(categories)
    print(f"  已保存到: {output_file}")

    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)

if __name__ == "__main__":
    main()
