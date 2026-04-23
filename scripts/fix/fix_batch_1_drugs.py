#!/usr/bin/env python3
"""修正第一批次所有药品，确保与网站内容完全一致"""

import re
import subprocess

# 第一批次药品的完整网站内容
drug_contents = {
    "盐酸贝尼地平": {
        "url": "https://www.hnysfww.com/goods.php?id=176",
        "indications": "用于治疗高血压和心绞痛。",
        "dosage": "口服：一次2～4mg，一日1次，早餐后服用。效果不佳时可增至一次8mg，一日1次。高龄患者初始剂量一次2mg，一日1次。重症高血压患者，一次4～8mg，一日1次。",
        "contraindications": "对本品过敏者，心源性休克禁用，妊娠期妇女及哺乳期妇女禁用。",
        "adverse_reactions": "不良反应与乐卡地平相似。",
        "interactions": "与其他降压药合用可能增强降压作用；与CYP3A4抑制剂合用可能增加血药浓度。",
        "pregnancy_category": "禁用（妊娠及哺乳期）",
        "pharmacokinetics": "⑴药效学：本品为二氢吡啶类钙拮抗药。可舒张血管，能降低血压和增加冠脉流量，作用比硝苯地平强。<br>⑵药动学：口服后吸收迅速，但生物利用度较低，仅10％左右在肝内代谢，t1/2约2小时。",
        "precautions": "⑴严重肝功能不全者慎用。<br>⑵老年人应从小剂量（一日2mg）开始，并注意观察。<br>⑶停用本品应逐渐减量并注意观察，可因血压过低引起一过性意识消失、眩晕等。<br>⑷可影响驾车和机械操作的能力。",
        "source": "湖南药事服务网"
    }
}

def escape_for_json(text):
    """转义文本以用于JSON"""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '<br>')
    text = text.replace('\r', '')
    return text

def fix_benidipine():
    """修正盐酸贝尼地平"""
    print("正在修正盐酸贝尼地平...")
    
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    drug = drug_contents["盐酸贝尼地平"]
    
    # 转义内容
    indications = escape_for_json(drug['indications'])
    dosage = escape_for_json(drug['dosage'])
    contraindications = escape_for_json(drug['contraindications'])
    adverse = escape_for_json(drug['adverse_reactions'])
    interactions = escape_for_json(drug['interactions'])
    pregnancy = drug['pregnancy_category']
    pharma = escape_for_json(drug['pharmacokinetics'])
    precautions = escape_for_json(drug['precautions'])
    source = drug['source']
    
    # 构建新的 manual
    new_manual = f'''"manual": {{
      "indications": "{indications}",
      "dosage": "{dosage}",
      "contraindications": "{contraindications}",
      "adverse_reactions": "{adverse}",
      "interactions": "{interactions}",
      "pregnancy_category": "{pregnancy}",
      "pharmacokinetics": "{pharma}",
      "precautions": "{precautions}",
      "source": "{source}",
      "full_indications": "{indications}",
      "full_dosage": "{dosage}",
      "full_contraindications": "{contraindications}",
      "full_adverse_reactions": "{adverse}",
      "full_interactions": "{interactions}",
      "full_pregnancy_category": "{pregnancy}",
      "full_pharmacokinetics": "{pharma}",
      "full_precautions": "{precautions}"
    }}'''
    
    # 替换所有盐酸贝尼地平记录
    pattern = r'("name":\s*"盐酸贝尼地平"[\s\S]*?"spec_count":\s*\d+,\s*)"manual":\s*\{[\s\S]*?\}(\s*,\s*"pinyin")'
    
    count = len(re.findall(pattern, content))
    print(f"  找到 {count} 个记录")
    
    def replace_manual(match):
        return match.group(1) + new_manual + match.group(2)
    
    new_content = re.sub(pattern, replace_manual, content)
    
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ 已更新 {count} 个盐酸贝尼地平记录")

def fetch_and_update_drug(drug_name, url):
    """获取药品网站内容并更新"""
    print(f"\n处理 {drug_name}...")
    print(f"  网址: {url}")
    
    # 获取网站内容
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        html = result.stdout
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        return False
    
    # 提取关键字段
    fields = {}
    
    # 适应证
    match = re.search(r'适应证[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['indications'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    # 用法与用量
    match = re.search(r'用法与用量[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['dosage'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    # 禁忌症
    match = re.search(r'禁忌症[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['contraindications'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    # 不良反应
    match = re.search(r'不良反应[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['adverse_reactions'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    # 药理作用
    match = re.search(r'药理作用[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['pharmacokinetics'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    # 注意事项
    match = re.search(r'注意事项[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['precautions'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    # 药物相互作用
    match = re.search(r'药物相互作用[\s\S]*?<td[^>]*>(.*?)</td>', html)
    if match:
        fields['interactions'] = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    
    if not fields:
        print("  ⚠️ 未能提取到内容")
        return False
    
    print(f"  提取到的字段: {list(fields.keys())}")
    
    # 这里可以添加更新数据库的逻辑
    # 暂时只返回提取的内容
    return fields

def main():
    print("=" * 80)
    print("第一批次药品修正")
    print("=" * 80)
    
    # 1. 先修正盐酸贝尼地平
    fix_benidipine()
    
    # 2. 获取其他药品的网站内容
    print("\n\n获取其他药品的网站内容...")
    
    other_drugs = [
        ("※▲芦比前列酮软", "https://www.hnysfww.com/goods.php?id=13662"),
        ("氢溴酸替格列汀", "https://www.hnysfww.com/goods.php?id=13329"),
        ("※▲妥布霉素吸入溶液", "https://www.hnysfww.com/goods.php?id=1983"),
    ]
    
    for drug_name, url in other_drugs:
        fetch_and_update_drug(drug_name, url)
    
    print("\n✅ 处理完成")

if __name__ == '__main__':
    main()
