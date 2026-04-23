#!/usr/bin/env python3
"""
为所有有手册的药品添加精简版内容
策略：
1. 如果已经有full_xxx字段，说明已经处理过，跳过
2. 如果没有full_xxx字段，将当前内容作为完整版保存到full_xxx
3. 根据完整版内容智能生成精简版
"""

import json
import re

def load_drugs():
    """加载药品数据"""
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'const DRUGS_DATA = (\[.*?\]);', content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return []

def save_drugs(drugs):
    """保存药品数据"""
    js_content = 'const DRUGS_DATA = ' + json.dumps(drugs, ensure_ascii=False, indent=2) + ';'
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

def smart_summarize(text, field_type):
    """智能生成精简版内容"""
    if not text or len(text) < 100:
        return text
    
    # 移除HTML标签进行长度判断
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # 如果内容本身就很短，直接返回
    if len(clean_text) < 150:
        return text
    
    # 根据不同字段类型采用不同的精简策略
    if field_type == 'indications':
        return summarize_indications(text)
    elif field_type == 'dosage':
        return summarize_dosage(text)
    elif field_type == 'contraindications':
        return summarize_contraindications(text)
    elif field_type == 'adverse_reactions':
        return summarize_adverse_reactions(text)
    elif field_type == 'precautions':
        return summarize_precautions(text)
    elif field_type == 'interactions':
        return summarize_interactions(text)
    elif field_type == 'pharmacokinetics':
        return summarize_pharmacokinetics(text)
    elif field_type == 'black_box_warning':
        return summarize_black_box(text)
    else:
        # 默认策略：提取前150个字符
        return truncate_text(text, 150)

def summarize_indications(text):
    """精简适应症"""
    # 提取主要感染类型
    patterns = [
        r'([^。；]+?感染)',
        r'([^。；]+?炎)',
        r'([^。；]+?病)',
    ]
    
    key_points = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches[:5]:  # 最多取5个
            clean = re.sub(r'<[^>]+>', '', match).strip()
            if clean and clean not in key_points and len(clean) > 2:
                key_points.append(clean)
    
    if key_points:
        # 提取第一段的概述部分
        first_para = text.split('<br>')[0] if '<br>' in text else text.split('。')[0]
        if len(re.sub(r'<[^>]+>', '', first_para)) > 20:
            return first_para + '<br><br>主要适用于：<strong>' + '、'.join(key_points[:6]) + '</strong>等。'
        else:
            return '适用于<strong>' + '、'.join(key_points[:8]) + '</strong>等。'
    
    return truncate_text(text, 200)

def summarize_dosage(text):
    """精简用法用量"""
    # 提取关键剂量信息
    lines = text.split('<br>')
    summary_lines = []
    
    for line in lines[:6]:  # 最多取6行
        clean = re.sub(r'<[^>]+>', '', line).strip()
        # 保留包含剂量的行
        if any(keyword in clean for keyword in ['成人', '儿童', '静脉', '口服', 'g', 'mg', 'ml', '一次', '一日']):
            if len(summary_lines) < 4:  # 最多保留4行
                summary_lines.append(line)
    
    if summary_lines:
        return '<br>'.join(summary_lines)
    
    return truncate_text(text, 200)

def summarize_contraindications(text):
    """精简禁忌"""
    # 提取关键禁忌
    patterns = [
        r'对([^。]+?)过敏',
        r'([^。]+?)禁用',
        r'([^。]+?)慎用',
    ]
    
    key_points = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            clean = re.sub(r'<[^>]+>', '', match).strip()
            if clean and clean not in key_points:
                key_points.append(clean)
    
    if key_points:
        return '对<strong>' + '、'.join(key_points[:5]) + '</strong>者禁用。'
    
    return truncate_text(text, 150)

def summarize_adverse_reactions(text):
    """精简不良反应"""
    # 提取常见和少见不良反应
    patterns = [
        r'常见[：:]?([^。]+?)',
        r'少见[：:]?([^。]+?)',
        r'偶见[：:]?([^。]+?)',
    ]
    
    sections = []
    if '常见' in text:
        sections.append('常见反应')
    if '少见' in text or '偶见' in text:
        sections.append('少见反应')
    if '严重' in text:
        sections.append('严重反应')
    
    # 提取具体反应名称
    reactions = []
    reaction_pattern = r'([\u4e00-\u9fa5]{2,8})(?:反应|症状|不良|不适)'
    matches = re.findall(reaction_pattern, text)
    for match in set(matches):
        if match not in ['不良', '患者', '临床']:
            reactions.append(match)
    
    if reactions:
        return '常见：<strong>' + '、'.join(reactions[:6]) + '</strong>等。详见完整说明。'
    
    return truncate_text(text, 180)

