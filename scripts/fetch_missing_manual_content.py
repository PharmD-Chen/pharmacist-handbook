#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为已更新网址但缺少详细内容的药品抓取并生成手册内容
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"
OUTPUT_DIR = PROJECT_ROOT / "output"

# 需要跳过的字段（不需要精简的字段）
SKIP_FIELDS = ['source', 'pregnancy_category']

def load_drug(drug_id):
    """加载药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    if not drug_file.exists():
        return None
    with open(drug_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_drug(drug_id, drug_data):
    """保存药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    with open(drug_file, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)

def check_manual_completeness(manual):
    """检查手册内容完整性"""
    required_fields = [
        'indications', 'dosage', 'contraindications', 
        'adverse_reactions', 'interactions', 'precautions'
    ]
    
    missing = []
    empty = []
    
    for field in required_fields:
        value = manual.get(field)
        if value is None:
            missing.append(field)
        elif not value or value.strip() == '' or value in ['null', 'None']:
            empty.append(field)
    
    return missing, empty

def simplify_indications(text):
    """精简适应症"""
    if not text:
        return ""
    # 去除多余空格和换行
    text = re.sub(r'\s+', ' ', text)
    # 保留关键疾病名称，去除解释性文字
    text = re.sub(r'适用于治疗', '用于', text)
    text = re.sub(r'请?用于治疗', '用于', text)
    text = re.sub(r'包括', '', text)
    return text.strip()[:300]

def simplify_dosage(text, dosage_form):
    """精简用法用量，根据剂型筛选"""
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    
    # 根据剂型筛选
    if '注射' in dosage_form:
        # 注射剂型：保留注射相关内容
        # 去除口服相关内容
        text = re.sub(r'口服[^。]*。', '', text)
    elif any(x in dosage_form for x in ['片', '胶囊', '颗粒', '丸']):
        # 口服剂型：保留口服相关内容
        # 去除注射相关内容
        text = re.sub(r'静脉注射[^。]*。', '', text)
        text = re.sub(r'肌内注射[^。]*。', '', text)
    
    # 精简描述
    text = re.sub(r'请?', '', text)
    text = re.sub(r'建议', '', text)
    text = re.sub(r'应该', '', text)
    
    return text.strip()[:400]

def simplify_contraindications(text):
    """精简禁忌症"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'禁用于', '禁用：', text)
    text = re.sub(r'对本品过敏者禁用', '过敏者禁用', text)
    return text.strip()[:250]

def simplify_adverse_reactions(text):
    """精简不良反应"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    
    # 提取常见不良反应
    common_patterns = [
        r'常见(?:不良)?反应[：:]?([^。]+)',
        r'常见[：:]?([^。]+)',
    ]
    
    for pattern in common_patterns:
        match = re.search(pattern, text)
        if match:
            return f"常见：{match.group(1).strip()[:200]}"
    
    # 如果没有匹配到，返回前200字符
    return text[:200]

def simplify_interactions(text):
    """精简药物相互作用"""
    if not text:
        return "暂未发现有临床意义的药物相互作用"
    
    text = re.sub(r'\s+', ' ', text)
    
    # 检查是否有实际内容
    if len(text.strip()) < 10 or '尚未' in text or '暂无' in text:
        return "暂未发现有临床意义的药物相互作用"
    
    return text.strip()[:250]

def simplify_pharmacokinetics(text):
    """精简药代动力学，提取关键参数"""
    if not text:
        return ""
    
    # 提取关键参数
    params = []
    
    # 达峰时间
    tmax_match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', text)
    if tmax_match:
        params.append(f"Tmax{tmax_match.group(1)}h")
    
    # 半衰期
    t12_match = re.search(r'半衰期.*?([\d\.]+)\s*小时?', text)
    if t12_match:
        params.append(f"t1/2{t12_match.group(1)}h")
    
    # 生物利用度
    bio_match = re.search(r'生物利用度.*?([\d\.]+)', text)
    if bio_match:
        params.append(f"F{bio_match.group(1)}%")
    
    # 蛋白结合率
    protein_match = re.search(r'蛋白结合率.*?([\d\.]+)', text)
    if protein_match:
        params.append(f"蛋白结合率{protein_match.group(1)}%")
    
    if params:
        return "；".join(params)
    
    # 如果没有提取到参数，返回前150字符
    text = re.sub(r'\s+', ' ', text)
    return text[:150]

