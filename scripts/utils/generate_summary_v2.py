#!/usr/bin/env python3
"""生成更精简的版本 - 去除说明性文字，只保留核心要点"""

import re

def extract_key_points(text, max_length=80):
    """提取关键要点，去除说明性文字"""
    if not text:
        return text
    
    # 如果内容已经很短，直接返回
    if len(text) <= max_length:
        return text
    
    # 分割成句子或条目
    # 先尝试按数字序号分割
    lines = re.split(r'(?:<br>|\n|\s+(?=\d+[\.、])|\s+(?=[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽]))', text)
    
    key_points = []
    total_length = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 去除HTML标签
        line = re.sub(r'<[^>]+>', '', line)
        
        # 精简内容：去除"应"、"可"等说明性词汇开头
        # 保留核心信息
        line = re.sub(r'^(本品|本品为|本药|该药|药物|用药|患者|治疗时|使用时)\s*', '', line)
        line = re.sub(r'^(应注意|应注意监测|应慎用|应禁用|应告知|应逐渐|应从小剂量|应定期|应停止|应暂停|应考虑|应谨慎|应去医院|应告知患者)', '', line)
        line = re.sub(r'^(有|具有|存在|伴有|患有)', '', line)
        line = re.sub(r'^(常见|偶见|罕见|主要|严重|轻度|中度|重度)\s*', r'\1', line)
        
        line = line.strip()
        
        if len(line) < 5:  # 太短的跳过
            continue
            
        # 如果加上这个要点会超出长度限制，就停止
        if total_length + len(line) > max_length and key_points:
            break
        
        key_points.append(line)
        total_length += len(line) + 3  # 3 for separator
    
    if not key_points:
        # 如果没有提取到要点，直接截断
        return text[:max_length-3] + '...' if len(text) > max_length else text
    
    # 合并要点
    result = '；'.join(key_points[:3])  # 最多3个要点
    
    if len(result) > max_length:
        result = result[:max_length-3] + '...'
    
    return result

def generate_summary_v2(full_text, field_type):
    """生成精简版内容V2 - 更加精简"""
    if not full_text:
        return full_text
    
    # 根据不同字段类型设置不同的精简策略
    if field_type == 'indications':
        # 适应症：提取主要疾病名称
        return extract_key_points(full_text, 100)
    
    elif field_type == 'dosage':
        # 用法用量：提取剂量和频次
        # 查找剂量模式
        dose_match = re.search(r'(一次?\d+[～\-]?\d*\s*(mg|g|ml|μg|IU|单位|片|粒|支|瓶)[^。；]*(?:一日|每日|分|次)[^。；]*)', full_text)
        if dose_match:
            dose = dose_match.group(1).strip()
            # 查找给药途径
            route_match = re.search(r'(口服|静脉|皮下|肌内|吸入|外用|滴鼻|滴眼|含服|舌下)', full_text)
            if route_match:
                return f"{route_match.group(1)}：{dose}"
            return dose
        return extract_key_points(full_text, 80)
    
    elif field_type == 'contraindications':
        # 禁忌症：提取禁用人群
        return extract_key_points(full_text, 80)
    
    elif field_type == 'adverse_reactions':
        # 不良反应：提取主要反应
        return extract_key_points(full_text, 100)
    
    elif field_type == 'interactions':
        # 相互作用：提取关键相互作用
        return extract_key_points(full_text, 80)
    
    elif field_type == 'pharmacokinetics':
        # 药理作用：提取药效学和药动学核心
        pharma_parts = []
        
        # 查找药效学
        efficacy_match = re.search(r'药效学[：:]\s*([^。；<]+)', full_text)
        if efficacy_match:
            pharma_parts.append(f"药效学：{efficacy_match.group(1).strip()}")
        
        # 查找药动学
        pk_match = re.search(r'药动学[：:]\s*([^。；<]+)', full_text)
        if pk_match:
            pharma_parts.append(f"药动学：{pk_match.group(1).strip()}")
        
        if pharma_parts:
            result = '；'.join(pharma_parts)
            return result[:120] + '...' if len(result) > 120 else result
        
        return extract_key_points(full_text, 100)
    
    elif field_type == 'precautions':
        # 注意事项：提取核心注意点
        return extract_key_points(full_text, 100)
    
    return extract_key_points(full_text, 80)

def process_drug_manual(manual_text):
    """处理单个药品的manual字段"""
    fields = {}
    
    field_names = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                   'interactions', 'pregnancy_category', 'pharmacokinetics', 'precautions']
    
    for field in field_names:
        pattern = rf'"full_{field}":\s*"([^"]*)"'
        match = re.search(pattern, manual_text)
        if match:
            fields[field] = match.group(1)
    
    # 生成精简版
    summary_fields = {}
    for field, full_value in fields.items():
        if field == 'pregnancy_category':
            summary_fields[field] = full_value
        else:
            summary_fields[field] = generate_summary_v2(full_value, field)
    
    return summary_fields, fields

def update_drugs_js():
    """更新drugs.js文件"""
    print("正在读取 drugs.js 文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    drug_pattern = r'("name":\s*"[^"]+"[\s\S]*?"manual":\s*\{[\s\S]*?\})'
    
    updated_count = 0
    
    def process_drug_match(match):
        nonlocal updated_count
        drug_text = match.group(1)
        
        name_match = re.search(r'"name":\s*"([^"]+)"', drug_text)
        if not name_match:
            return drug_text
        
        drug_name = name_match.group(1)
        
        manual_match = re.search(r'"manual":\s*\{([\s\S]*?)\}', drug_text)
        if not manual_match:
            return drug_text
        
        manual_content = manual_match.group(1)
        
        if '"full_indications"' not in manual_content:
            return drug_text
        
        summary_fields, full_fields = process_drug_manual(manual_content)
        
        # 构建新的manual
        new_manual_lines = ['"manual": {']
        
        field_order = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                       'interactions', 'pregnancy_category', 'pharmacokinetics', 'precautions']
        
        for field in field_order:
            if field in summary_fields:
                new_manual_lines.append(f'      "{field}": "{summary_fields[field]}",')
        
        source_match = re.search(r'"source":\s*"([^"]*)"', manual_content)
        if source_match:
            new_manual_lines.append(f'      "source": "{source_match.group(1)}",')
        
        for field in field_order:
            if field in full_fields:
                new_manual_lines.append(f'      "full_{field}": "{full_fields[field]}",')
        
        if new_manual_lines[-1].endswith(','):
            new_manual_lines[-1] = new_manual_lines[-1][:-1]
        
        new_manual_lines.append('    }')
        new_manual = '\n'.join(new_manual_lines)
        
        new_drug_text = re.sub(r'"manual":\s*\{[\s\S]*?\}', new_manual, drug_text)
        
        updated_count += 1
        if updated_count % 100 == 0:
            print(f"  已处理 {updated_count} 个药品...")
        
        return new_drug_text
    
    new_content = re.sub(drug_pattern, process_drug_match, content)
    
    print(f"\n共更新 {updated_count} 个药品的精简版内容")
    
    print("正在保存...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 完成！")

if __name__ == '__main__':
    update_drugs_js()
