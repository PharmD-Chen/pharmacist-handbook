#!/usr/bin/env python3
"""更新氟尿嘧啶的说明书"""

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

def get_website_content(url):
    """获取网站内容"""
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
    pattern = rf'<td[^>]*>\s*{re.escape(field_name_cn)}\s*</td>\s*<td[^>]*>(.*?)</td>'
    match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
    
    if match:
        content = match.group(1)
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'<sub>(.*?)</sub>', r'\1', content)
        content = re.sub(r'<sup>(.*?)</sup>', r'\1', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\n\s*\n', '\n', content)
        content = content.strip()
        return content
    return None

def filter_dosage_by_form(dosage_text, dosage_form):
    """根据剂型筛选用法用量"""
    if not dosage_text:
        return dosage_text
    
    form_keywords = {
        '片': ['口服', '含服', '嚼服', '吞服', '舌下含服'],
        '胶囊': ['口服', '吞服'],
        '颗粒': ['口服', '冲服', '开水冲服'],
        '散': ['口服', '冲服', '外用'],
        '丸': ['口服', '含服'],
        '注射液': ['静脉注射', '肌内注射', '皮下注射', '静脉滴注', '注射'],
        '注射用': ['静脉注射', '肌内注射', '皮下注射', '静脉滴注', '注射'],
        '滴眼液': ['滴眼', '眼部'],
        '滴鼻液': ['滴鼻', '鼻部'],
        '滴耳液': ['滴耳', '耳部'],
        '栓剂': ['直肠给药', '阴道给药', '肛门'],
        '软膏': ['外用', '涂抹'],
        '乳膏': ['外用', '涂抹'],
        '凝胶': ['外用', '涂抹'],
        '贴': ['外用', '贴敷'],
        '喷雾': ['吸入', '喷入', '外用'],
        '吸入': ['吸入'],
        '含片': ['含服'],
        '混悬液': ['口服', '外用'],
        '口服溶液': ['口服'],
        '糖浆': ['口服'],
    }
    
    keywords = []
    for form, keys in form_keywords.items():
        if form in dosage_form:
            keywords = keys
            break
    
    if not keywords:
        return dosage_text
    
    sections = re.split(r'(?:\n|\s+)(?=\d+[\.、])', dosage_text)
    
    filtered_sections = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        for keyword in keywords:
            if keyword in section:
                filtered_sections.append(section)
                break
    
    if filtered_sections:
        return '\n'.join(filtered_sections)
    
    return dosage_text

def summarize_pharmacokinetics(text, max_length=100):
    """专门处理药代动力学的精简 - 提取药动学关键参数"""
    if not text:
        return text
    
    # 优先提取药动学部分（第二部分）
    pk_section = ""
    
    # 查找药动学部分 - 支持多种格式
    pk_match = re.search(r'[⑵\s]*药动学[：:\s]*(.+)', text, re.DOTALL)
    if pk_match:
        pk_section = pk_match.group(1).strip()
    
    # 如果没有找到药动学部分，使用整个文本
    if not pk_section:
        pk_section = text
    
    # 清理HTML标签和特殊空格
    pk_section = re.sub(r'<[^>]+>', '', pk_section)
    pk_section = re.sub(r'[　\s]+', ' ', pk_section)
    
    # 提取关键药动学参数
    key_params = []
    
    # 1. 达峰时间 (Tmax/ｔmax) - 支持全角和半角
    tmax_patterns = [
        r'(?:达峰时间|ｔmax|tmax)[^\d]*([\d\.]+\s*(?:±\s*[\d\.]+)?\s*(?:h|小时|min|分钟|分))',
        r'(?:时间)[^\d]*(?:ｔmax|tmax)[^\d]*([\d\.]+\s*(?:±\s*[\d\.]+)?\s*(?:h|小时|min|分钟|分))',
    ]
    for pattern in tmax_patterns:
        tmax_match = re.search(pattern, pk_section, re.IGNORECASE)
        if tmax_match:
            key_params.append(f"达峰时间{tmax_match.group(1)}")
            break
    
    # 2. 峰浓度 (Cmax/ｃmax) - 支持全角和半角
    cmax_patterns = [
        r'(?:峰浓度|最高血药浓度|Cmax|ｃmax)[^\d]*([\d\.]+(?:\s*±\s*[\d\.]+)?(?:\s*-\s*[\d\.]+)?\s*(?:ng|μg|mg|g)?/?(?:ml|L)?)',
        r'Cmax[^\d]*([\d\.]+(?:\s*±\s*[\d\.]+)?(?:\s*、\s*[\d\.]+)?\s*(?:ng|μg|mg|g)?/?(?:ml|L)?)',
    ]
    for pattern in cmax_patterns:
        cmax_match = re.search(pattern, pk_section, re.IGNORECASE)
        if cmax_match:
            key_params.append(f"峰浓度{cmax_match.group(1)}")
            break
    
    # 3. 半衰期
    half_life_match = re.search(r'(?:半衰期|消除半衰期)[^\d]*([\d\.]+\s*(?:±\s*[\d\.]+)?\s*(?:h|小时|min|分钟|分))', pk_section, re.IGNORECASE)
    if half_life_match:
        key_params.append(f"半衰期{half_life_match.group(1)}")
    
    # 4. 生物利用度
    bio_match = re.search(r'(?:生物利用度)[^\d]*([\d\.]+)', pk_section, re.IGNORECASE)
    if bio_match:
        key_params.append(f"生物利用度{bio_match.group(1)}%")
    
    # 5. 蛋白结合率
    protein_match = re.search(r'(?:蛋白结合率)[^\d]*([\d\.]+)', pk_section, re.IGNORECASE)
    if protein_match:
        key_params.append(f"蛋白结合率{protein_match.group(1)}%")
    
    if key_params:
        result = '，'.join(key_params[:3])
        if len(result) > max_length:
            result = result[:max_length-3] + '...'
        return result
    
    # 如果没有提取到参数，返回药动学部分的前80字符
    if pk_section:
        return pk_section[:max_length-3] + '...' if len(pk_section) > max_length else pk_section
    
    return text[:max_length-3] + '...' if len(text) > max_length else text

def generate_summary(text, field_type, max_length=100):
    """生成精简版内容"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    # 药代动力学特殊处理
    if field_type == 'pharmacokinetics':
        return summarize_pharmacokinetics(text, max_length)
    
    # 其他字段使用通用精简
    lines = re.split(r'(?:<br>|\n|\s+(?=\d+[\.、])|\s+(?=[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽]))', text)
    
    key_points = []
    total_length = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
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

def main():
    drug_id = 7
    drug_name = '氟尿嘧啶'
    url = 'https://www.hnysfww.com/goods.php?id=2482'
    dosage_form = '注射液'
    
    print(f"正在更新: {drug_name} (ID: {drug_id})")
    print(f"网址: {url}")
    
    html = get_website_content(url)
    if not html:
        print(f"❌ 无法获取网站内容")
        return False
    
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
    
    has_content = any(v for v in fields.values() if v)
    if not has_content:
        print(f"❌ 未找到任何内容")
        return False
    
    print(f"✅ 成功获取数据")
    for key, value in fields.items():
        if value:
            print(f"  - {key}: {len(value)} 字符")
    
    # 更新JSON
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug_id}.json'
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug = json.load(f)
        
        if 'manual' not in drug:
            drug['manual'] = {}
        
        # 根据剂型筛选用法用量
        full_dosage = fields.get('dosage', '')
        filtered_dosage = filter_dosage_by_form(full_dosage, dosage_form)
        
        # 更新精简版字段
        drug['manual']['indications'] = generate_summary(fields.get('indications', ''), 'indications')
        drug['manual']['dosage'] = generate_summary(filtered_dosage, 'dosage')
        drug['manual']['contraindications'] = generate_summary(fields.get('contraindications', ''), 'contraindications')
        drug['manual']['adverse_reactions'] = generate_summary(fields.get('adverse_reactions', ''), 'adverse_reactions')
        drug['manual']['interactions'] = generate_summary(fields.get('interactions', ''), 'interactions')
        drug['manual']['pregnancy_category'] = fields.get('pregnancy_category', '')
        drug['manual']['pharmacokinetics'] = generate_summary(fields.get('pharmacokinetics', ''), 'pharmacokinetics')
        drug['manual']['precautions'] = generate_summary(fields.get('precautions', ''), 'precautions')
        drug['manual']['source'] = '湖南药事服务网'
        
        # 添加完整版字段
        drug['manual']['full_indications'] = escape_for_json(fields.get('indications', ''))
        drug['manual']['full_dosage'] = escape_for_json(filtered_dosage)
        drug['manual']['full_contraindications'] = escape_for_json(fields.get('contraindications', ''))
        drug['manual']['full_adverse_reactions'] = escape_for_json(fields.get('adverse_reactions', ''))
        drug['manual']['full_interactions'] = escape_for_json(fields.get('interactions', ''))
        drug['manual']['full_pharmacokinetics'] = escape_for_json(fields.get('pharmacokinetics', ''))
        drug['manual']['full_precautions'] = escape_for_json(fields.get('precautions', ''))
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已更新文件")
        return True
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()
