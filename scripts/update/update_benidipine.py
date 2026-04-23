#!/usr/bin/env python3
"""更新盐酸贝尼地平的手册内容以匹配网站"""

import re

# 盐酸贝尼地平的完整手册内容（来自网站 https://www.hnysfww.com/goods.php?id=176）
BENIDIPINE_CONTENT = {
    "indications": "用于治疗高血压和心绞痛。",
    "dosage": "口服：一次2～4mg，一日1次，早餐后服用。效果不佳时可增至一次8mg，一日1次。高龄患者初始剂量一次2mg，一日1次。重症高血压患者，一次4～8mg，一日1次。",
    "contraindications": "对本品过敏者禁用；心源性休克禁用；妊娠期妇女及哺乳期妇女禁用。",
    "adverse_reactions": "不良反应与乐卡地平相似。",
    "interactions": "与其他降压药合用可能增强降压作用；与CYP3A4抑制剂合用可能增加血药浓度。",
    "pregnancy_category": "禁用（妊娠及哺乳期）",
    "pharmacokinetics": "本品为二氢吡啶类钙拮抗药。可舒张血管，能降低血压和增加冠脉流量，作用比硝苯地平强。口服后吸收迅速，但生物利用度较低，仅10％左右在肝内代谢，t1/2约2小时。",
    "precautions": "严重肝功能不全者慎用；老年人应从小剂量（一日2mg）开始，并注意观察；停用本品应逐渐减量并注意观察，可因血压过低引起一过性意识消失、眩晕等；可影响驾车和机械操作的能力。",
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
    indications_esc = escape_for_json(BENIDIPINE_CONTENT['indications'])
    dosage_esc = escape_for_json(BENIDIPINE_CONTENT['dosage'])
    contra_esc = escape_for_json(BENIDIPINE_CONTENT['contraindications'])
    adverse_esc = escape_for_json(BENIDIPINE_CONTENT['adverse_reactions'])
    inter_esc = escape_for_json(BENIDIPINE_CONTENT['interactions'])
    pharma_esc = escape_for_json(BENIDIPINE_CONTENT['pharmacokinetics'])
    prec_esc = escape_for_json(BENIDIPINE_CONTENT['precautions'])
    
    print("正在更新所有盐酸贝尼地平记录...")
    
    # 构建新的 manual 对象
    new_manual_lines = [
        '"manual": {',
        f'      "indications": "{indications_esc}",',
        f'      "dosage": "{dosage_esc}",',
        f'      "contraindications": "{contra_esc}",',
        f'      "adverse_reactions": "{adverse_esc}",',
        f'      "interactions": "{inter_esc}",',
        f'      "pregnancy_category": "{BENIDIPINE_CONTENT["pregnancy_category"]}",',
        f'      "pharmacokinetics": "{pharma_esc}",',
        f'      "precautions": "{prec_esc}",',
        f'      "source": "{BENIDIPINE_CONTENT["source"]}",',
        f'      "full_indications": "{indications_esc}",',
        f'      "full_dosage": "{dosage_esc}",',
        f'      "full_contraindications": "{contra_esc}",',
        f'      "full_adverse_reactions": "{adverse_esc}",',
        f'      "full_interactions": "{inter_esc}",',
        f'      "full_pregnancy_category": "{BENIDIPINE_CONTENT["pregnancy_category"]}",',
        f'      "full_pharmacokinetics": "{pharma_esc}",',
        f'      "full_precautions": "{prec_esc}"',
        '    }'
    ]
    new_manual = '\n'.join(new_manual_lines)
    
    # 替换所有盐酸贝尼地平的 manual 部分
    # 匹配模式：找到 "name": "盐酸贝尼地平" 后面的 manual 对象
    pattern = r'("name":\s*"盐酸贝尼地平"[\s\S]*?"spec_count":\s*\d+,\s*)"manual":\s*\{[\s\S]*?\}(\s*,\s*"pinyin")'
    
    count = len(re.findall(pattern, content))
    print(f"找到 {count} 个盐酸贝尼地平记录")
    
    def replace_manual(match):
        return match.group(1) + new_manual + match.group(2)
    
    new_content = re.sub(pattern, replace_manual, content)
    
    if new_content == content:
        print("警告：未能成功替换内容")
        return
    
    # 保存文件
    print("正在保存更新后的文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ 盐酸贝尼地平手册内容更新完成！")
    print(f"更新了 {count} 个记录")
    print("更新内容：")
    print(f"  - 适应症: {BENIDIPINE_CONTENT['indications']}")
    print(f"  - 用法用量: {BENIDIPINE_CONTENT['dosage'][:50]}...")
    print(f"  - 禁忌症: {BENIDIPINE_CONTENT['contraindications']}")
    print(f"  - 不良反应: {BENIDIPINE_CONTENT['adverse_reactions']}")
    print(f"  - 来源: {BENIDIPINE_CONTENT['source']}")

if __name__ == '__main__':
    main()
