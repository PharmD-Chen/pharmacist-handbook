#!/usr/bin/env python3
"""更新甲苯磺酸艾多沙班的详细内容以匹配网站"""

import re

# 甲苯磺酸艾多沙班的完整手册内容（来自网站 https://www.hnysfww.com/goods.php?id=11184）
EDOXABAN_CONTENT = {
    "indications": """⑴预防卒中和体循环栓塞：推荐用于非瓣膜性房颤（NVAF）患者。
⑵治疗深静脉血栓（DVT）和肺栓塞（PE），预防复发性深静脉血栓和肺栓塞（静脉血栓栓塞，VTE）。""",

    "dosage": """口服：可与或不与食物一起服用。如果发生漏服，患者应立即服用本品，并于次日继续每日服药1次。患者不得因漏服而在同一天服用两倍剂量。
⑴预防卒中和体循环栓塞：推荐剂量为一次60mg，一日1次。
⑵非瓣膜性房颤（NVAF）患者采用艾多沙班治疗时应长期使用。
⑶治疗深静脉血栓（DVT）和肺栓塞（PE），预防复发性深静脉血栓和肺栓塞（静脉血栓栓塞，VTE）：艾多沙班推荐剂量为一次60mg，一日1次，经初始非口服抗凝剂治疗至少5天后开始给药。不得同时给予艾多沙班和非口服抗凝剂。在谨慎评估治疗获益和出血风险之后，应根据个体情况确定治疗深静脉血栓、肺栓塞（静脉血栓栓塞，VTE）以及预防复发性VTE的持续时间。应基于一过性危险因素（如：近期接受手术、创伤、制动）进行短期治疗（至少3个月），并应基于永久性危险因素或者特发性DVT或PE进行较长时间的治疗。
⑷对于非瓣膜性房颤（NVAF）和静脉血栓栓塞（VTE）的推荐剂量为一次60mg，一日1次；存在一种或一种以上下列临床因素的患者中，艾多沙班的推荐剂量为一次30mg，一日1次：
   - 中度或重度肾损害（CrCl 15-50 mL/min）
   - 体重≤60kg
   - 与特定P-糖蛋白（P-gp）抑制剂合用：环孢素、决奈达隆、红霉素或酮康唑。""",

    "contraindications": """以下患者禁用：
⑴对本品活性成份或者其它辅料过敏的患者。
⑵有临床明显活动性出血的患者。
⑶伴有凝血障碍和临床相关出血风险的肝病患者。
⑷具有大出血显著风险的病灶或病情，例如目前或近期患有胃肠道溃疡，存在出血风险较高的恶性肿瘤，近期发生脑部或脊椎损伤，近期接受脑部、脊椎或眼科手术，近期发生颅内出血，已知或疑似的食管静脉曲张，动静脉畸形，血管动脉瘤或重大脊椎内或脑内血管畸形。
⑸无法控制的重度高血压。
⑹除了转换为口服抗凝剂治疗，或给予维持中心静脉或动脉导管通畅所需剂量普通肝素（UFH）的特殊情况之外，禁用任何其它抗凝剂的伴随治疗，例如UFH、低分子肝素（依诺肝素、达肝素等）、肝素衍生物（磺达肝癸钠等）、口服抗凝剂（华法林、达比加群酯、利伐沙班、阿哌沙班等）。
⑺妊娠和哺乳期妇女。
⑻机械性心瓣膜或中度至严重二尖瓣狭窄建议不使用。""",

    "adverse_reactions": """主要不良反应为出血（尿潜血阳性、皮下出血、伤口出血等）、γ-GTP升高、ALT升高，其他不良反应有头痛、腹泻、出疹子、瘙痒、浮肿、发热等。""",

    "interactions": """⑴减少与奈玛特韦/利托那韦片（组合包装）合用，必须合用建议减少艾多沙班剂量，并监测。
⑵避免与其他抗凝剂合用。
⑶与P-糖蛋白（P-gp）抑制剂合用需调整剂量。""",

    "pregnancy_category": "禁用（妊娠及哺乳期）",

    "pharmacokinetics": """本品为小分子口服抗凝药，为凝血因子X（FXa）阻滞剂。凝血过程中，活化的凝血因子X（FXa）将凝血酶原（FII）激活成为凝血酶（FIIa），促使纤维蛋白形成，由此形成血栓，因而FXa已成为开发新一代抗凝药物的主要靶点。依度沙班通过选择性、可逆性且直接抑制FXa达到抑制血栓形成的口服抗凝药物，其对FXa的选择性比FIIa高104倍。""",

    "precautions": """⑴哺乳母亲：终止药物或终止哺乳。
⑵受损肾功能(CrCL为15至50mL/min)：减低剂量。
⑶中度或严重肝受损：建议不使用。
⑷尚未确定在儿童患者中安全性和有效性。
⑸在临床试验中在老年人(65岁或以上)和较年轻患者SAVAYSA的疗效和安全性相似。""",

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
    indications_esc = escape_for_json(EDOXABAN_CONTENT['indications'])
    dosage_esc = escape_for_json(EDOXABAN_CONTENT['dosage'])
    contra_esc = escape_for_json(EDOXABAN_CONTENT['contraindications'])
    adverse_esc = escape_for_json(EDOXABAN_CONTENT['adverse_reactions'])
    inter_esc = escape_for_json(EDOXABAN_CONTENT['interactions'])
    pharma_esc = escape_for_json(EDOXABAN_CONTENT['pharmacokinetics'])
    prec_esc = escape_for_json(EDOXABAN_CONTENT['precautions'])
    
    print("正在更新所有甲苯磺酸艾多沙班记录...")
    
    # 构建新的 manual 对象
    new_manual_lines = [
        '"manual": {',
        f'      "indications": "{indications_esc}",',
        f'      "dosage": "{dosage_esc}",',
        f'      "contraindications": "{contra_esc}",',
        f'      "adverse_reactions": "{adverse_esc}",',
        f'      "interactions": "{inter_esc}",',
        f'      "pregnancy_category": "{EDOXABAN_CONTENT["pregnancy_category"]}",',
        f'      "pharmacokinetics": "{pharma_esc}",',
        f'      "precautions": "{prec_esc}",',
        f'      "source": "{EDOXABAN_CONTENT["source"]}",',
        f'      "full_indications": "{indications_esc}",',
        f'      "full_dosage": "{dosage_esc}",',
        f'      "full_contraindications": "{contra_esc}",',
        f'      "full_adverse_reactions": "{adverse_esc}",',
        f'      "full_interactions": "{inter_esc}",',
        f'      "full_pregnancy_category": "{EDOXABAN_CONTENT["pregnancy_category"]}",',
        f'      "full_pharmacokinetics": "{pharma_esc}",',
        f'      "full_precautions": "{prec_esc}"',
        '    }'
    ]
    new_manual = '\n'.join(new_manual_lines)
    
    # 替换所有甲苯磺酸艾多沙班的 manual 部分
    pattern = r'("name":\s*"※▲甲苯磺酸艾多沙班"[\s\S]*?"spec_count":\s*\d+,\s*)"manual":\s*\{[\s\S]*?\}(\s*,\s*"pinyin")'
    
    count = len(re.findall(pattern, content))
    print(f"找到 {count} 个甲苯磺酸艾多沙班记录")
    
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
    
    print("\n✅ 甲苯磺酸艾多沙班手册内容更新完成！")
    print(f"更新了 {count} 个记录")
    print("更新内容：")
    print(f"  - 适应症: {EDOXABAN_CONTENT['indications'][:50]}...")
    print(f"  - 用法用量: {EDOXABAN_CONTENT['dosage'][:50]}...")
    print(f"  - 禁忌症: {EDOXABAN_CONTENT['contraindications'][:50]}...")
    print(f"  - 不良反应: {EDOXABAN_CONTENT['adverse_reactions']}")
    print(f"  - 来源: {EDOXABAN_CONTENT['source']}")

if __name__ == '__main__':
    main()