def summarize_precautions(text):
    """精简注意事项"""
    # 提取带序号的要点
    numbered_items = re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩]([^<]+)', text)
    
    if numbered_items:
        key_points = []
        for item in numbered_items[:5]:
            clean = item.strip()
            if len(clean) > 5:
                key_points.append(clean[:30] + '...' if len(clean) > 30 else clean)
        
        if key_points:
            return '<br>'.join(['①' + p.replace('...', '') for p in key_points])
    
    # 如果没有序号，提取关键警告
    if '警告' in text or '注意' in text:
        first_para = text.split('<br>')[0] if '<br>' in text else text.split('。')[0]
        return first_para
    
    return truncate_text(text, 200)

def summarize_interactions(text):
    """精简药物相互作用"""
    # 提取与哪些药物有相互作用
    patterns = [
        r'与([^。]+?)(?:合用|联用|同用)',
        r'([\u4e00-\u9fa5]+?类)',
    ]
    
    drugs = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            clean = re.sub(r'<[^>]+>', '', match).strip()
            if clean and len(clean) > 1 and len(clean) < 15:
                drugs.append(clean)
    
    if drugs:
        return '与<strong>' + '、'.join(list(set(drugs))[:5]) + '</strong>等药物有相互作用。详见完整说明。'
    
    return truncate_text(text, 180)

def summarize_pharmacokinetics(text):
    """精简药代动力学"""
    # 提取半衰期、排泄等关键信息
    key_info = []
    
    patterns = {
        '半衰期': r'半衰期[^。]*?([\d.]+\s*小时?)',
        '达峰时间': r'达峰[^。]*?([\d.]+\s*小时?)',
        '蛋白结合率': r'蛋白结合率[^。]*?([\d.]+%)',
    }
    
    for name, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            key_info.append(f'{name}约{match.group(1)}')
    
    if key_info:
        return '；'.join(key_info) + '。详见完整说明。'
    
    return truncate_text(text, 150)

def summarize_black_box(text):
    """精简黑框警示"""
    # 提取主要警告标题
    if '警告' in text:
        first_para = text.split('<br>')[0] if '<br>' in text else text.split('。')[0]
        return first_para
    
    return truncate_text(text, 200)

def truncate_text(text, max_length):
    """截断文本到指定长度"""
    clean_text = re.sub(r'<[^>]+>', '', text)
    if len(clean_text) <= max_length:
        return text
    
    # 在HTML标签安全的情况下截断
    truncated = text[:max_length * 2]  # 预留HTML标签空间
    # 找到最后一个完整的句子或逗号
    for sep in ['。<br>', '。', '<br>', '；']:
        idx = truncated.rfind(sep)
        if idx > max_length * 0.5:
            return truncated[:idx + len(sep)] + '...'
    
    return truncated + '...'

def process_all_drugs(drugs):
    """处理所有药品"""
    processed = 0
    skipped = 0
    
    fields_to_process = [
        'indications', 'dosage', 'contraindications', 'adverse_reactions',
        'interactions', 'pregnancy_category', 'pharmacokinetics', 
        'precautions', 'black_box_warning', 'solvent'
    ]
    
    for drug in drugs:
        manual = drug.get('manual', {})
        if not manual:
            continue
        
        # 检查是否已经处理过（有full_字段）
        has_full_fields = any(key.startswith('full_') for key in manual.keys())
        if has_full_fields:
            skipped += 1
            continue
        
        # 处理每个字段
        for field in fields_to_process:
            if field in manual and manual[field]:
                full_content = manual[field]
                
                # 保存完整版
                manual[f'full_{field}'] = full_content
                
                # 生成精简版
                summary = smart_summarize(full_content, field)
                manual[field] = summary
        
        drug['manual'] = manual
        processed += 1
        
        if processed % 100 == 0:
            print(f"  已处理 {processed} 个药品...")
    
    return drugs, processed, skipped

def main():
    print("=" * 60)
    print("批量为药品添加精简版内容")
    print("=" * 60)
    
    drugs = load_drugs()
    print(f"当前共有 {len(drugs)} 个药品条目")
    
    print("\n开始处理...")
    drugs, processed, skipped = process_all_drugs(drugs)
    
    print(f"\n处理完成:")
    print(f"  - 新处理: {processed} 个药品")
    print(f"  - 已存在(跳过): {skipped} 个药品")
    
    print("\n保存数据...")
    save_drugs(drugs)
    print("✅ 数据已保存")
    
    print("\n说明:")
    print("- 精简版内容显示在主界面")
    print("- 完整内容保存在 full_xxx 字段，点击箭头查看")

if __name__ == '__main__':
    main()
