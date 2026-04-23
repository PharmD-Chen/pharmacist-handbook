#!/usr/bin/env python3
"""
生成轻量级药品索引文件
从完整的drugs.js中提取基本信息，用于快速加载
"""

import json
import re

def extract_drug_index():
    """从drugs.js中提取轻量级索引"""

    # 读取原始文件
    with open('deploy/data/drugs/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取drugIndex数组
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("Error: Could not find drugIndex array")
        return

    # 解析JSON
    try:
        drugs = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    # 创建轻量级索引
    index = []
    for drug in drugs:
        # 只保留基本信息
        item = {
            "id": drug.get("id"),
            "name": drug.get("name"),
            "full_name": drug.get("full_name"),
            "dosage_form": drug.get("dosage_form"),
            "types": drug.get("types", []),
            "manufacturers": drug.get("manufacturers", []),
            "pinyin": drug.get("pinyin"),
            "pinyin_initials": drug.get("pinyin_initials"),
            "dosage_form_pinyin": drug.get("dosage_form_pinyin"),
            "dosage_form_initials": drug.get("dosage_form_initials"),
            # 保留精简版手册内容
            "manual": {
                "indications": drug.get("manual", {}).get("indications", ""),
                "dosage": drug.get("manual", {}).get("dosage", ""),
                "contraindications": drug.get("manual", {}).get("contraindications", ""),
                "adverse_reactions": drug.get("manual", {}).get("adverse_reactions", ""),
                "interactions": drug.get("manual", {}).get("interactions", ""),
                "precautions": drug.get("manual", {}).get("precautions", ""),
                "pregnancy_category": drug.get("manual", {}).get("pregnancy_category", ""),
                "black_box_warning": drug.get("manual", {}).get("black_box_warning", ""),
            }
        }
        index.append(item)

    # 生成轻量级索引文件
    output = f"""// 药品手册索引 - 轻量级版本
// 自动生成于 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 共 {len(index)} 个药品
// 此文件只包含精简版内容，用于快速加载

const drugIndexLite = {json.dumps(index, ensure_ascii=False, indent=2)};

// 导出
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndexLite }};
}}
"""

    # 写入文件
    with open('deploy/data/drugs/drugs_lite.js', 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Generated drugs_lite.js with {len(index)} drugs")
    print(f"Original file size: {len(content)} bytes")
    print(f"Lite file size: {len(output)} bytes")

if __name__ == '__main__':
    extract_drug_index()
