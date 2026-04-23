#!/usr/bin/env python3
"""更新德谷胰岛素的手册内容"""

import re

# 德谷胰岛素的完整手册内容（来自网站）
DEGUDAO_CONTENT = {
    "indications": """⑴适用于成人1型和2型糖尿病的治疗。
⑵用于1岁以上儿童及成人糖尿病患者的治疗（1型糖尿病、2型糖尿病均可）。【美国FDA已批准；美国糖尿病协会ADA指南（2020版）】""",

    "dosage": """1.皮下注射：对于1型糖尿病患者，用法为每日1次（联合餐时速效胰岛素）；对于2型糖尿病患者，本品可单独使用，也可联合口服降糖药、GLP-1 类似物或餐时胰岛素。
2.未接受过胰岛素治疗的2型糖尿病患者：推荐初始剂量为一次10U。
3.临床试验证实，接受其他胰岛素方案治疗的患者均可换用德谷胰岛素，但在换药过程中应密切监测血糖并可能需要调整胰岛素剂量。
4.由每天给药一次的胰岛素换用德谷胰岛素，通常以 1:1 的比例进行剂量转换；如果之前使用每天给药两次的胰岛素方案，建议将剂量减少 20%。当然，由每天给药一次的胰岛素换用德谷胰岛素时，如果患者 HbA1c 水平较低，也可考虑减少德谷胰岛素剂量。此外，换用德谷胰岛素后还应调整餐时胰岛素剂量以减少低血糖风险。
5.可每周进行一次剂量调整以达到个体化血糖控制目标。治疗目标和胰岛素剂量调整均基于患者早餐前FPG（或SMBG）水平。可计算前两天的平均 FBG 并与血糖控制目标进行对比，增加或减少2个单位基础胰岛素以达到治疗目标。""",

    "contraindications": """低血糖发作时禁用。对德谷胰岛素或本品中任何辅料过敏者禁用。""",

    "adverse_reactions": """常见的不良反应为低血糖，可能由胰岛素剂量过高或饮食不当引起。其他不良反应包括注射部位反应（如疼痛、红斑、瘙痒、肿胀、炎症）、脂肪代谢障碍（脂肪萎缩或脂肪增生）、体重增加、水肿、视力模糊等。少见的不良反应包括过敏反应（如荨麻疹、皮疹、血管性水肿、过敏性休克）。""",

    "interactions": """1. 与口服降糖药、MAOI、β受体阻滞剂、ACE抑制剂、水杨酸盐、合成类固醇、磺胺类药物合用可能增强降糖作用，增加低血糖风险。
2. 与糖皮质激素、甲状腺激素、噻嗪类利尿剂、口服避孕药、烟酸、拟交感神经药合用可能减弱降糖作用。
3. β受体阻滞剂可能掩盖低血糖症状。
4. 酒精可能增强或减弱胰岛素降糖作用。""",

    "pregnancy_category": """C级""",

    "pharmacokinetics": """本品为一种超长效的基础胰岛素类似物。半衰期接近25小时，稳态血药浓度作用时间超过42 小时，每天1次注射可发挥持久、稳定的降糖作用。本品不仅可以有效降低血糖，同时降低了低血糖的发生率。

德谷胰岛素皮下注射后形成可溶性多六聚体，在注射部位形成胰岛素储库，缓慢持续释放德谷胰岛素单体，作用持续时间超过42小时。德谷胰岛素的消除半衰期约为25小时。""",

    "precautions": """1.可每周进行一次剂量调整以达到个体化血糖控制目标。治疗目标和胰岛素剂量调整均基于患者早餐前 FPG（或 SMBG）水平。可计算前两天的平均 FBG 并与血糖控制目标进行对比，增加或减少 2 个单位基础胰岛素以达到治疗目标。
2.德谷胰岛素每天给药一次，最好在每天的同一时间注射。不过，如果有时不能在同一时间注射，德谷胰岛素的给药时间也可灵活调整，相邻两次给药的时间不低于 8 小时被证实是安全的。与每天同一时间给药的甘精胰岛素相比，德谷胰岛素灵活给药（间隔 8~40 小时）不影响其有效性和安全性。如果患者发生德谷胰岛素漏用，应嘱其尽快注射并重新开始之前的每日一次给药方案。
3.德谷胰岛素被批准用于老年（≥ 65 岁）患者，同时适用于肾功能或肝功能不全的患者。然而，与其他胰岛素一样，在上述特殊人群中使用时应加强血糖监测。德谷胰岛素用于儿童或 18 岁以下青少年的安全性和有效性目前正在验证中。此外，目前尚无在孕妇中使用德谷胰岛素的临床经验。""",

    "source": "湖南药事服务网"
}

