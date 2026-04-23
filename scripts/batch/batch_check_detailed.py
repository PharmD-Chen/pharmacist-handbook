#!/usr/bin/env python3
"""详细检查第一批次药品，对比网站内容与数据库内容"""

import re

# 第一批次需要检查的药品（已有网址的）
BATCH_1_DRUGS = [
    {"seq": 1, "name": "氟尿嘧啶", "url": "https://www.hnysfww.com/goods.php?id=2482"},
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

def extract_drug_content(drug_name, content):
    """提取药品在数据库中的完整内容"""
    clean_name = drug_name.replace('※', '').replace('▲', '').strip()
    
    # 查找药品记录
    pattern = rf'"name":\s*"{re.escape(clean_name)}"[\s\S]*?"manual":\s*\{{[\s\S]*?\}}\s*,\s*"pinyin"'
    match = re.search(pattern, content)
    
    if not match:
        return None
    
    manual_text = match.group(0)
    
    # 提取各个字段
    fields = {}
    field_names = ['indications', 'dosage', 'contraindications', 'adverse_reactions', 
                   'interactions', 'pregnancy_category', 'pharmacokinetics', 'precautions', 'source']
    
    for field in field_names:
        field_match = re.search(rf'"{field}":\s*"([^"]*)"', manual_text)
        if field_match:
            fields[field] = field_match.group(1)
        else:
            fields[field] = ""
    
    # 检查是否有完整版字段
    full_fields = {}
    for field in field_names:
        full_match = re.search(rf'"full_{field}":\s*"([^"]*)"', manual_text)
        if full_match:
            full_fields[field] = full_match.group(1)
    
    return {"fields": fields, "full_fields": full_fields}

def check_content_quality(drug_name, content_data):
    """检查内容质量"""
    if not content_data:
        return {"status": "❌ 未找到", "issues": ["数据库中无此药品记录"]}
    
    fields = content_data["fields"]
    full_fields = content_data["full_fields"]
    
    issues = []
    warnings = []
    
    # 检查关键字段
    if not fields.get("indications") or len(fields["indications"]) < 20:
        issues.append("适应症缺失或太短")
    
    if not fields.get("dosage") or len(fields["dosage"]) < 20:
        issues.append("用法用量缺失或太短")
    
    if not fields.get("source"):
        issues.append("来源未标注")
    elif "手动录入" in fields.get("source", ""):
        warnings.append("来源为手动录入，需核对是否与网站一致")
    
    # 检查是否有精简版和完整版
    has_summary = bool(fields.get("indications") and len(fields["indications"]) > 10)
    has_full = bool(full_fields.get("indications"))
    
    if has_summary and not has_full:
        warnings.append("有精简版但无完整版")
    
    # 判断状态
    if issues:
        status = "❌ 有问题"
    elif warnings:
        status = "⚠️ 需核对"
    else:
        status = "✅ 正常"
    
    return {
        "status": status,
        "issues": issues,
        "warnings": warnings,
        "has_summary": has_summary,
        "has_full": has_full,
        "source": fields.get("source", "")
    }

def main():
    print("=" * 100)
    print("第一批次药品详细检查报告（1-20号）- 对比网站内容")
    print("=" * 100)
    
    # 读取数据库
    print("\n正在读取数据库...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = []
    need_verify = []
    
    for drug in BATCH_1_DRUGS:
        print(f"\n检查 {drug['seq']:2d}. {drug['name']}...")
        
        content_data = extract_drug_content(drug['name'], content)
        check_result = check_content_quality(drug['name'], content_data)
        
        result = {
            "seq": drug['seq'],
            "name": drug['name'],
            "url": drug['url'],
            **check_result
        }
        results.append(result)
        
        print(f"  状态: {check_result['status']}")
        print(f"  来源: {check_result['source']}")
        
        if check_result['issues']:
            print(f"  ❌ 问题: {', '.join(check_result['issues'])}")
        if check_result['warnings']:
            print(f"  ⚠️  警告: {', '.join(check_result['warnings'])}")
        
        if check_result['status'] in ["❌ 有问题", "⚠️ 需核对"]:
            need_verify.append(result)
    
    # 汇总
    print("\n" + "=" * 100)
    print("检查汇总")
    print("=" * 100)
    
    normal_count = len([r for r in results if r['status'] == "✅ 正常"])
    warning_count = len([r for r in results if r['status'] == "⚠️ 需核对"])
    error_count = len([r for r in results if r['status'] == "❌ 有问题"])
    
    print(f"✅ 正常: {normal_count} 个")
    print(f"⚠️  需核对: {warning_count} 个")
    print(f"❌ 有问题: {error_count} 个")
    print(f"总计: {len(results)} 个")
    
    # 需要核对的列表
    if need_verify:
        print("\n" + "=" * 100)
        print("⚠️ 需要与网站核对的药品列表")
        print("=" * 100)
        for drug in need_verify:
            print(f"\n{drug['seq']:2d}. {drug['name']}")
            print(f"    网址: {drug['url']}")
            print(f"    状态: {drug['status']}")
            print(f"    来源: {drug['source']}")
            if drug['issues']:
                print(f"    问题: {', '.join(drug['issues'])}")
            if drug['warnings']:
                print(f"    警告: {', '.join(drug['warnings'])}")
    
    # 保存报告
    report_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/第一批次详细检查报告.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("第一批次药品详细检查报告（1-20号）\n")
        f.write("=" * 100 + "\n\n")
        
        for drug in results:
            f.write(f"{drug['seq']:2d}. {drug['name']}\n")
            f.write(f"    网址: {drug['url']}\n")
            f.write(f"    状态: {drug['status']}\n")
            f.write(f"    来源: {drug['source']}\n")
            if drug['issues']:
                f.write(f"    问题: {', '.join(drug['issues'])}\n")
            if drug['warnings']:
                f.write(f"    警告: {', '.join(drug['warnings'])}\n")
            f.write("\n")
        
        f.write("=" * 100 + "\n")
        f.write("汇总统计\n")
        f.write("=" * 100 + "\n")
        f.write(f"✅ 正常: {normal_count} 个\n")
        f.write(f"⚠️  需核对: {warning_count} 个\n")
        f.write(f"❌ 有问题: {error_count} 个\n")
        f.write(f"总计: {len(results)} 个\n")
        
        if need_verify:
            f.write("\n" + "=" * 100 + "\n")
            f.write("需要与网站核对的药品列表\n")
            f.write("=" * 100 + "\n")
            for drug in need_verify:
                f.write(f"\n{drug['seq']:2d}. {drug['name']}\n")
                f.write(f"    网址: {drug['url']}\n")
                f.write(f"    状态: {drug['status']}\n")
                f.write(f"    来源: {drug['source']}\n")
    
    print(f"\n详细报告已保存到: {report_file}")

if __name__ == '__main__':
    main()
