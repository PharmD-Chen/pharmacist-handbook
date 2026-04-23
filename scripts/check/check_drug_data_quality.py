#!/usr/bin/env python3
"""
检查药品数据质量
检查129个注射液药品的数据完整性
"""

import json
from pathlib import Path

# 129个注射液药品ID列表
INJECTION_DRUG_IDS = [
    113, 114, 569, 721, 794, 766, 745, 540, 793, 733, 997, 785, 859, 795, 592,
    729, 749, 768, 581, 791, 789, 849, 757, 738, 869, 799, 803, 586, 571, 604,
    916, 103, 629, 788, 847, 105, 639, 263, 595, 558, 547, 549, 606, 439, 804,
    837, 905, 277, 826, 411, 833, 1024, 830, 832, 628, 684, 387, 388, 435, 887,
    281, 107, 934, 688, 295, 900, 234, 781, 779, 6, 5, 658, 656, 444, 741, 585,
    681, 736, 86, 624, 1014, 565, 1027, 641, 77, 35, 431, 461, 560, 786, 55, 917,
    432, 130, 434, 634, 631, 563, 753, 132, 185, 739, 398, 61, 852, 1029, 262,
    224, 983, 978, 979, 509, 510, 735, 725, 647, 619, 36, 800, 774, 391, 419,
    610, 609, 608, 137, 3, 946, 700
]

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

def check_drug_data(drug_id):
    """检查单个药品的数据质量"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return {"id": drug_id, "exists": False, "issues": ["文件不存在"]}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {"id": drug_id, "exists": True, "issues": [f"JSON解析错误: {e}"]}
    
    issues = []
    drug_name = data.get('name', f'ID:{drug_id}')
    
    # 检查药品手册字段
    manual = data.get('manual', {})
    
    # 检查关键字段是否为空
    key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions']
    empty_fields = []
    
    for field in key_fields:
        value = manual.get(field, '')
        if not value or value.strip() == '':
            empty_fields.append(field)
    
    if empty_fields:
        issues.append(f"缺少关键字段: {', '.join(empty_fields)}")
    
    # 检查库位信息
    specs = data.get('specifications', [])
    for spec in specs:
        has_outpatient = bool(spec.get('outpatient_location'))
        has_inpatient = bool(spec.get('inpatient_location'))
        
        if not has_outpatient and not has_inpatient:
            issues.append("缺少库位信息(门诊和住院)")
        elif not has_inpatient:
            issues.append("缺少住院库位号")
        elif not has_outpatient:
            issues.append("缺少门诊库位号")
    
    # 检查数据内容异常（如不良反应包含禁忌症内容）
    adverse = manual.get('adverse_reactions', '')
    if '禁忌' in adverse and '不良反应' not in adverse:
        issues.append("不良反应字段包含禁忌症内容，数据混乱")
    
    # 检查是否只有不良反应而其他都为空
    has_adverse = bool(manual.get('adverse_reactions', '').strip())
    has_indications = bool(manual.get('indications', '').strip())
    has_dosage = bool(manual.get('dosage', '').strip())
    
    if has_adverse and not has_indications and not has_dosage:
        issues.append("仅存在不良反应数据，其他关键字段缺失")
    
    return {
        "id": drug_id,
        "name": drug_name,
        "exists": True,
        "issues": issues,
        "data_summary": {
            "has_indications": has_indications,
            "has_dosage": has_dosage,
            "has_contraindications": bool(manual.get('contraindications', '').strip()),
            "has_adverse_reactions": has_adverse,
            "has_interactions": bool(manual.get('interactions', '').strip()),
            "has_precautions": bool(manual.get('precautions', '').strip())
        }
    }

def main():
    """主函数"""
    print("=" * 80)
    print("检查129个注射液药品数据质量")
    print("=" * 80)
    
    problematic_drugs = []
    good_drugs = []
    
    for drug_id in INJECTION_DRUG_IDS:
        result = check_drug_data(drug_id)
        
        if result['issues']:
            problematic_drugs.append(result)
        else:
            good_drugs.append(result)
    
    # 输出结果
    print(f"\n总计检查: {len(INJECTION_DRUG_IDS)} 个药品")
    print(f"数据完整: {len(good_drugs)} 个")
    print(f"存在问题: {len(problematic_drugs)} 个")
    
    if problematic_drugs:
        print("\n" + "=" * 80)
        print("存在问题的药品列表:")
        print("=" * 80)
        
        for drug in problematic_drugs:
            print(f"\n【ID: {drug['id']}】{drug.get('name', '未知')}")
            for issue in drug['issues']:
                print(f"  - {issue}")
            
            # 显示数据摘要
            if 'data_summary' in drug:
                summary = drug['data_summary']
                print(f"  数据完整性:")
                print(f"    适应症: {'✓' if summary['has_indications'] else '✗'}")
                print(f"    用法用量: {'✓' if summary['has_dosage'] else '✗'}")
                print(f"    禁忌症: {'✓' if summary['has_contraindications'] else '✗'}")
                print(f"    不良反应: {'✓' if summary['has_adverse_reactions'] else '✗'}")
                print(f"    相互作用: {'✓' if summary['has_interactions'] else '✗'}")
                print(f"    注意事项: {'✓' if summary['has_precautions'] else '✗'}")
    
    # 保存问题药品列表到文件
    if problematic_drugs:
        output_file = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/problematic_drugs.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(problematic_drugs, f, ensure_ascii=False, indent=2)
        print(f"\n问题药品列表已保存到: {output_file}")
    
    print("\n" + "=" * 80)
    print("检查完成!")
    print("=" * 80)

if __name__ == "__main__":
    main()
