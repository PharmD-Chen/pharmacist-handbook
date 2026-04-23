#!/usr/bin/env python3
"""
全面质量检查 - 验证所有药品手册内容的真实性和规范性
"""
import json
import re
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'
OUTPUT_DIR = PROJECT_DIR / 'output'

# 合格的数据源
VALID_SOURCES = [
    '湖南药事服务网',
    'hnysfww.com',
    '国家药品监督管理局',
    '药品说明书'
]

# 可疑内容模式
SUSPICIOUS_PATTERNS = [
    r'哪儿有',  # 网站导航文字
    r'剂型与规格.*(?:基药|医保)',  # 混入的规格信息
    r'用法与用量.*(?:口服|外用).*剂型',  # 重复的用法用量
    r'药物相互作用.*(?:用法|用量)',  # 混入的用法用量
    r'注意事项.*(?:药物相互作用|用法用量)',  # 过长的注意事项
    r'^\s*$',  # 空内容
    r'null|None|undefined',  # 无效值
]

# 必需字段
REQUIRED_FIELDS = [
    'indications',
    'dosage',
    'contraindications',
    'adverse_reactions',
    'precautions'
]

def check_content_quality(drug_data, drug_id, drug_name):
    """检查单个药品内容质量"""
    issues = []
    warnings = []
    
    manual = drug_data.get('manual', {})
    url_data = drug_data.get('url', {})
    
    # 1. 检查数据来源
    source = manual.get('source', '')
    hnysfww_url = url_data.get('hnysfww', '')
    
    if not source:
        issues.append('缺少source字段')
    elif not any(valid in source for valid in VALID_SOURCES):
        issues.append(f'不可信的数据源: {source}')
    
    if not hnysfww_url:
        issues.append('缺少湖南药事服务网网址')
    elif 'hnysfww.com' not in hnysfww_url:
        issues.append(f'网址不是湖南药事服务网: {hnysfww_url}')
    
    # 2. 检查字段内容质量
    for field in REQUIRED_FIELDS:
        value = manual.get(field)
        full_field = f'full_{field}'
        full_value = manual.get(full_field)
        
        # 检查是否为空
        if not value or value in ['null', 'None', '']:
            warnings.append(f'{field}为空')
            continue
        
        # 检查是否包含可疑内容
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, str(value)):
                issues.append(f'{field}包含可疑内容: {pattern}')
                break
        
        # 检查精简版和详细版是否一致（应该一致或详细版更长）
        if full_value and len(str(full_value)) < len(str(value)):
            warnings.append(f'{field}: full版比精简版短')
        
        # 检查内容长度是否合理
        if len(str(value)) > 1000:
            warnings.append(f'{field}内容过长({len(str(value))}字符)')
        
        # 检查是否包含其他字段的内容（交叉污染）
        other_fields = [f for f in REQUIRED_FIELDS if f != field]
        for other in other_fields:
            other_value = manual.get(other, '')
            if other_value and str(other_value) in str(value) and len(str(other_value)) > 20:
                issues.append(f'{field}包含{other}的内容（交叉污染）')
                break
    
    # 3. 检查特殊字段
    # 药代动力学
    pk = manual.get('pharmacokinetics', '')
    if pk:
        # 检查是否包含药效学描述（应该是药动学参数）
        if any(word in pk for word in ['作用', '抑制', '促进', '治疗', '改善']):
            if not any(word in pk for word in ['小时', 'h', '半衰期', '达峰', 'Tmax', 'Cmax']):
                warnings.append('pharmacokinetics可能包含药效学而非药动学内容')
    
    # 4. 检查中成药字段
    indications = manual.get('indications', '')
    if indications:
        # 中成药应该使用"功能主治"风格
        if any(word in indications for word in ['活血', '化瘀', '清热', '解毒', '舒筋', '活络']):
            # 可能是中成药，检查是否从正确字段提取
            if drug_data.get('dosage_form') in ['片', '胶囊', '颗粒', '丸']:
                pass  # 可能是中成药
    
    return issues, warnings