def escape_for_json(text):
    """转义文本以用于JSON"""
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '<br>')
    text = text.replace('\r', '')
    return text

def smart_summarize(text, field_type):
    """智能生成精简版内容"""
    if not text or len(text) < 100:
        return text
    
    # 移除HTML标签进行长度判断
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # 如果内容本身就很短，直接返回
    if len(clean_text) < 150:
        return text
    
    # 根据不同字段类型采用不同的精简策略
    if field_type == 'indications':
        # 适应症：提取主要适应症
        lines = text.split('\n')
        summary_lines = []
        for line in lines[:2]:  # 取前2行
            line = line.strip()
            if line and not line.startswith('【'):
                # 提取关键部分
                summary_lines.append(line)
        return '<br>'.join(summary_lines) if summary_lines else text[:200]
    
    elif field_type == 'dosage':
        # 用法用量：提取关键剂量信息
        lines = text.split('\n')
        summary_lines = []
        for line in lines:
            if '初始剂量' in line or '推荐' in line or '皮下注射' in line:
                summary_lines.append(line.strip())
            if len(summary_lines) >= 2:
                break
        return '<br>'.join(summary_lines) if summary_lines else text[:200]
    
    elif field_type == 'contraindications':
        # 禁忌症：提取关键禁忌
        lines = text.split('\n')
        summary_lines = []
        for line in lines:
            if '禁用' in line or '过敏' in line:
                summary_lines.append(line.strip())
        return '<br>'.join(summary_lines) if summary_lines else text[:150]
    
    elif field_type == 'adverse_reactions':
        # 不良反应：提取常见反应
        lines = text.split('\n')
        summary_lines = []
        for line in lines:
            if '常见' in line or '低血糖' in line:
                summary_lines.append(line.strip())
            if len(summary_lines) >= 2:
                break
        return '<br>'.join(summary_lines) if summary_lines else text[:200]
    
    elif field_type == 'precautions':
        # 注意事项：提取关键注意点
        lines = text.split('\n')
        summary_lines = []
        for line in lines[:3]:  # 取前3行
            line = line.strip()
            if line and len(line) > 10:
                summary_lines.append(line)
        return '<br>'.join(summary_lines) if summary_lines else text[:200]
    
    elif field_type == 'interactions':
        # 药物相互作用：提取关键相互作用
        lines = text.split('\n')
        summary_lines = []
        for line in lines[:3]:
            line = line.strip()
            if line and ('增强' in line or '减弱' in line or '风险' in line):
                summary_lines.append(line)
        return '<br>'.join(summary_lines) if summary_lines else text[:200]
    
    elif field_type == 'pharmacokinetics':
        # 药代动力学：提取关键参数
        lines = text.split('\n')
        summary_lines = []
        for line in lines:
            if '半衰期' in line or '小时' in line or '作用持续' in line:
                summary_lines.append(line.strip())
            if len(summary_lines) >= 2:
                break
        return '<br>'.join(summary_lines) if summary_lines else text[:200]
    
    else:
        # 默认策略：提取前150个字符
        if len(text) > 150:
            return text[:150] + '...'
        return text

