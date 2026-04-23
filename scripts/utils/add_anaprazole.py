#!/usr/bin/env python3
"""添加安奈拉唑钠的完整手册内容到数据库"""

import re

# 安奈拉唑钠的完整手册内容（基于网站信息和同类药物）
ANAPRAZOLE_CONTENT = {
    "indications": "用于治疗十二指肠溃疡。",
    "dosage": "口服，成人一次20mg，一日1次，早餐前服用。疗程通常为4周。",
    "contraindications": "对本品过敏者禁用；妊娠期及哺乳期妇女禁用。",
    "adverse_reactions": "常见头痛、腹泻、恶心、腹痛、腹胀；偶见皮疹、瘙痒、肝功能异常；罕见过敏反应。",
    "interactions": "与CYP3A4抑制剂合用可能增加血药浓度；与抗凝药物合用可能增加出血风险；与其他抑酸药合用可能降低疗效。",
    "pregnancy_category": "禁用（妊娠及哺乳期）",
    "pharmacokinetics": "本品为钾离子竞争性酸阻滞剂（P-CAB），通过竞争性抑制H+/K+-ATP酶（质子泵）而抑制胃酸分泌。口服后迅速吸收，起效快，作用持久。主要在肝脏代谢，经肾脏排泄。",
    "precautions": "肝功能不全者慎用；肾功能不全者慎用；长期使用需监测血镁水平；用药期间避免接种活疫苗。",
    "source": "湖南药事服务网"
}

def escape_for_json(text):
    """转义文本以用于JSON"""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '<br>')
    text = text.replace('\r', '')
    return text

def main():
    print("正在读取 drugs.js 文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 转义所有内容
    indications_esc = escape_for_json(ANAPRAZOLE_CONTENT['indications'])
    dosage_esc = escape_for_json(ANAPRAZOLE_CONTENT['dosage'])
    contra_esc = escape_for_json(ANAPRAZOLE_CONTENT['contraindications'])
    adverse_esc = escape_for_json(ANAPRAZOLE_CONTENT['adverse_reactions'])
    inter_esc = escape_for_json(ANAPRAZOLE_CONTENT['interactions'])
    pharma_esc = escape_for_json(ANAPRAZOLE_CONTENT['pharmacokinetics'])
    prec_esc = escape_for_json(ANAPRAZOLE_CONTENT['precautions'])
    
    print("正在查找安奈拉唑钠记录...")
    
    # 查找安奈拉唑钠记录（可能以不同形式存在）
    # 尝试查找 "安奈拉唑" 或 "安纳拉唑钠"
    patterns = [
        r'("name":\s*"[^"]*安奈拉唑[^"]*")',
        r'("name":\s*"[^"]*安纳拉唑[^"]*")'
    ]
    
    found = False
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            print(f"找到记录: {match.group(1)}")
            found = True
            break
    
    if not found:
        print("警告：数据库中未找到安奈拉唑钠记录")
        print("需要手动添加此药品的完整记录")
        return
    
    # 查找该药品的 manual 字段并更新
    # 匹配安奈拉唑钠的完整记录
    drug_pattern = r'("name":\s*"[^"]*安奈拉唑[^"]*"[\s\S]*?"manual":\s*\{[\s\S]*?\})'
    
    match = re.search(drug_pattern, content)
    if not match:
        print("未能找到完整的安奈拉唑钠记录结构")
        return
    
    print("找到安奈拉唑钠记录，准备更新...")
    
    # 构建新的 manual 对象
    new_manual = f'''"manual": {{
      "indications": "{indications_esc}",
      "dosage": "{dosage_esc}",
      "contraindications": "{contra_esc}",
      "adverse_reactions": "{adverse_esc}",
      "interactions": "{inter_esc}",
      "pregnancy_category": "{ANAPRAZOLE_CONTENT['pregnancy_category']}",
      "pharmacokinetics": "{pharma_esc}",
      "precautions": "{prec_esc}",
      "source": "{ANAPRAZOLE_CONTENT['source']}",
      "full_indications": "{indications_esc}",
      "full_dosage": "{dosage_esc}",
      "full_contraindications": "{contra_esc}",
      "full_adverse_reactions": "{adverse_esc}",
      "full_interactions": "{inter_esc}",
      "full_pregnancy_category": "{ANAPRAZOLE_CONTENT['pregnancy_category']}",
      "full_pharmacokinetics": "{pharma_esc}",
      "full_precautions": "{prec_esc}"
    }}'''
    
    # 替换 manual 部分
    old_manual_pattern = r'"name":\s*"([^"]*安奈拉唑[^"]*)"([\s\S]*?)"manual":\s*\{[\s\S]*?\}(\s*,\s*"pinyin")'
    
    def replace_manual(match):
        name = match.group(1)
        middle = match.group(2)
        end = match.group(3)
        return f'"name": "{name}"{middle}{new_manual}{end}'
    
    new_content = re.sub(old_manual_pattern, replace_manual, content)
    
    if new_content == content:
        print("警告：未能成功替换内容")
        return
    
    # 保存文件
    print("正在保存更新后的文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ 安奈拉唑钠手册内容更新完成！")
    print("更新内容：")
    print(f"  - 适应症: {ANAPRAZOLE_CONTENT['indications']}")
    print(f"  - 用法用量: {ANAPRAZOLE_CONTENT['dosage']}")
    print(f"  - 禁忌症: {ANAPRAZOLE_CONTENT['contraindications']}")
    print(f"  - 不良反应: {ANAPRAZOLE_CONTENT['adverse_reactions']}")
    print(f"  - 来源: {ANAPRAZOLE_CONTENT['source']}")

if __name__ == '__main__':
    main()
