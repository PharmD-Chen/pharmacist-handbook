#!/usr/bin/env python3
"""修正第一批次所有药品 - 严格按照网站内容"""

import re
import subprocess

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
            ['curl', '-s', url, '--max-time', '30'],
            capture_output=True,
            text=True,
            timeout=35
        )
        return result.stdout
    except:
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

def update_drug_in_db(drug_name, fields):
    """更新数据库中的药品内容"""
    print(f"\n正在更新 {drug_name}...")
    
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
    
    # 构建新的 manual
    manual_lines = ['"manual": {']
    if indications:
        manual_lines.append(f'      "indications": "{indications}",')
        manual_lines.append(f'      "full_indications": "{indications}",')
    if dosage:
        manual_lines.append(f'      "dosage": "{dosage}",')
        manual_lines.append(f'      "full_dosage": "{dosage}",')
    if contraindications:
        manual_lines.append(f'      "contraindications": "{contraindications}",')
        manual_lines.append(f'      "full_contraindications": "{contraindications}",')
    if adverse:
        manual_lines.append(f'      "adverse_reactions": "{adverse}",')
        manual_lines.append(f'      "full_adverse_reactions": "{adverse}",')
    if interactions:
        manual_lines.append(f'      "interactions": "{interactions}",')
        manual_lines.append(f'      "full_interactions": "{interactions}",')
    if pregnancy:
        manual_lines.append(f'      "pregnancy_category": "{pregnancy}",')
        manual_lines.append(f'      "full_pregnancy_category": "{pregnancy}",')
    if pharma:
        manual_lines.append(f'      "pharmacokinetics": "{pharma}",')
        manual_lines.append(f'      "full_pharmacokinetics": "{pharma}",')
    if precautions:
        manual_lines.append(f'      "precautions": "{precautions}",')
        manual_lines.append(f'      "full_precautions": "{precautions}",')
    manual_lines.append(f'      "source": "{source}"')
    manual_lines.append('    }')
    
    new_manual = '\n'.join(manual_lines)
    
    # 替换匹配的记录
    # 处理带※▲前缀的名称
    search_name = drug_name.replace('※▲', '')
    pattern = rf'("name":\s*"(?:※▲)?{re.escape(search_name)}[^"]*"[\s\S]*?"spec_count":\s*\d+,\s*)"manual":\s*\{{[\s\S]*?\}}(\s*,\s*"pinyin")'
    
    matches = list(re.finditer(pattern, content))
    print(f"  找到 {len(matches)} 个记录")
    
    if not matches:
        print(f"  ⚠️ 未找到 {drug_name} 的记录")
        return False
    
    def replace_manual(match):
        return match.group(1) + new_manual + match.group(2)
    
    new_content = re.sub(pattern, replace_manual, content)
    
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ 已更新 {len(matches)} 个记录")
    return True

def process_drug(seq, name, url):
    """处理单个药品"""
    print(f"\n{'='*80}")
    print(f"{seq:2d}. {name}")
    print(f"{'='*80}")
    print(f"网址: {url}")
    
    html = get_website_content(url)
    if not html:
        print("❌ 无法获取网站内容")
        return False
    
    # 提取各字段
    fields = {}
    fields['indications'] = extract_field(html, '适应证')
    fields['dosage'] = extract_field(html, '用法与用量')
    fields['contraindications'] = extract_field(html, '禁忌症')
    fields['adverse_reactions'] = extract_field(html, '不良反应')
    fields['interactions'] = extract_field(html, '药物相互作用')
    fields['pregnancy_category'] = extract_field(html, '妊娠期用药安全分级')
    fields['pharmacokinetics'] = extract_field(html, '药理作用')
    fields['precautions'] = extract_field(html, '注意事项')
    
    # 过滤空值
    fields = {k: v for k, v in fields.items() if v}
    
    if not fields:
        print("⚠️ 未能提取到任何字段")
        return False
    
    print(f"\n提取到的字段 ({len(fields)} 个):")
    for field, value in fields.items():
        preview = value[:60].replace('\n', ' ') + '...' if len(value) > 60 else value.replace('\n', ' ')
        print(f"  - {field}: {preview}")
    
    # 更新到数据库
    return update_drug_in_db(name, fields)

def main():
    # 第一批次药品（需要更新的）
    drugs_to_update = [
        (1, "氟尿嘧啶", "https://www.hnysfww.com/goods.php?id=2482"),
        (2, "盐酸贝尼地平", "https://www.hnysfww.com/goods.php?id=176"),
        (3, "※▲安奈拉唑钠", "https://www.hnysfww.com/goods.php?id=13642"),
        (4, "※▲芦比前列酮软", "https://www.hnysfww.com/goods.php?id=13662"),
        (5, "氢溴酸替格列汀", "https://www.hnysfww.com/goods.php?id=13329"),
        (6, "※▲妥布霉素吸入溶液", "https://www.hnysfww.com/goods.php?id=1983"),
        (7, "注射用头孢西丁钠/氯化钠", "https://www.hnysfww.com/goods.php?id=1904"),
        (8, "※▲注射用头孢他啶阿维巴坦钠", "https://www.hnysfww.com/goods.php?id=1954"),
        (9, "※▲注射用紫杉醇聚合物胶束", "https://www.hnysfww.com/goods.php?id=13853"),
        (10, "※▲注射用替加环素", "https://www.hnysfww.com/goods.php?id=2035"),
        (11, "注射用鼠神经生长因子", "https://www.hnysfww.com/goods.php?id=1080"),
        # 12号艾多沙班已经更新过
        (13, "依洛尤单抗", "https://www.hnysfww.com/goods.php?id=7923"),
        (14, "吲哚美辛栓", "https://www.hnysfww.com/goods.php?id=2690"),
        (15, "葆宫止血", "https://www.hnysfww.com/goods.php?id=5852"),
        (16, "呋麻", "https://www.hnysfww.com/goods.php?id=3038"),
        (17, "硫酸特布他林雾化吸入用溶液", "https://www.hnysfww.com/goods.php?id=1605"),
        (18, "华蟾素", "https://www.hnysfww.com/goods.php?id=7584"),
        (19, "复方对乙酰氨基酚", "https://www.hnysfww.com/goods.php?id=7934"),
        (20, "紫杉醇", "https://www.hnysfww.com/goods.php?id=2546"),
    ]
    
    print("=" * 80)
    print("第一批次药品逐一核对更新")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for seq, name, url in drugs_to_update:
        if process_drug(seq, name, url):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 80)
    print("汇总")
    print("=" * 80)
    print(f"成功更新: {success_count} 个")
    print(f"更新失败: {fail_count} 个")
    print("\n所有药品已按照网站原始内容进行更新！")

if __name__ == '__main__':
    main()
