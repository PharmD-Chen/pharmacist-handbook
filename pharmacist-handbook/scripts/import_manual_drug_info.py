#!/usr/bin/env python3
"""
批量导入手动录入的药品信息
"""

import json
from pathlib import Path

BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DATA_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"
OUTPUT_FILE = BASE_DIR / "pharmacist-handbook/data/drugs.js"


def load_drugs():
    """加载药品数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start = content.find('[')
    end = content.rfind(']')
    return json.loads(content[start:end+1])


def save_drugs(drugs):
    """保存药品数据"""
    import datetime
    
    js_content = "// 药品数据文件\n"
    js_content += f"// 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"// 药品数量: {len(drugs)}\n\n"
    js_content += "const DRUGS_DATA = "
    js_content += json.dumps(drugs, ensure_ascii=False, indent=2)
    js_content += ";\n"
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✓ 数据已保存: {OUTPUT_FILE}")


def import_from_json(json_file):
    """从JSON文件导入药品信息"""
    print(f"\n正在导入: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 支持两种格式
    # 格式1: {"药品信息列表": [...]}
    # 格式2: [{...}, {...}] (直接数组)
    
    if isinstance(data, dict) and '药品信息列表' in data:
        drug_info_list = data['药品信息列表']
    elif isinstance(data, list):
        drug_info_list = data
    else:
        print("错误: 不支持的JSON格式")
        return
    
    print(f"导入文件中包含 {len(drug_info_list)} 条药品信息")
    
    # 加载现有药品数据
    drugs = load_drugs()
    
    update_count = 0
    skip_count = 0
    not_found = []
    
    for drug_info in drug_info_list:
        name = drug_info.get('name')
        dosage_form = drug_info.get('dosage_form', '')
        manual = drug_info.get('manual')
        
        if not name or not manual:
            print(f"  ⚠ 跳过无效数据: {name}")
            continue
        
        # 查找匹配的药品
        found = False
        for drug in drugs:
            if drug['name'] == name:
                # 如果指定了剂型，则剂型也要匹配
                if dosage_form and drug.get('dosage_form') != dosage_form:
                    continue
                
                # 更新药品信息
                drug['manual'] = manual
                update_count += 1
                found = True
                print(f"  ✓ 已更新: {name} {drug.get('dosage_form', '')}")
                break
        
        if not found:
            not_found.append(f"{name} {dosage_form}".strip())
    
    # 保存数据
    save_drugs(drugs)
    
    print("\n" + "="*60)
    print("导入完成")
    print(f"成功更新: {update_count} 个药品")
    print(f"未找到: {len(not_found)} 个药品")
    if not_found:
        print("\n未找到的药品:")
        for name in not_found[:10]:  # 只显示前10个
            print(f"  - {name}")
        if len(not_found) > 10:
            print(f"  ... 还有 {len(not_found) - 10} 个")
    print("="*60)


def main():
    """主函数"""
    import sys
    
    print("="*60)
    print("药品信息批量导入工具")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\n使用方式:")
        print("  python import_manual_drug_info.py <json文件路径>")
        print("\n示例:")
        print("  python import_manual_drug_info.py ../data/manual_drug_info.json")
        print("\nJSON文件格式:")
        print('''
[
  {
    "name": "药品名",
    "dosage_form": "剂型",
    "manual": {
      "indications": "适应症",
      "dosage": "用法用量",
      ...
    }
  }
]
''')
        return
    
    json_file = sys.argv[1]
    import_from_json(json_file)


if __name__ == "__main__":
    main()
