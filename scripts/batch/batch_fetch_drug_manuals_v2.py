#!/usr/bin/env python3
"""批量抓取药品说明书内容 - 优化版"""

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
    
    # 定义剂型关键词映射
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
    
    # 获取当前剂型的关键词
    keywords = []
    for form, keys in form_keywords.items():
        if form in dosage_form:
            keywords = keys
            break
    
    if not keywords:
        return dosage_text
    
    # 分割成不同用法
    sections = re.split(r'(?:\n|\s+)(?=\d+[\.、])', dosage_text)
    
    filtered_sections = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # 检查是否包含当前剂型的关键词
        for keyword in keywords:
            if keyword in section:
                # 提取该段落
                filtered_sections.append(section)
                break
    
    if filtered_sections:
        return '\n'.join(filtered_sections)
    
    # 如果没有匹配到，返回原文
    return dosage_text

def generate_summary(text, field_type, max_length=100):
    """生成精简版内容"""
    if not text:
        return text
    
    if len(text) <= max_length:
        return text
    
    # 药代动力学特殊处理
    if field_type == 'pharmacokinetics':
        return summarize_pharmacokinetics(text, max_length)
    
    # 分割成条目
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

def summarize_pharmacokinetics(text, max_length=100):
    """专门处理药代动力学的精简 - 提取药动学关键参数"""
    if not text:
        return text
    
    # 优先提取药动学部分（第二部分）
    pk_section = ""
    
    # 查找药动学部分 - 支持多种格式
    # 匹配 "⑵药动学：" 或 "药动学：" 后面的内容
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

def fetch_drug_manual(drug_name, url):
    """抓取单个药品的说明书"""
    print(f"\n正在抓取: {drug_name}")
    print(f"网址: {url}")
    
    html = get_website_content(url)
    if not html:
        print(f"❌ 无法获取 {drug_name} 的网站内容")
        return None
    
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
        print(f"⚠️ {drug_name} 未找到任何内容")
        return None
    
    print(f"✅ 成功获取 {drug_name} 的数据")
    for key, value in fields.items():
        if value:
            print(f"  - {key}: {len(value)} 字符")
    
    return fields

def update_drug_json(drug_id, manual_data, dosage_form):
    """更新药品JSON文件"""
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug_id}.json'
    
    if not os.path.exists(json_path):
        print(f"❌ 找不到文件: {json_path}")
        return False
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug = json.load(f)
        
        if 'manual' not in drug:
            drug['manual'] = {}
        
        # 根据剂型筛选用法用量
        full_dosage = manual_data.get('dosage', '')
        filtered_dosage = filter_dosage_by_form(full_dosage, dosage_form)
        
        # 更新精简版字段
        drug['manual']['indications'] = generate_summary(manual_data.get('indications', ''), 'indications')
        drug['manual']['dosage'] = generate_summary(filtered_dosage, 'dosage')
        drug['manual']['contraindications'] = generate_summary(manual_data.get('contraindications', ''), 'contraindications')
        drug['manual']['adverse_reactions'] = generate_summary(manual_data.get('adverse_reactions', ''), 'adverse_reactions')
        drug['manual']['interactions'] = generate_summary(manual_data.get('interactions', ''), 'interactions')
        drug['manual']['pregnancy_category'] = manual_data.get('pregnancy_category', '')
        drug['manual']['pharmacokinetics'] = generate_summary(manual_data.get('pharmacokinetics', ''), 'pharmacokinetics')
        drug['manual']['precautions'] = generate_summary(manual_data.get('precautions', ''), 'precautions')
        drug['manual']['source'] = '湖南药事服务网'
        
        # 添加完整版字段（使用筛选后的用法用量）
        drug['manual']['full_indications'] = escape_for_json(manual_data.get('indications', ''))
        drug['manual']['full_dosage'] = escape_for_json(filtered_dosage)
        drug['manual']['full_contraindications'] = escape_for_json(manual_data.get('contraindications', ''))
        drug['manual']['full_adverse_reactions'] = escape_for_json(manual_data.get('adverse_reactions', ''))
        drug['manual']['full_interactions'] = escape_for_json(manual_data.get('interactions', ''))
        drug['manual']['full_pharmacokinetics'] = escape_for_json(manual_data.get('pharmacokinetics', ''))
        drug['manual']['full_precautions'] = escape_for_json(manual_data.get('precautions', ''))
        
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
    seen_urls = set()  # 用于去重
    
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

def find_drug_by_name(drug_index, name):
    """根据名称查找药品信息 - 支持模糊匹配"""
    # 清理名称（移除特殊标记）
    clean_name = re.sub(r'^[※▲]+', '', name).strip()
    
    # 首先尝试精确匹配
    for drug in drug_index:
        drug_clean_name = re.sub(r'^[※▲]+', '', drug['name']).strip()
        if drug_clean_name == clean_name:
            return drug
    
    # 尝试包含匹配（如 "苏合香" 匹配 "※苏合香"）
    for drug in drug_index:
        drug_clean_name = re.sub(r'^[※▲]+', '', drug['name']).strip()
        if clean_name in drug_clean_name or drug_clean_name in clean_name:
            return drug
    
    return None

def check_drug_has_manual(drug_id):
    """检查药品是否已有手册数据"""
    json_path = f'/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs/{drug_id}.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            drug = json.load(f)
        manual = drug.get('manual', {})
        # 检查是否有完整版字段且有内容
        return bool(manual.get('full_indications') or manual.get('full_dosage'))
    except:
        return False

def main():
    print("=" * 60)
    print("批量抓取药品说明书 - 优化版")
    print("=" * 60)
    
    print("\n加载药品索引...")
    drug_index = load_drug_index()
    print(f"✅ 共 {len(drug_index)} 个药品")
    
    print("\n解析药品网址...")
    drugs_with_url = parse_url_list()
    print(f"✅ 找到 {len(drugs_with_url)} 个有网址的药品")
    
    # 过滤掉已经处理过的药品
    drugs_to_process = []
    skipped_count = 0
    for drug_info in drugs_with_url:
        drug = find_drug_by_name(drug_index, drug_info['name'])
        if drug and check_drug_has_manual(drug['id']):
            skipped_count += 1
        else:
            drugs_to_process.append(drug_info)
    
    print(f"⏭️  跳过已处理: {skipped_count} 个")
    print(f"📝 待处理: {len(drugs_to_process)} 个")
    
    success_count = 0
    fail_count = 0
    
    for i, drug_info in enumerate(drugs_to_process, 1):
        print(f"\n[{i}/{len(drugs_to_process)}] ", end='')
        
        drug = find_drug_by_name(drug_index, drug_info['name'])
        if not drug:
            print(f"⚠️ 未找到药品: {drug_info['name']}")
            fail_count += 1
            continue
        
        manual_data = fetch_drug_manual(drug_info['name'], drug_info['url'])
        if not manual_data:
            fail_count += 1
            continue
        
        # 传入剂型信息
        if update_drug_json(drug['id'], manual_data, drug.get('dosage_form', '')):
            success_count += 1
            print(f"✅ 已更新药品 ID {drug['id']}: {drug_info['name']}")
        else:
            fail_count += 1
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"完成！成功: {success_count}, 失败: {fail_count}, 跳过: {skipped_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
