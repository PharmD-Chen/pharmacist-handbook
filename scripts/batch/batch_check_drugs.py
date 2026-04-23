#!/usr/bin/env python3
"""批量检查药品手册内容 - 第一批次（1-20号）"""

import re
import json

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

def check_drug_in_database(drug_name, content):
    """检查药品是否在数据库中以及内容完整性"""
    # 清理药品名称（去除特殊标记）
    clean_name = drug_name.replace('※', '').replace('▲', '').strip()
    
    # 在内容中查找药品
    pattern = rf'"name":\s*"[^"]*{re.escape(clean_name)}[^"]*"'
    matches = re.findall(pattern, content)
    
    if not matches:
        return {"found": False, "status": "未找到", "fields": {}}
    
    # 找到第一个匹配的位置，检查其manual字段
    match = re.search(rf'"name":\s*"[^"]*{re.escape(clean_name)}[^"]*"[\s\S]*?"manual":\s*(\{{[\s\S]*?\}})', content)
    
    if not match:
        return {"found": True, "status": "无手册内容", "fields": {}}
    
    manual_text = match.group(1)
    
    # 检查关键字段
    fields = {
        "indications": "indications" in manual_text and len(re.search(r'"indications":\s*"([^"]*)"', manual_text).group(1)) > 10 if re.search(r'"indications":\s*"([^"]*)"', manual_text) else False,
        "dosage": "dosage" in manual_text and len(re.search(r'"dosage":\s*"([^"]*)"', manual_text).group(1)) > 10 if re.search(r'"dosage":\s*"([^"]*)"', manual_text) else False,
        "contraindications": "contraindications" in manual_text,
        "adverse_reactions": "adverse_reactions" in manual_text,
        "source": "source" in manual_text,
    }
    
    # 判断状态
    if all(fields.values()):
        status = "✅ 完整"
    elif fields["indications"] or fields["dosage"]:
        status = "⚠️ 部分"
    else:
        status = "❌ 缺失"
    
    return {"found": True, "status": status, "fields": fields}

def main():
    print("=" * 80)
    print("第一批次药品检查报告（1-20号，共19个有网址的药品）")
    print("=" * 80)
    
    # 读取数据库文件
    print("\n正在读取数据库...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"数据库大小: {len(content)} 字符\n")
    
    # 检查结果汇总
    results = {
        "complete": 0,
        "partial": 0,
        "missing": 0,
        "not_found": 0
    }
    
    detailed_results = []
    
    for drug in BATCH_1_DRUGS:
        print(f"\n检查 {drug['seq']:2d}. {drug['name']}...")
        result = check_drug_in_database(drug['name'], content)
        
        if result["status"] == "✅ 完整":
            results["complete"] += 1
        elif result["status"] == "⚠️ 部分":
            results["partial"] += 1
        elif result["status"] == "❌ 缺失":
            results["missing"] += 1
        else:
            results["not_found"] += 1
        
        detailed_results.append({
            "seq": drug['seq'],
            "name": drug['name'],
            "url": drug['url'],
            **result
        })
        
        print(f"  状态: {result['status']}")
        if result['fields']:
            print(f"  字段: 适应症{'✓' if result['fields'].get('indications') else '✗'}, "
                  f"用法用量{'✓' if result['fields'].get('dosage') else '✗'}, "
                  f"禁忌症{'✓' if result['fields'].get('contraindications') else '✗'}, "
                  f"不良反应{'✓' if result['fields'].get('adverse_reactions') else '✗'}, "
                  f"来源{'✓' if result['fields'].get('source') else '✗'}")
    
    # 打印汇总
    print("\n" + "=" * 80)
    print("检查汇总")
    print("=" * 80)
    print(f"✅ 内容完整: {results['complete']} 个")
    print(f"⚠️  内容部分: {results['partial']} 个")
    print(f"❌ 内容缺失: {results['missing']} 个")
    print(f"🔍 未找到记录: {results['not_found']} 个")
    print(f"总计: {len(BATCH_1_DRUGS)} 个")
    
    # 需要更新的药品列表
    need_update = [r for r in detailed_results if r['status'] in ['⚠️ 部分', '❌ 缺失', '未找到']]
    
    if need_update:
        print("\n" + "=" * 80)
        print("需要更新/补充的药品列表")
        print("=" * 80)
        for drug in need_update:
            print(f"{drug['seq']:2d}. {drug['name']}")
            print(f"    网址: {drug['url']}")
            print(f"    状态: {drug['status']}")
            print()
    
    # 保存详细报告
    report_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/第一批次检查报告.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("第一批次药品检查报告（1-20号）\n")
        f.write("=" * 80 + "\n\n")
        
        for drug in detailed_results:
            f.write(f"{drug['seq']:2d}. {drug['name']}\n")
            f.write(f"    网址: {drug['url']}\n")
            f.write(f"    状态: {drug['status']}\n")
            if drug['fields']:
                f.write(f"    字段完整性:\n")
                for field, exists in drug['fields'].items():
                    f.write(f"      - {field}: {'✓' if exists else '✗'}\n")
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("汇总统计\n")
        f.write("=" * 80 + "\n")
        f.write(f"✅ 内容完整: {results['complete']} 个\n")
        f.write(f"⚠️  内容部分: {results['partial']} 个\n")
        f.write(f"❌ 内容缺失: {results['missing']} 个\n")
        f.write(f"🔍 未找到记录: {results['not_found']} 个\n")
        f.write(f"总计: {len(BATCH_1_DRUGS)} 个\n")
    
    print(f"\n详细报告已保存到: {report_file}")

if __name__ == '__main__':
    main()