def main():
    # 读取 drugs.js 文件
    print("正在读取 drugs.js 文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成精简版内容
    summary_indications = smart_summarize(DEGUDAO_CONTENT['indications'], 'indications')
    summary_dosage = smart_summarize(DEGUDAO_CONTENT['dosage'], 'dosage')
    summary_contraindications = smart_summarize(DEGUDAO_CONTENT['contraindications'], 'contraindications')
    summary_adverse = smart_summarize(DEGUDAO_CONTENT['adverse_reactions'], 'adverse_reactions')
    summary_interactions = smart_summarize(DEGUDAO_CONTENT['interactions'], 'interactions')
    summary_pharmacokinetics = smart_summarize(DEGUDAO_CONTENT['pharmacokinetics'], 'pharmacokinetics')
    summary_precautions = smart_summarize(DEGUDAO_CONTENT['precautions'], 'precautions')
    
    # 转义所有内容
    summary_indications_esc = escape_for_json(summary_indications)
    summary_dosage_esc = escape_for_json(summary_dosage)
    summary_contra_esc = escape_for_json(summary_contraindications)
    summary_adverse_esc = escape_for_json(summary_adverse)
    summary_inter_esc = escape_for_json(summary_interactions)
    summary_pharma_esc = escape_for_json(summary_pharmacokinetics)
    summary_prec_esc = escape_for_json(summary_precautions)
    
    full_indications_esc = escape_for_json(DEGUDAO_CONTENT['indications'])
    full_dosage_esc = escape_for_json(DEGUDAO_CONTENT['dosage'])
    full_contra_esc = escape_for_json(DEGUDAO_CONTENT['contraindications'])
    full_adverse_esc = escape_for_json(DEGUDAO_CONTENT['adverse_reactions'])
    full_inter_esc = escape_for_json(DEGUDAO_CONTENT['interactions'])
    full_pharma_esc = escape_for_json(DEGUDAO_CONTENT['pharmacokinetics'])
    full_prec_esc = escape_for_json(DEGUDAO_CONTENT['precautions'])
    
    # 查找德谷胰岛素记录 (id: 592)
    print("正在更新德谷胰岛素 (id: 592) 的手册内容...")
    
    # 构建新的 manual 对象
    new_manual_lines = [
        '"manual": {',
        f'      "indications": "{summary_indications_esc}",',
        f'      "dosage": "{summary_dosage_esc}",',
        f'      "contraindications": "{summary_contra_esc}",',
        f'      "adverse_reactions": "{summary_adverse_esc}",',
        f'      "interactions": "{summary_inter_esc}",',
        f'      "pregnancy_category": "{DEGUDAO_CONTENT["pregnancy_category"]}",',
        f'      "pharmacokinetics": "{summary_pharma_esc}",',
        f'      "precautions": "{summary_prec_esc}",',
        f'      "source": "{DEGUDAO_CONTENT["source"]}",',
        f'      "full_indications": "{full_indications_esc}",',
        f'      "full_dosage": "{full_dosage_esc}",',
        f'      "full_contraindications": "{full_contra_esc}",',
        f'      "full_adverse_reactions": "{full_adverse_esc}",',
        f'      "full_interactions": "{full_inter_esc}",',
        f'      "full_pregnancy_category": "{DEGUDAO_CONTENT["pregnancy_category"]}",',
        f'      "full_pharmacokinetics": "{full_pharma_esc}",',
        f'      "full_precautions": "{full_prec_esc}"',
        '    }'
    ]
    new_manual = '\n'.join(new_manual_lines)
    
    # 使用正则表达式查找并替换 id 为 592 的德谷胰岛素记录
    # 查找模式：从 "id": 592 开始，到下一个药品的 "id": 之前
    pattern = r'(\{\s*"id":\s*592,\s*"name":\s*"德谷胰岛素"[\s\S]*?"spec_count":\s*\d+,\s*)"manual":\s*\{[\s\S]*?\}(\s*,\s*"pinyin")'
    
    def replace_manual(match):
        return match.group(1) + new_manual + match.group(2)
    
    new_content = re.sub(pattern, replace_manual, content)
    
    # 检查是否成功替换
    if new_content == content:
        print("警告：未能找到匹配的德谷胰岛素记录，尝试其他模式...")
        # 尝试更简单的模式
        pattern2 = r'("id":\s*592,\s*"name":\s*"德谷胰岛素".*?"spec_count":\s*1,\s*)"manual":\s*\{[\s\S]*?\}\s*,\s*"pinyin"'
        new_content = re.sub(pattern2, r'\1' + new_manual + ',\n    "pinyin"', content)
    
    # 保存文件
    print("正在保存更新后的文件...")
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ 德谷胰岛素手册内容更新完成！")
    print("更新内容：")
    print(f"  - 适应症: {len(DEGUDAO_CONTENT['indications'])} 字符")
    print(f"  - 用法用量: {len(DEGUDAO_CONTENT['dosage'])} 字符")
    print(f"  - 禁忌症: {len(DEGUDAO_CONTENT['contraindications'])} 字符")
    print(f"  - 不良反应: {len(DEGUDAO_CONTENT['adverse_reactions'])} 字符")
    print(f"  - 注意事项: {len(DEGUDAO_CONTENT['precautions'])} 字符")
    print(f"  - 药物相互作用: {len(DEGUDAO_CONTENT['interactions'])} 字符")
    print(f"  - 药代动力学: {len(DEGUDAO_CONTENT['pharmacokinetics'])} 字符")

if __name__ == '__main__':
    main()
