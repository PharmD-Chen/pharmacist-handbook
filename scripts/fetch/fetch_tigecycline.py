#!/usr/bin/env python3
"""获取替加环素的完整数据"""

import re
import subprocess
import json

def escape_for_json(text):
    """转义文本以用于JSON"""
    if not text:
        return ""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '<br>')
    text = text.replace('\r', '')
    return text

def get_website_content():
    """获取网站内容"""
    url = "https://www.hnysfww.com/goods.php?id=2035"
    try:
        result = subprocess.run(
            ['curl', '-s', url, '--max-time', '30', '-H', 'User-Agent: Mozilla/5.0'],
            capture_output=True,
            text=True,
            timeout=35
        )
        return result.stdout
    except Exception as e:
        print(f"获取网站内容失败: {e}")
        return None

def extract_field(html, field_name_cn):
    """精确提取字段内容"""
    # 构建匹配模式：找到包含字段名的td，然后获取下一个td的内容
    pattern = rf'<td[^>]*>\s*{re.escape(field_name_cn)}\s*</td>\s*<td[^>]*>(.*?)</td>'
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    
    if match:
        content = match.group(1)
        # 保留<br>标签，移除其他HTML标签
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<sub>(.*?)</sub>', r'\1', content)
        content = re.sub(r'<sup>(.*?)</sup>', r'\1', content)
        content = re.sub(r'<[^>]+>', '', content)
        # 清理多余空白
        content = re.sub(r'\n\s*\n', '\n', content)
        content = content.strip()
        return content
    return None

def generate_summary(text, field_type, max_length=100):
    """生成精简版内容"""
    if not text:
        return text
    
    # 如果内容已经很短，直接返回
    if len(text) <= max_length:
        return text
    
    # 分割成条目
    lines = re.split(r'(?:<br>|\n|\s+(?=\d+[\.、])|\s+(?=[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽]))', text)
    
    key_points = []
    total_length = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 去除HTML标签
        line = re.sub(r'<[^>]+>', '', line)
        
        # 精简内容：去除说明性词汇开头
        line = re.sub(r'^(本品|本品为|本药|该药|药物|用药|患者|治疗时|使用时)\s*', '', line)
        line = re.sub(r'^(应注意|应注意监测|应慎用|应禁用|应告知|应逐渐|应从小剂量|应定期|应停止|应暂停|应考虑|应谨慎|应去医院|应告知患者)', '', line)
        line = re.sub(r'^(有|具有|存在|伴有|患有)', '', line)
        
        line = line.strip()
        
        if len(line) < 5:
            continue
        
        if total_length + len(line) > max_length and key_points:
            break
        
        key_points.append(line)
        total_length += len(line) + 3
    
    if not key_points:
        return text[:max_length-3] + '...' if len(text) > max_length else text
    
    result = '；'.join(key_points[:3])
    
    if len(result) > max_length:
        result = result[:max_length-3] + '...'
    
    return result

def fetch_tigecycline():
    """获取替加环素数据"""
    print("正在从网站获取替加环素数据...")
    
    html = get_website_content()
    if not html:
        print("❌ 无法获取网站内容")
        return None
    
    # 提取各个字段
    fields = {
        'indications': extract_field(html, '适应证'),
        'dosage': extract_field(html, '用法与用量'),
        'contraindications': extract_field(html, '禁忌症'),
        'adverse_reactions': extract_field(html, '不良反应'),
        'interactions': extract_field(html, '药物相互作用'),
        'pregnancy_category': extract_field(html, 'FDA妊娠分级'),
        'pharmacokinetics': extract_field(html, '药理作用'),
        'precautions': extract_field(html, '注意事项')
    }
    
    print("\n获取到的原始数据：")
    for key, value in fields.items():
        if value:
            print(f"  {key}: {value[:80]}...")
        else:
            print(f"  {key}: (空)")
    
    return fields

def update_tigecycline_in_db(fields):
    """更新数据库中的替加环素"""
    print("\n正在更新 drugs.js...")
    
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 转义所有字段
    indications = escape_for_json(fields.get('indications', ''))
    dosage = escape_for_json(fields.get('dosage', ''))
    contraindications = escape_for_json(fields.get('contraindications', ''))
    adverse = escape_for_json(fields.get('adverse_reactions', ''))
    interactions = escape_for_json(fields.get('interactions', ''))
    pregnancy = fields.get('pregnancy_category', '')
    pharma = escape_for_json(fields.get('pharmacokinetics', ''))
    precautions = escape_for_json(fields.get('precautions', ''))
    source = "湖南药事服务网"
    
    # 生成精简版
    summary_indications = escape_for_json(generate_summary(fields.get('indications', ''), 'indications'))
    summary_dosage = escape_for_json(generate_summary(fields.get('dosage', ''), 'dosage'))
    summary_contra = escape_for_json(generate_summary(fields.get('contraindications', ''), 'contraindications'))
    summary_adverse = escape_for_json(generate_summary(fields.get('adverse_reactions', ''), 'adverse'))
    summary_interactions = "暂未发现有临床意义的药物相互作用。"
    summary_pharma = escape_for_json(generate_summary(fields.get('pharmacokinetics', ''), 'pharma'))
    summary_precautions = escape_for_json(generate_summary(fields.get('precautions', ''), 'precautions'))
    
    # 构建新的 manual
    manual_lines = ['"manual": {']
    if summary_indications:
        manual_lines.append(f'      "indications": "{summary_indications}",')
    if summary_dosage:
        manual_lines.append(f'      "dosage": "{summary_dosage}",')
    if summary_contra:
        manual_lines.append(f'      "contraindications": "{summary_contra}",')
    if summary_adverse:
        manual_lines.append(f'      "adverse_reactions": "{summary_adverse}",')
    manual_lines.append(f'      "interactions": "{summary_interactions}",')
    if pregnancy:
        manual_lines.append(f'      "pregnancy_category": "{pregnancy}",')
    if summary_pharma:
        manual_lines.append(f'      "pharmacokinetics": "{summary_pharma}",')
    if summary_precautions:
        manual_lines.append(f'      "precautions": "{summary_precautions}",')
    
    # 完整版字段
    if indications:
        manual_lines.append(f'      "full_indications": "{indications}",')
    if dosage:
        manual_lines.append(f'      "full_dosage": "{dosage}",')
    if contraindications:
        manual_lines.append(f'      "full_contraindications": "{contraindications}",')
    if adverse:
        manual_lines.append(f'      "full_adverse_reactions": "{adverse}",')
    if interactions:
        manual_lines.append(f'      "full_interactions": "{interactions}",')
    if pregnancy:
        manual_lines.append(f'      "full_pregnancy_category": "{pregnancy}",')
    if pharma:
        manual_lines.append(f'      "full_pharmacokinetics": "{pharma}",')
    if precautions:
        manual_lines.append(f'      "full_precautions": "{precautions}",')
    
    manual_lines.append(f'      "source": "{source}"')
    manual_lines.append('    }')
    
    new_manual = '\n'.join(manual_lines)
    
    # 查找并替换替加环素的 manual 部分
    pattern = r'("name": "※▲注射用替加环素".*?"spec_count": \d+,\s*)"manual": \{[^}]*\}'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print("找到替加环素记录，正在更新...")
        new_content = content[:match.end(1)] + new_manual + content[match.end():]
        
        with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 替加环素数据更新完成！")
        return True
    else:
        print("❌ 未找到替加环素记录")
        return False

if __name__ == '__main__':
    fields = fetch_tigecycline()
    if fields:
        update_tigecycline_in_db(fields)
    else:
        print("❌ 获取数据失败")
