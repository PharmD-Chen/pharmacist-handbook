#!/usr/bin/env python3
"""批量抓取已有网址但缺少详细信息的药品"""

import json
import re
import time
import urllib.request
from pathlib import Path

def load_drug_index():
    """加载药品索引"""
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_url_list():
    """从药品网址汇总文件解析药品和网址"""
    url_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md'
    
    drugs_with_url = []
    seen_urls = set()
    
    with open(url_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 格式1: 列表格式 `- 药品名 https://...`
    pattern1 = r'-\s*([^\n]+?)\s+(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    matches1 = re.findall(pattern1, content)
    
    for drug_name, url in matches1:
        if url not in seen_urls:
            seen_urls.add(url)
            clean_name = re.sub(r'^[※▲]+', '', drug_name).strip()
            drugs_with_url.append({
                'name': clean_name,
                'url': url
            })
    
    # 格式2: 表格格式 `| 序号 | 药品名 | 剂型 | 规格 | [链接](https://...) |`
    pattern2 = r'\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*\[链接\]\((https://www\.hnysfww\.com/goods\.php\?id=\d+)\)\s*\|'
    matches2 = re.findall(pattern2, content)
    
    for drug_name, dosage_form, spec, url in matches2:
        if url not in seen_urls:
            seen_urls.add(url)
            clean_name = re.sub(r'^[※▲]+', '', drug_name).strip()
            drugs_with_url.append({
                'name': clean_name,
                'url': url
            })
    
    return drugs_with_url

def check_drug_has_manual(drug_id):
    """检查药品是否已有手册数据"""
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug_id}.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug = json.load(f)
        manual = drug.get('manual', {})
        return bool(manual.get('full_indications') or manual.get('full_dosage'))
    except:
        return False

def find_drug_by_name(drug_index, name):
    """根据名称查找药品信息 - 支持模糊匹配"""
    clean_name = re.sub(r'^[※▲]+', '', name).strip()
    
    for drug in drug_index:
        drug_clean_name = re.sub(r'^[※▲]+', '', drug['name']).strip()
        if drug_clean_name == clean_name:
            return drug
    
    for drug in drug_index:
        drug_clean_name = re.sub(r'^[※▲]+', '', drug['name']).strip()
        if clean_name in drug_clean_name or drug_clean_name in clean_name:
            return drug
    
    return None

