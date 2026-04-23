#!/usr/bin/env python3
"""批量获取第一批次所有药品的网站内容并更新到数据库"""

import re
import subprocess
import json

# 第一批次药品列表
BATCH_1_DRUGS = [
    {"seq": 1, "name": "氟尿嘧啶", "url": "https://www.hnysfww.com/goods.php?id=2482"},
    {"seq": 2, "name": "盐酸贝尼地平", "url": "https://www.hnysfww.com/goods.php?id=176"},
    {"seq": 3, "name": "※▲安奈拉唑钠", "url": "https://www.hnysfww.com/goods.php?id=13642"},
    {"seq": 4, "name": "※▲芦比前列酮软", "url": "https://www.hnysfww.com/goods.php?id=13662"},
    {"seq": 5, "name": "氢溴酸替格列汀", "url": "https://www.hnysfww.com/goods.php?id=13329"},
    {"seq": 6, "name": "※▲妥布霉素吸入溶液", "url": "https://www.hnysfww.com/goods.php?id=1983"},
    {"seq": 7, "name": "注射用头孢西丁钠/氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1904"},
    {"seq": 8, "name": "※▲注射用头孢他啶阿维巴坦钠", "url": "https://www.hnysfww.com/goods.php?id=1954"},
    {"seq": 9, "name": "※▲注射用紫杉醇聚合物胶束", "url": "https://www.hnysfww.com/goods.php?id=13853"},
    {"seq": 10, "name": "※▲注射用替加环素", "url": "https://www.hnysfww.com/goods.php?id=2035"},
    {"seq": 11, "name": "注射用鼠神经生长因子", "url": "https://www.hnysfww.com/goods.php?id=1080"},
    {"seq": 12, "name": "※▲甲苯磺酸艾多沙班", "url": "https://www.hnysfww.com/goods.php?id=11184"},
    {"seq": 13, "name": "依洛尤单抗", "url": "https://www.hnysfww.com/goods.php?id=7923"},
    {"seq": 14, "name": "吲哚美辛栓", "url": "https://www.hnysfww.com/goods.php?id=2690"},
    {"seq": 15, "name": "葆宫止血", "url": "https://www.hnysfww.com/goods.php?id=5852"},
    {"seq": 16, "name": "呋麻", "url": "https://www.hnysfww.com/goods.php?id=3038"},
    {"seq": 17, "name": "硫酸特布他林雾化吸入用溶液", "url": "https://www.hnysfww.com/goods.php?id=1605"},
    {"seq": 18, "name": "华蟾素", "url": "https://www.hnysfww.com/goods.php?id=7584"},
    {"seq": 19, "name": "复方对乙酰氨基酚", "url": "https://www.hnysfww.com/goods.php?id=7934"},
    {"seq": 20, "name": "紫杉醇", "url": "https://www.hnysfww.com/goods.php?id=2546"},
]

def fetch_drug_content(url):
    """获取药品网站内容"""
    try:
        result = subprocess.run(
            ['curl', '-s', url, '--max-time', '30'],
            capture_output=True,
            text=True,
            timeout=35
        )
        return result.stdout
    except Exception as e:
        print(f"    ❌ 获取失败: {e}")
        return None

def extract_fields(html):
    """从HTML中提取药品字段"""
    fields = {}
    
    # 字段映射
    field_patterns = {
        'indications': r'适应证[\s\S]*?<td[^>]*>(.*?)</td>',
        'dosage': r'用法与用量[\s\S]*?<td[^>]*>(.*?)</td>',
        'contraindications': r'禁忌症[\s\S]*?<td[^>]*>(.*?)</td>',
        'adverse_reactions': r'不良反应[\s\S]*?<td[^>]*>(.*?)</td>',
        'interactions': r'药物相互作用[\s\S]*?<td[^>]*>(.*?)</td>',
        'pregnancy_category': r'妊娠期用药安全分级[\s\S]*?<td[^>]*>(.*?)</td>',
        'pharmacokinetics': r'药理作用[\s\S]*?<td[^>]*>(.*?)</td>',
        'precautions': r'注意事项[\s\S]*?<td[^>]*>(.*?)</td>',
    }
    
    for field, pattern in field_patterns.items():
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            content = match.group(1)
            # 清理HTML标签但保留<br>
            content = re.sub(r'<br\s*/?>', '\n', content)
            content = re.sub(r'<sub>(.*?)</sub>', r'\1', content)
            content = re.sub(r'<sup>(.*?)</sup>', r'\1', content)
            content = re.sub(r'<[^>]+>', '', content)
            # 清理多余空白
            content = re.sub(r'\n\s*\n', '\n', content)
            content = content.strip()
            if content:
                fields[field] = content
    
    return fields

def main():
    print("=" * 80)
    print("第一批次药品网站内容获取")
    print("=" * 80)
    
    all_drug_data = {}
    
    for drug in BATCH_1_DRUGS:
        print(f"\n{drug['seq']:2d}. {drug['name']}")
        print(f"    网址: {drug['url']}")
        
        html = fetch_drug_content(drug['url'])
        if not html:
            print("    ❌ 无法获取网站内容")
            all_drug_data[drug['name']] = {'error': '无法获取网站内容'}
            continue
        
        fields = extract_fields(html)
        
        if not fields:
            print("    ⚠️ 未能提取到字段内容")
            all_drug_data[drug['name']] = {'error': '未能提取字段'}
            continue
        
        print(f"    ✅ 成功提取 {len(fields)} 个字段:")
        for field, value in fields.items():
            preview = value[:40].replace('\n', ' ') + '...' if len(value) > 40 else value.replace('\n', ' ')
            print(f"      - {field}: {preview}")
        
        all_drug_data[drug['name']] = {
            'seq': drug['seq'],
            'url': drug['url'],
            'fields': fields
        }
    
    # 保存到JSON文件
    output_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/第一批次网站原始内容.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_drug_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("汇总")
    print("=" * 80)
    success = len([d for d in all_drug_data.values() if 'fields' in d])
    failed = len([d for d in all_drug_data.values() if 'error' in d])
    print(f"成功获取: {success} 个")
    print(f"获取失败: {failed} 个")
    print(f"\n数据已保存到: {output_file}")
    print("\n下一步：请检查此文件，确认内容正确后，我将更新到数据库")

if __name__ == '__main__':
    main()
