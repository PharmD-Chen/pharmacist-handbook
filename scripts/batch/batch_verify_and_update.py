#!/usr/bin/env python3
"""第一批次药品逐一核对并更新 - 按艾多沙班方式"""

import re
import subprocess
import json

# 第一批次药品列表（20个）
BATCH_1_DRUGS = [
    {"seq": 1, "name": "氟尿嘧啶", "url": "https://www.hnysfww.com/goods.php?id=2482", "id": 12},
    {"seq": 2, "name": "盐酸贝尼地平", "url": "https://www.hnysfww.com/goods.php?id=176", "id": 13},
    {"seq": 3, "name": "※▲安奈拉唑钠", "url": "https://www.hnysfww.com/goods.php?id=13642", "id": None},
    {"seq": 4, "name": "※▲芦比前列酮软", "url": "https://www.hnysfww.com/goods.php?id=13662", "id": None},
    {"seq": 5, "name": "氢溴酸替格列汀", "url": "https://www.hnysfww.com/goods.php?id=13329", "id": None},
    {"seq": 6, "name": "※▲妥布霉素吸入溶液", "url": "https://www.hnysfww.com/goods.php?id=1983", "id": None},
    {"seq": 7, "name": "注射用头孢西丁钠/氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1904", "id": None},
    {"seq": 8, "name": "※▲注射用头孢他啶阿维巴坦钠", "url": "https://www.hnysfww.com/goods.php?id=1954", "id": None},
    {"seq": 9, "name": "※▲注射用紫杉醇聚合物胶束", "url": "https://www.hnysfww.com/goods.php?id=13853", "id": None},
    {"seq": 10, "name": "※▲注射用替加环素", "url": "https://www.hnysfww.com/goods.php?id=2035", "id": None},
    {"seq": 11, "name": "注射用鼠神经生长因子", "url": "https://www.hnysfww.com/goods.php?id=1080", "id": None},
    {"seq": 12, "name": "※▲甲苯磺酸艾多沙班", "url": "https://www.hnysfww.com/goods.php?id=11184", "id": None},
    {"seq": 13, "name": "依洛尤单抗", "url": "https://www.hnysfww.com/goods.php?id=7923", "id": None},
    {"seq": 14, "name": "吲哚美辛栓", "url": "https://www.hnysfww.com/goods.php?id=2690", "id": None},
    {"seq": 15, "name": "葆宫止血", "url": "https://www.hnysfww.com/goods.php?id=5852", "id": None},
    {"seq": 16, "name": "呋麻", "url": "https://www.hnysfww.com/goods.php?id=3038", "id": None},
    {"seq": 17, "name": "硫酸特布他林雾化吸入用溶液", "url": "https://www.hnysfww.com/goods.php?id=1605", "id": None},
    {"seq": 18, "name": "华蟾素", "url": "https://www.hnysfww.com/goods.php?id=7584", "id": None},
    {"seq": 19, "name": "复方对乙酰氨基酚", "url": "https://www.hnysfww.com/goods.php?id=7934", "id": None},
    {"seq": 20, "name": "紫杉醇", "url": "https://www.hnysfww.com/goods.php?id=2546", "id": None},
]

def get_website_content(url):
    """从网站获取药品内容"""
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"  获取网站内容失败: {e}")
        return None

def extract_field_from_html(html, field_name):
    """从HTML中提取特定字段"""
    if not html:
        return None
    
    # 根据字段名构建不同的匹配模式
    patterns = {
        'indications': r'适应证[\s\S]*?<td[^>]*>(.*?)</td>',
        'dosage': r'用法与用量[\s\S]*?<td[^>]*>(.*?)</td>',
        'contraindications': r'禁忌症[\s\S]*?<td[^>]*>(.*?)</td>',
        'adverse_reactions': r'不良反应[\s\S]*?<td[^>]*>(.*?)</td>',
        'interactions': r'药物相互作用[\s\S]*?<td[^>]*>(.*?)</td>',
        'pregnancy_category': r'妊娠期用药安全分级[\s\S]*?<td[^>]*>(.*?)</td>',
        'pharmacokinetics': r'药理作用[\s\S]*?<td[^>]*>(.*?)</td>',
        'precautions': r'注意事项[\s\S]*?<td[^>]*>(.*?)</td>',
    }
    
    pattern = patterns.get(field_name, rf'{field_name}[\s\S]*?<td[^>]*>(.*?)</td>')
    match = re.search(pattern, html, re.IGNORECASE)
    
    if match:
        content = match.group(1)
        # 清理HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        # 清理多余空白
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    return None

def check_drug_content(drug, html_content):
    """检查药品内容是否需要更新"""
    fields_to_check = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                       'interactions', 'pharmacokinetics', 'precautions']
    
    website_data = {}
    for field in fields_to_check:
        value = extract_field_from_html(html_content, field)
        if value:
            website_data[field] = value
    
    return website_data

def main():
    print("=" * 80)
    print("第一批次药品逐一核对（按艾多沙班方式）")
    print("=" * 80)
    
    results = []
    
    for drug in BATCH_1_DRUGS:
        print(f"\n{drug['seq']:2d}. {drug['name']}")
        print(f"    网址: {drug['url']}")
        
        # 获取网站内容
        html = get_website_content(drug['url'])
        if not html:
            print("    ❌ 无法获取网站内容")
            results.append({
                'seq': drug['seq'],
                'name': drug['name'],
                'status': '无法获取网站内容',
                'needs_update': False
            })
            continue
        
        # 提取网站字段
        website_data = check_drug_content(drug, html)
        
        if not website_data:
            print("    ⚠️  网站内容解析失败")
            results.append({
                'seq': drug['seq'],
                'name': drug['name'],
                'status': '网站内容解析失败',
                'needs_update': False
            })
            continue
        
        print(f"    网站获取到的字段:")
        for field, value in website_data.items():
            preview = value[:50] + '...' if len(value) > 50 else value
            print(f"      - {field}: {preview}")
        
        results.append({
            'seq': drug['seq'],
            'name': drug['name'],
            'url': drug['url'],
            'status': '已获取网站内容',
            'website_data': website_data,
            'needs_update': True
        })
    
    # 保存结果到文件
    report_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/第一批次网站内容获取报告.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("汇总")
    print("=" * 80)
    success_count = len([r for r in results if r.get('needs_update')])
    fail_count = len([r for r in results if not r.get('needs_update')])
    print(f"成功获取: {success_count} 个")
    print(f"获取失败: {fail_count} 个")
    print(f"\n详细报告已保存到: {report_file}")
    
    return results

if __name__ == '__main__':
    main()
