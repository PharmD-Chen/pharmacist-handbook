#!/usr/bin/env python3
"""为所有药品生成精简版内容"""

import re

def smart_truncate(text, max_length=100):
    """智能截断文本，尽量在句子结尾处截断"""
    if not text or len(text) <= max_length:
        return text
    
    # 尝试在句子结尾处截断
    truncated = text[:max_length]
    
    # 查找最后一个句号、分号或换行
    for delimiter in ['。', '；', '<br>', '\n', ' ']:
        last_pos = truncated.rfind(delimiter)
        if last_pos > max_length * 0.5:  # 确保至少保留一半内容
            return truncated[:last_pos + 1]
    
    return truncated + '...'

def generate_summary(full_text, field_type):
    """根据字段类型生成精简版内容"""
    if not full_text:
        return full_text
    
    # 根据不同字段类型设置不同的精简策略
    limits = {
        'indications': 150,
        'dosage': 120,
        'contraindications': 100,
        'adverse_reactions': 150,
        'interactions': 120,
        'pharmacokinetics': 150,
        'precautions': 120
    }
    
    limit = limits.get(field_type, 100)
    
    # 如果内容已经很短，直接返回
    if len(full_text) <= limit:
        return full_text
    
    # 智能截断
    return smart_truncate(full_text, limit)

def process_drug_manual(manual_text):
    """处理单个药品的manual字段"""
    # 提取所有full_字段
    fields = {}
    
    field_names = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                   'interactions', 'pregnancy_category', 'pharmacokinetics', 'precautions']
    
    for field in field_names:
        # 匹配full_字段
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
            summary_fields[field] = generate_summary(full_value, field)
    
    return summary_fields, fields

def update_drugs_js():
    """更新drugs.js文件"""
    print("正在读取 drugs.js 文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到所有药品记录
    drug_pattern = r'("name":\s*"[^"]+"[\s\S]*?"manual":\s*\{[\s\S]*?\})'
    
    updated_count = 0
    
    def process_drug_match(match):
        nonlocal updated_count
        drug_text = match.group(1)
        
        # 提取药品名称
        name_match = re.search(r'"name":\s*"([^"]+)"', drug_text)
        if not name_match:
            return drug_text
        
        drug_name = name_match.group(1)
        
        # 提取manual部分
        manual_match = re.search(r'"manual":\s*\{([\s\S]*?)\}', drug_text)
        if not manual_match:
            return drug_text
        
        manual_content = manual_match.group(1)
        
        # 检查是否有full_字段
        if '"full_indications"' not in manual_content:
            return drug_text
        
        # 处理manual字段
        summary_fields, full_fields = process_drug_manual(manual_content)
        
        # 构建新的manual
        new_manual_lines = ['"manual": {']
        
        field_order = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                       'interactions', 'pregnancy_category', 'pharmacokinetics', 'precautions']
        
        for field in field_order:
            if field in summary_fields:
                new_manual_lines.append(f'      "{field}": "{summary_fields[field]}",')
        
        # 添加source
        source_match = re.search(r'"source":\s*"([^"]*)"', manual_content)
        if source_match:
            new_manual_lines.append(f'      "source": "{source_match.group(1)}",')
        
        # 添加full_字段
        for field in field_order:
            if field in full_fields:
                new_manual_lines.append(f'      "full_{field}": "{full_fields[field]}",')
        
        # 移除最后一个逗号
        if new_manual_lines[-1].endswith(','):
            new_manual_lines[-1] = new_manual_lines[-1][:-1]
        
        new_manual_lines.append('    }')
        new_manual = '\n'.join(new_manual_lines)
        
        # 替换原manual
        new_drug_text = re.sub(r'"manual":\s*\{[\s\S]*?\}', new_manual, drug_text)
        
        updated_count += 1
        if updated_count % 10 == 0:
            print(f"  已处理 {updated_count} 个药品...")
        
        return new_drug_text
    
    # 处理所有药品
    new_content = re.sub(drug_pattern, process_drug_match, content)
    
    print(f"\n共更新 {updated_count} 个药品的精简版内容")
    
    # 保存文件
    print("正在保存...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 完成！")

if __name__ == '__main__':
    update_drugs_js()
