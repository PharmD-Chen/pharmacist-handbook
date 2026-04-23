#!/usr/bin/env python3
"""
手动添加药品详细信息工具
用于补充药品的适应症、用法用量等信息
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


def add_manual_info(drug):
    """为单个药品添加手册信息"""
    print(f"\n{'='*60}")
    print(f"药品: {drug['name']} {drug['dosage_form']}")
    print(f"{'='*60}")
    
    # 显示当前信息
    current = drug.get('manual', {})
    if current and current.get('indications'):
        print("\n当前信息:")
        print(f"  适应症: {current['indications'][:50]}...")
        update = input("\n是否更新? (y/n): ").lower()
        if update != 'y':
            return drug
    
    # 输入新信息
    print("\n请输入药品信息（直接回车跳过）:")
    
    manual = {
        'indications': input('适应症: ').strip(),
        'dosage': input('用法用量: ').strip(),
        'contraindications': input('禁忌: ').strip(),
        'adverse_reactions': input('不良反应: ').strip(),
        'interactions': input('药物相互作用: ').strip(),
        'pregnancy_category': input('FDA妊娠分级: ').strip(),
        'pharmacokinetics': input('药代动力学: ').strip(),
        'precautions': input('注意事项: ').strip(),
        'source': 'manual'
    }
    
    # 只保留非空字段
    manual = {k: v for k, v in manual.items() if v}
    
    if manual:
        drug['manual'] = manual
        print("✓ 信息已添加")
    else:
        print("✗ 未输入任何信息")
    
    return drug


def batch_add_from_file(json_file):
    """从JSON文件批量添加药品信息"""
    print(f"\n从文件批量导入: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        batch_data = json.load(f)
    
    drugs = load_drugs()
    
    update_count = 0
    for drug_info in batch_data:
        name = drug_info.get('name')
        dosage_form = drug_info.get('dosage_form')
        manual = drug_info.get('manual')
        
        if not name or not manual:
            continue
        
        # 查找匹配的药品
        for drug in drugs:
            if drug['name'] == name and drug['dosage_form'] == dosage_form:
                drug['manual'] = manual
                update_count += 1
                print(f"✓ 已更新: {name} {dosage_form}")
                break
    
    save_drugs(drugs)
    print(f"\n共更新 {update_count} 个药品")


def interactive_mode():
    """交互式添加模式"""
    drugs = load_drugs()
    
    print(f"\n共加载 {len(drugs)} 个药品")
    print("输入 'q' 退出, 's' 保存并退出, 'n' 跳过当前药品\n")
    
    for i, drug in enumerate(drugs, 1):
        # 检查是否已有信息
        if drug.get('manual') and drug['manual'].get('indications'):
            continue
        
        print(f"\n[{i}/{len(drugs)}] ", end="")
        
        drug = add_manual_info(drug)
        
        # 保存进度
        if i % 10 == 0:
            save_drugs(drugs)
            print(f"\n已自动保存进度 ({i}/{len(drugs)})")
    
    # 最终保存
    save_drugs(drugs)
    print("\n✓ 所有数据已保存")


def main():
    """主函数"""
    import sys
    
    print("="*60)
    print("药品信息录入工具")
    print("="*60)
    print("\n使用方式:")
    print("1. 交互式录入: python add_drug_manual.py")
    print("2. 批量导入: python add_drug_manual.py batch <json文件>")
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
    
    if len(sys.argv) > 1 and sys.argv[1] == 'batch':
        if len(sys.argv) > 2:
            batch_add_from_file(sys.argv[2])
        else:
            print("\n错误: 请提供JSON文件路径")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
