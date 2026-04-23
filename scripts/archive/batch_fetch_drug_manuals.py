#!/usr/bin/env python3
"""批量抓取药品说明书内容"""

import re
import subprocess
import json
import os
import time

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

def fetch_drug_manual(drug_name, url):
    """抓取单个药品的说明书"""
    print(f"\n正在抓取: {drug_name}")
    print(f"网址: {url}")
    
    html = get_website_content(url)
    if not html:
        print(f"❌ 无法获取 {drug_name} 的网站内容")
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
    
    # 检查是否有内容
    has_content = any(v for v in fields.values() if v)
    if not has_content:
        print(f"⚠️ {drug_name} 未找到任何内容")
        return None
    
    print(f"✅ 成功获取 {drug_name} 的数据")
    for key, value in fields.items():
        if value:
            print(f"  - {key}: {len(value)} 字符")
    
    return fields

def update_drug_json(drug_id, manual_data):
    """更新药品JSON文件"""
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug_id}.json'
    
    if not os.path.exists(json_path):
        print(f"❌ 找不到文件: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug = json.load(f)
        
        # 更新manual字段
        if 'manual' not in drug:
            drug['manual'] = {}
        
        # 更新精简版字段
        drug['manual']['indications'] = generate_summary(manual_data.get('indications', ''), 'indications')
        drug['manual']['dosage'] = generate_summary(manual_data.get('dosage', ''), 'dosage')
        drug['manual']['contraindications'] = generate_summary(manual_data.get('contraindications', ''), 'contraindications')
        drug['manual']['adverse_reactions'] = generate_summary(manual_data.get('adverse_reactions', ''), 'adverse_reactions')
        drug['manual']['interactions'] = generate_summary(manual_data.get('interactions', ''), 'interactions')
        drug['manual']['pregnancy_category'] = manual_data.get('pregnancy_category', '')
        drug['manual']['pharmacokinetics'] = generate_summary(manual_data.get('pharmacokinetics', ''), 'pharmacokinetics')
        drug['manual']['precautions'] = generate_summary(manual_data.get('precautions', ''), 'precautions')
        drug['manual']['source'] = '湖南药事服务网'
        
        # 添加完整版字段
        drug['manual']['full_indications'] = escape_for_json(manual_data.get('indications', ''))
        drug['manual']['full_dosage'] = escape_for_json(manual_data.get('dosage', ''))
        drug['manual']['full_contraindications'] = escape_for_json(manual_data.get('contraindications', ''))
        drug['manual']['full_adverse_reactions'] = escape_for_json(manual_data.get('adverse_reactions', ''))
        drug['manual']['full_interactions'] = escape_for_json(manual_data.get('interactions', ''))
        drug['manual']['full_pharmacokinetics'] = escape_for_json(manual_data.get('pharmacokinetics', ''))
        drug['manual']['full_precautions'] = escape_for_json(manual_data.get('precautions', ''))
        
        # 保存
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(drug, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"❌ 更新文件失败: {e}")
        return False

def load_drug_index():
    """加载药品索引"""
    index_path = '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/index.json'
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_url_list():
    """从药品网址汇总文件解析药品和网址"""
    url_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md'
    
    drugs_with_url = []
    
    with open(url_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配格式: - 药品名称 https://www.hnysfww.com/goods.php?id=xxx
    pattern = r'-\s*([^\n]+?)\s+(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    matches = re.findall(pattern, content)
    
    for drug_name, url in matches:
        # 清理药品名称（去除特殊标记）
        clean_name = re.sub(r'^[※▲]+', '', drug_name).strip()
        drugs_with_url.append({
            'name': clean_name,
            'url': url
        })
    
    return drugs_with_url

def find_drug_id_by_name(drug_index, name):
    """根据名称查找药品ID"""
    for drug in drug_index:
        if drug['name'] == name:
            return drug['id']
    return None

def main():
    print("=" * 60)
    print("批量抓取药品说明书")
    print("=" * 60)
    
    # 加载索引
    print("\n加载药品索引...")
    drug_index = load_drug_index()
    print(f"✅ 共 {len(drug_index)} 个药品")
    
    # 解析网址列表
    print("\n解析药品网址...")
    drugs_with_url = parse_url_list()
    print(f"✅ 找到 {len(drugs_with_url)} 个有网址的药品")
    
    # 抓取数据
    success_count = 0
    fail_count = 0
    
    for i, drug_info in enumerate(drugs_with_url, 1):
        print(f"\n[{i}/{len(drugs_with_url)}] ", end='')
        
        # 查找药品ID
        drug_id = find_drug_id_by_name(drug_index, drug_info['name'])
        if not drug_id:
            print(f"⚠️ 未找到药品: {drug_info['name']}")
            fail_count += 1
            continue
        
        # 抓取数据
        manual_data = fetch_drug_manual(drug_info['name'], drug_info['url'])
        if not manual_data:
            fail_count += 1
            continue
        
        # 更新JSON文件
        if update_drug_json(drug_id, manual_data):
            success_count += 1
            print(f"✅ 已更新药品 ID {drug_id}: {drug_info['name']}")
        else:
            fail_count += 1
        
        # 延迟，避免请求过快
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
