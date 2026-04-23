#!/usr/bin/env python3
"""
修复药品手册质量问题
- 清理"哪儿有"等可疑内容
- 修复字段交叉污染
- 清理pharmacokinetics中的药效学内容
"""
import json
import re
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'

def clean_suspicious_content(text):
    """清理可疑内容"""
    if not text:
        return text
    
    # 移除"哪儿有"及后面的内容
    text = re.sub(r'\s*哪儿有.*', '', text)
    
    # 移除"剂型与规格"及后面的内容
    text = re.sub(r'\s*剂型与规格.*', '', text)
    
    # 移除"基药"、"医保"等标记
    text = re.sub(r'\s*(?:基药|医保|乙|甲)\d*%?', '', text)
    
    return text.strip()

def clean_pharmacokinetics(text):
    """清理pharmacokinetics，保留药动学参数，移除药效学描述"""
    if not text:
        return text
    
    # 如果包含药动学参数，保留这些参数
    pk_patterns = [
        r'半衰期[^。]*(?:约?\d+[\d\.]*\s*(?:小时|h|min|分钟))',
        r'达峰时间[^。]*(?:约?\d+[\d\.]*\s*(?:小时|h|min|分钟))',
        r'Tmax[^。]*(?:约?\d+[\d\.]*\s*(?:小时|h|min|分钟)?)',
        r'Cmax[^。]*(?:\d+[\d\.]*\s*(?:μg|mg|ng|pg)[/／](?:ml|mL|L|l))',
        r'生物利用度[^。]*(?:\d+[\d\.]*\s*%)',
        r'蛋白结合率[^。]*(?:\d+[\d\.]*\s*%)',
        r'(?:经|由)[^。]*(?:肝脏|肾脏|胆道|粪便|尿液|尿)[^。]*(?:代谢|排泄|消除|清除)',
    ]
    
    pk_info = []
    for pattern in pk_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        pk_info.extend(matches)
    
    if pk_info:
        return ' '.join(pk_info)
    
    # 如果没有提取到药动学参数，但包含成份信息（中成药），保留成份
    if re.match(r'^[\u4e00-\u9fa5、，,]+(?:姜黄|黄连|黄柏|黄芩|甘草|麝香|三七|人参|丹参|当归|川芎|白芍|熟地黄|山药|山茱萸|茯苓|泽泻|牡丹皮)', text):
        # 这是中成药成份，保留
        return text
    
    # 如果主要是药效学描述，返回空或简化
    if any(word in text for word in ['作用', '抑制', '促进', '治疗', '改善', '试验', '动物']):
        return None
    
    return text

def fix_cross_contamination(manual):
    """修复字段交叉污染"""
    fields = ['dosage', 'contraindications', 'adverse_reactions', 'interactions', 'precautions', 'pharmacokinetics']
    
    for field in fields:
        value = manual.get(field, '')
        if not value:
            continue
        
        # 检查是否包含其他字段的标题
        other_titles = {
            '禁忌症?': 'contraindications',
            '不良反应': 'adverse_reactions',
            '药物相互作用': 'interactions',
            '注意事项': 'precautions',
            '用法与?用量': 'dosage',
            '药理作用': 'pharmacokinetics'
        }
        
        for title_pattern, target_field in other_titles.items():
            if target_field == field:
                continue
            
            # 如果当前字段包含其他字段的标题，进行分割
            if re.search(title_pattern, value):
                parts = re.split(title_pattern, value, maxsplit=1)
                if len(parts) == 2:
                    # 保留当前字段标题之前的内容
                    manual[field] = parts[0].strip()
                    manual[f'full_{field}'] = parts[0].strip()
                    print(f"    修复 {field}: 移除{target_field}内容")
    
    return manual

def fix_drug(drug_id):
    """修复单个药品"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    
    try:
        with open(drug_file, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        manual = drug_data.get('manual', {})
        modified = False
        
        # 1. 清理可疑内容
        fields_to_clean = [
            'dosage', 'full_dosage',
            'contraindications', 'full_contraindications',
            'adverse_reactions', 'full_adverse_reactions',
            'interactions', 'full_interactions',
            'precautions', 'full_precautions',
            'pharmacokinetics', 'full_pharmacokinetics'
        ]
        
        for field in fields_to_clean:
            if manual.get(field):
                original = manual[field]
                cleaned = clean_suspicious_content(original)
                if original != cleaned:
                    manual[field] = cleaned
                    modified = True
                    print(f"    清理 {field}: 移除可疑内容")
        
        # 2. 修复字段交叉污染
        manual = fix_cross_contamination(manual)
        
        # 3. 清理pharmacokinetics
        if manual.get('pharmacokinetics'):
            original = manual['pharmacokinetics']
            cleaned = clean_pharmacokinetics(original)
            if cleaned != original:
                if cleaned:
                    manual['pharmacokinetics'] = cleaned
                    manual['full_pharmacokinetics'] = cleaned
                    print(f"    清理 pharmacokinetics: 保留药动学参数")
                else:
                    manual['pharmacokinetics'] = None
                    manual['full_pharmacokinetics'] = ''
                    print(f"    清理 pharmacokinetics: 移除药效学内容")
                modified = True
        
        if modified:
            drug_data['manual'] = manual
            with open(drug_file, 'w', encoding='utf-8') as f:
                json.dump(drug_data, f, ensure_ascii=False, indent=2)
            return True
        
        return False
        
    except Exception as e:
        print(f"    错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("修复药品手册质量问题")
    print("=" * 80)
    
    # 读取质量报告
    report_file = PROJECT_DIR / 'output' / 'comprehensive_quality_report.json'
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    drugs_with_issues = report.get('drugs_with_issues', [])
    drugs_with_warnings = report.get('drugs_with_warnings', [])
    
    # 合并需要修复的药品
    drugs_to_fix = []
    
    # 添加有问题的药品
    for drug in drugs_with_issues:
        # 只修复有内容问题的，不修复缺少网址的
        if any('哪儿有' in issue or '交叉污染' in issue for issue in drug.get('issues', [])):
            drugs_to_fix.append(drug)
    
    # 添加有警告的药品
    for drug in drugs_with_warnings:
        if any('pharmacokinetics' in warning for warning in drug.get('warnings', [])):
            drugs_to_fix.append(drug)
    
    # 去重
    seen = set()
    unique_drugs = []
    for drug in drugs_to_fix:
        if drug['id'] not in seen:
            seen.add(drug['id'])
            unique_drugs.append(drug)
    
    print(f"\n需要修复的药品: {len(unique_drugs)}个\n")
    
    fixed_count = 0
    
    for drug in unique_drugs:
        drug_id = drug['id']
        drug_name = drug['name']
        
        print(f"处理: ID {drug_id} - {drug_name}")
        
        if fix_drug(drug_id):
            fixed_count += 1
            print(f"  ✓ 已修复")
        else:
            print(f"  - 无需修复或修复失败")
    
    print(f"\n{'=' * 80}")
    print(f"修复完成: {fixed_count}/{len(unique_drugs)}")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    main()