def get_website_content(url):
    """获取网站内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"   获取失败: {e}")
        return None

def extract_field(html, field_name):
    """从HTML中提取字段内容"""
    patterns = [
        rf'<td[^>]*>.*?{field_name}.*?</td>\s*<td[^>]*>(.*?)</td>',
        rf'{field_name}[:：]\s*(.*?)(?:<|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\s+', ' ', content).strip()
            return content
    
    return None

def summarize_pharmacokinetics(text):
    """提取药代动力学关键参数"""
    if not text:
        return text
    
    result = []
    
    patterns = {
        '达峰时间': r'达峰时间.*?([\d\.]+\s*(?:h|小时))',
        'Tmax': r'Tmax.*?([\d\.]+\s*(?:h|小时))',
        '峰浓度': r'峰浓度.*?([\d\.]+\s*[^\s,，]+)',
        'Cmax': r'Cmax.*?([\d\.]+\s*[^\s,，]+)',
        '半衰期': r'半衰期.*?([\d\.]+\s*(?:h|小时))',
        't1/2': r't1/2.*?([\d\.]+\s*(?:h|小时))',
        '生物利用度': r'生物利用度.*?([\d\.]+\s*%)',
        '蛋白结合率': r'蛋白结合率.*?([\d\.]+\s*%)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result.append(f"{key}: {match.group(1)}")
    
    return '; '.join(result) if result else text[:200]

def filter_dosage_by_form(dosage_text, dosage_form):
    """根据剂型筛选用法用量"""
    if not dosage_text:
        return dosage_text
    
    dosage_form = dosage_form.lower() if dosage_form else ''
    
    if any(x in dosage_form for x in ['片', '胶囊', '颗粒', '丸', '散', '口服']):
        keywords = ['口服', '吞服', '餐前', '餐后', '空腹']
    elif any(x in dosage_form for x in ['注射', '输液']):
        keywords = ['静脉', '肌内', '皮下', '注射', '滴注', '输注']
    elif any(x in dosage_form for x in ['软膏', '乳膏', '凝胶', '贴剂', '外用']):
        keywords = ['外用', '涂抹', '敷贴', '局部']
    else:
        return dosage_text[:500]
    
    lines = dosage_text.split('\n')
    filtered = []
    for line in lines:
        if any(kw in line for kw in keywords):
            filtered.append(line)
    
    return '\n'.join(filtered[:10]) if filtered else dosage_text[:500]

def extract_key_points(text):
    """提取关键要点，去除说明性文字"""
    if not text:
        return text
    
    text = re.sub(r'请?患者?注意', '', text)
    text = re.sub(r'建议', '', text)
    text = re.sub(r'应该', '', text)
    text = re.sub(r'因为[^。]+', '', text)
    text = re.sub(r'可能[^。]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text[:300]

def fetch_and_update_drug(drug, url, dosage_form):
    """获取并更新药品信息"""
    print(f"\n正在处理: {drug['name']} (ID: {drug['id']})")
    print(f"网址: {url}")
    
    html = get_website_content(url)
    if not html:
        print(f"   ❌ 无法获取网站内容")
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
    
    # 更新药品JSON
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug["id"]}.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
    except:
        print(f"   ❌ 无法读取药品JSON文件")
        return False
    
    if 'manual' not in drug_data:
        drug_data['manual'] = {}
    
    manual = drug_data['manual']
    
    # 更新字段
    if fields['indications']:
        manual['full_indications'] = fields['indications']
        manual['indications'] = extract_key_points(fields['indications'])
    
    if fields['dosage']:
        manual['full_dosage'] = fields['dosage']
        manual['dosage'] = filter_dosage_by_form(fields['dosage'], dosage_form)
    
    if fields['contraindications']:
        manual['full_contraindications'] = fields['contraindications']
        manual['contraindications'] = extract_key_points(fields['contraindications'])
    
    if fields['adverse_reactions']:
        manual['full_adverse_reactions'] = fields['adverse_reactions']
        manual['adverse_reactions'] = extract_key_points(fields['adverse_reactions'])
    
    if fields['interactions']:
        manual['full_interactions'] = fields['interactions']
        manual['interactions'] = extract_key_points(fields['interactions'])
    
    if fields['pregnancy_category']:
        manual['pregnancy_category'] = fields['pregnancy_category']
    
    if fields['pharmacokinetics']:
        manual['full_pharmacokinetics'] = fields['pharmacokinetics']
        manual['pharmacokinetics'] = summarize_pharmacokinetics(fields['pharmacokinetics'])
    
    if fields['precautions']:
        manual['full_precautions'] = fields['precautions']
        manual['precautions'] = extract_key_points(fields['precautions'])
    
    # 保存
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 已更新药品 ID {drug['id']}: {drug['name']}")
    return True

def main():
    print("=" * 60)
    print("批量抓取药品详细信息")
    print("=" * 60)
    
    print("\n加载药品索引...")
    drug_index = load_drug_index()
    print(f"✅ 共 {len(drug_index)} 个药品")
    
    print("\n解析药品网址...")
    drugs_with_url = parse_url_list()
    print(f"✅ 找到 {len(drugs_with_url)} 个有网址的药品")
    
    # 过滤掉已经处理过的药品
    drugs_to_process = []
    for item in drugs_with_url:
        drug = find_drug_by_name(drug_index, item['name'])
        if drug and not check_drug_has_manual(drug['id']):
            drugs_to_process.append({
                'drug': drug,
                'url': item['url']
            })
    
    print(f"📝 待处理: {len(drugs_to_process)} 个")
    
    if not drugs_to_process:
        print("\n✅ 所有药品都已处理完毕！")
        return
    
    print("\n开始批量抓取...")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, item in enumerate(drugs_to_process, 1):
        print(f"\n[{i}/{len(drugs_to_process)}] ", end="")
        
        drug = item['drug']
        url = item['url']
        dosage_form = drug.get('dosage_form', '')
        
        if fetch_and_update_drug(drug, url, dosage_form):
            success_count += 1
        else:
            fail_count += 1
        
        # 添加延迟避免请求过快
        if i < len(drugs_to_process):
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("完成！")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📊 总计: {len(drugs_to_process)}")

if __name__ == '__main__':
    main()