def simplify_precautions(text):
    """精简注意事项"""
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    
    # 去除客套用语
    text = re.sub(r'请?', '', text)
    text = re.sub(r'建议', '', text)
    text = re.sub(r'应(该)?', '', text)
    
    # 提取关键警告
    warnings = []
    
    # 查找警告模式
    warning_patterns = [
        r'慎用[:：]?([^；。]+)',
        r'禁用[:：]?([^；。]+)',
        r'注意[:：]?([^；。]+)',
    ]
    
    for pattern in warning_patterns:
        matches = re.findall(pattern, text)
        warnings.extend(matches)
    
    if warnings:
        return "；".join(warnings[:5])  # 最多5条
    
    return text.strip()[:250]

def generate_simplified_version(drug_data):
    """生成精简版内容"""
    manual = drug_data.get('manual', {})
    dosage_form = drug_data.get('dosage_form', '')
    
    # 生成精简版字段
    simplified = {}
    
    if 'full_indications' in manual:
        simplified['indications'] = simplify_indications(manual['full_indications'])
    
    if 'full_dosage' in manual:
        simplified['dosage'] = simplify_dosage(manual['full_dosage'], dosage_form)
    
    if 'full_contraindications' in manual:
        simplified['contraindications'] = simplify_contraindications(manual['full_contraindications'])
    
    if 'full_adverse_reactions' in manual:
        simplified['adverse_reactions'] = simplify_adverse_reactions(manual['full_adverse_reactions'])
    
    if 'full_interactions' in manual:
        simplified['interactions'] = simplify_interactions(manual['full_interactions'])
    
    if 'full_pharmacokinetics' in manual:
        simplified['pharmacokinetics'] = simplify_pharmacokinetics(manual['full_pharmacokinetics'])
    
    if 'full_precautions' in manual:
        simplified['precautions'] = simplify_precautions(manual['full_precautions'])
    
    return simplified

def process_drug(drug_id):
    """处理单个药品"""
    drug_data = load_drug(drug_id)
    if not drug_data:
        return False, "文件不存在"
    
    # 检查是否有URL
    url_data = drug_data.get('url', {})
    if not url_data.get('hnysfww'):
        return False, "无湖南药事服务网网址"
    
    manual = drug_data.get('manual', {})
    if not manual:
        return False, "无手册内容"
    
    # 检查是否有详细版内容
    has_full_version = any(k.startswith('full_') for k in manual.keys())
    
    if not has_full_version:
        return False, "无详细版内容，需要重新抓取"
    
    # 检查精简版是否完整
    missing, empty = check_manual_completeness(manual)
    
    if not missing and not empty:
        return False, "精简版内容已完整"
    
    # 生成精简版
    simplified = generate_simplified_version(drug_data)
    
    # 更新手册内容
    for key, value in simplified.items():
        if key in missing or key in empty:
            manual[key] = value
    
    drug_data['manual'] = manual
    
    # 保存
    save_drug(drug_id, drug_data)
    
    return True, f"已更新字段: {list(simplified.keys())}"

def main():
    """主函数"""
    print("=" * 80)
    print("为已更新网址的药品生成精简版内容")
    print("=" * 80)
    
    # 加载药品索引
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)
    
    processed = []
    skipped = []
    failed = []
    
    print(f"\n开始处理 {len(drugs_index)} 个药品...")
    
    for drug in drugs_index:
        drug_id = drug['id']
        drug_name = drug['name']
        
        success, message = process_drug(drug_id)
        
        if success:
            processed.append({'id': drug_id, 'name': drug_name, 'message': message})
            print(f"✓ ID {drug_id}: {drug_name} - {message}")
        elif '已完整' in message or '无详细版' in message:
            skipped.append({'id': drug_id, 'name': drug_name, 'reason': message})
        else:
            failed.append({'id': drug_id, 'name': drug_name, 'reason': message})
    
    # 输出统计
    print("\n" + "=" * 80)
    print("处理统计")
    print("=" * 80)
    print(f"已处理: {len(processed)} 个")
    print(f"已跳过: {len(skipped)} 个")
    print(f"失败: {len(failed)} 个")
    
    if processed:
        print("\n已处理的药品:")
        for item in processed[:10]:  # 只显示前10个
            print(f"  - ID {item['id']}: {item['name']}")
        if len(processed) > 10:
            print(f"  ... 还有 {len(processed) - 10} 个")
    
    if failed:
        print("\n失败的药品:")
        for item in failed:
            print(f"  - ID {item['id']}: {item['name']} - {item['reason']}")
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()