def comprehensive_check():
    """全面检查所有药品"""
    print("=" * 80)
    print("全面质量检查 - 药品手册内容验证")
    print("=" * 80)
    
    # 读取药品索引
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)
    
    total_drugs = len(drugs_index)
    checked_drugs = 0
    drugs_with_issues = []
    drugs_with_warnings = []
    drugs_passed = []
    
    # 统计
    source_stats = defaultdict(int)
    field_stats = defaultdict(int)
    
    print(f"\n开始检查 {total_drugs} 个药品...\n")
    
    for drug in drugs_index:
        drug_id = drug['id']
        drug_name = drug['name']
        
        drug_file = DRUGS_DIR / f'{drug_id}.json'
        if not drug_file.exists():
            continue
        
        try:
            with open(drug_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            checked_drugs += 1
            
            # 统计来源
            source = drug_data.get('manual', {}).get('source', '未知')
            source_stats[source] += 1
            
            # 统计字段
            manual = drug_data.get('manual', {})
            for field in REQUIRED_FIELDS + ['interactions', 'pharmacokinetics']:
                if manual.get(field) and manual.get(field) not in ['null', 'None', '']:
                    field_stats[field] += 1
            
            # 质量检查
            issues, warnings = check_content_quality(drug_data, drug_id, drug_name)
            
            if issues:
                drugs_with_issues.append({
                    'id': drug_id,
                    'name': drug_name,
                    'issues': issues,
                    'warnings': warnings
                })
            elif warnings:
                drugs_with_warnings.append({
                    'id': drug_id,
                    'name': drug_name,
                    'warnings': warnings
                })
            else:
                drugs_passed.append({
                    'id': drug_id,
                    'name': drug_name
                })
            
            # 每100个药品显示进度
            if checked_drugs % 100 == 0:
                print(f"  已检查: {checked_drugs}/{total_drugs}")
            
        except Exception as e:
            drugs_with_issues.append({
                'id': drug_id,
                'name': drug_name,
                'issues': [f'读取错误: {str(e)}'],
                'warnings': []
            })
    
    # 生成报告
    print(f"\n{'=' * 80}")
    print("检查完成!")
    print(f"{'=' * 80}")
    
    print(f"\n📊 总体统计:")
    print(f"  总药品数: {total_drugs}")
    print(f"  已检查: {checked_drugs}")
    print(f"  ✓ 通过检查: {len(drugs_passed)} ({len(drugs_passed)/checked_drugs*100:.1f}%)")
    print(f"  ⚠ 有警告: {len(drugs_with_warnings)} ({len(drugs_with_warnings)/checked_drugs*100:.1f}%)")
    print(f"  ✗ 有问题: {len(drugs_with_issues)} ({len(drugs_with_issues)/checked_drugs*100:.1f}%)")
    
    print(f"\n📋 数据来源统计:")
    for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}个药品")
    
    print(f"\n📝 字段完整性统计:")
    for field, count in sorted(field_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count / checked_drugs * 100
        print(f"  {field}: {count}/{checked_drugs} ({percentage:.1f}%)")
    
    # 显示有问题药品
    if drugs_with_issues:
        print(f"\n{'=' * 80}")
        print(f"✗ 有问题的药品 ({len(drugs_with_issues)}个):")
        print(f"{'=' * 80}")
        for drug in drugs_with_issues[:20]:  # 只显示前20个
            print(f"\nID {drug['id']}: {drug['name']}")
            for issue in drug['issues']:
                print(f"  ✗ {issue}")
            for warning in drug['warnings'][:3]:  # 最多显示3个警告
                print(f"  ⚠ {warning}")
        
        if len(drugs_with_issues) > 20:
            print(f"\n... 还有 {len(drugs_with_issues) - 20} 个药品有问题")
    
    # 保存详细报告
    report_file = OUTPUT_DIR / 'comprehensive_quality_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_drugs': total_drugs,
                'checked_drugs': checked_drugs,
                'passed': len(drugs_passed),
                'warnings': len(drugs_with_warnings),
                'issues': len(drugs_with_issues)
            },
            'source_stats': dict(source_stats),
            'field_stats': dict(field_stats),
            'drugs_with_issues': drugs_with_issues,
            'drugs_with_warnings': drugs_with_warnings
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    return drugs_with_issues, drugs_with_warnings

if __name__ == '__main__':
    comprehensive_check()
