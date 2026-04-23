#!/usr/bin/env python3
"""
检查指定范围内的药品下载状态
"""

import json
from pathlib import Path

# 从L224-352的药品列表
DRUGS_LIST = [
    {"id": 113, "name": "5%葡萄糖"},
    {"id": 114, "name": "50%葡萄糖"},
    {"id": 569, "name": "※※▲银杏叶提取物"},
    {"id": 721, "name": "※※醒脑静"},
    {"id": 794, "name": "※▲丁甘交联玻璃酸钠"},
    {"id": 766, "name": "※▲丹红"},
    {"id": 745, "name": "※▲伊奈利珠单抗"},
    {"id": 540, "name": "※▲利拉鲁肽"},
    {"id": 793, "name": "※▲右酮洛芬氨丁三醇"},
    {"id": 733, "name": "※▲司库奇尤单抗"},
    {"id": 997, "name": "※▲天麻素"},
    {"id": 785, "name": "※▲奥马珠单抗"},
    {"id": 859, "name": "※▲左西孟旦"},
    {"id": 795, "name": "※▲布比卡因脂质体"},
    {"id": 592, "name": "※▲帕妥珠曲妥珠单抗"},
    {"id": 729, "name": "※▲度拉糖肽"},
    {"id": 749, "name": "※▲度普利尤单抗"},
    {"id": 768, "name": "※▲德谷胰岛素利拉鲁肽"},
    {"id": 581, "name": "※▲替雷利珠单抗"},
    {"id": 791, "name": "※▲瑞帕妥单抗"},
    {"id": 789, "name": "※▲盐酸伊立替康脂质体"},
    {"id": 849, "name": "※▲盐酸艾司氯胺酮"},
    {"id": 757, "name": "※▲盐酸莫西沙星氯化钠"},
    {"id": 738, "name": "※▲肾康"},
    {"id": 869, "name": "※▲脂肪乳氨基酸葡萄糖"},
    {"id": 799, "name": "※▲英克司兰钠"},
    {"id": 803, "name": "※▲血必净"},
    {"id": 586, "name": "※▲辅酶Q10"},
    {"id": 571, "name": "※▲重组人血管内皮抑制素"},
    {"id": 604, "name": "※地舒单抗"},
    {"id": 916, "name": "※硫酸庆大霉素"},
    {"id": 103, "name": "丁苯酞氯化钠"},
    {"id": 629, "name": "丹参"},
    {"id": 788, "name": "乳酸环丙沙星氯化钠"},
    {"id": 847, "name": "亚甲蓝"},
    {"id": 105, "name": "人促红素"},
    {"id": 639, "name": "人粒细胞刺激因子"},
    {"id": 263, "name": "人胰岛素"},
    {"id": 595, "name": "伊匹木单抗"},
    {"id": 558, "name": "依托泊苷"},
    {"id": 547, "name": "依达拉奉氯化钠"},
    {"id": 549, "name": "依降钙素"},
    {"id": 606, "name": "信迪利单抗"},
    {"id": 439, "name": "克林霉素磷酸酯"},
    {"id": 804, "name": "利奈唑胺葡萄糖"},
    {"id": 837, "name": "卡铂"},
    {"id": 905, "name": "去乙酰毛花苷"},
    {"id": 277, "name": "呋塞米"},
    {"id": 826, "name": "咪达唑仑"},
    {"id": 411, "name": "唑来膦酸"},
    {"id": 833, "name": "地佐辛"},
    {"id": 1024, "name": "地塞米松棕榈酸酯"},
    {"id": 830, "name": "地特胰岛素"},
    {"id": 832, "name": "地西泮"},
    {"id": 628, "name": "复方曲肽"},
    {"id": 684, "name": "复方氨基酸"},
    {"id": 387, "name": "多索茶碱"},
    {"id": 388, "name": "多西他赛"},
    {"id": 435, "name": "奥沙利铂"},
    {"id": 887, "name": "尼莫地平"},
    {"id": 281, "name": "左氧氟沙星氯化钠"},
    {"id": 107, "name": "德谷门冬双胰岛素"},
    {"id": 934, "name": "托拉塞米"},
    {"id": 688, "name": "拉考沙胺"},
    {"id": 295, "name": "枸橼酸芬太尼"},
    {"id": 900, "name": "氟哌啶醇"},
    {"id": 234, "name": "氟康唑氯化钠"},
    {"id": 781, "name": "氢溴酸加兰他敏"},
    {"id": 779, "name": "氨甲环酸"},
    {"id": 6, "name": "氨茶碱"},
    {"id": 5, "name": "氯化钾"},
    {"id": 658, "name": "注射用头孢地嗪钠/5%葡萄糖"},
    {"id": 656, "name": "注射用头孢曲松钠/氯化钠"},
    {"id": 444, "name": "浓氯化钠"},
    {"id": 741, "name": "特立帕肽"},
    {"id": 585, "name": "环磷腺苷葡胺"},
    {"id": 681, "name": "甘精胰岛素"},
    {"id": 736, "name": "甲氨蝶呤"},
    {"id": 86, "name": "甲硝唑氯化钠"},
    {"id": 624, "name": "甲磺酸酚妥拉明"},
    {"id": 1014, "name": "甲钴胺"},
    {"id": 565, "name": "盐酸乌拉地尔"},
    {"id": 1027, "name": "盐酸二甲弗林"},
    {"id": 641, "name": "盐酸倍他司汀"},
    {"id": 77, "name": "盐酸克林霉素"},
    {"id": 35, "name": "盐酸利多卡因"},
    {"id": 431, "name": "盐酸右美托咪定"},
    {"id": 461, "name": "盐酸吗啡"},
    {"id": 560, "name": "盐酸哌替啶"},
    {"id": 786, "name": "盐酸帕洛诺司琼"},
    {"id": 55, "name": "盐酸昂丹司琼"},
    {"id": 917, "name": "盐酸普罗帕酮"},
    {"id": 432, "name": "盐酸曲马多"},
    {"id": 130, "name": "盐酸氨溴索"},
    {"id": 434, "name": "盐酸氯丙嗪"},
    {"id": 634, "name": "盐酸甲氧氯普胺"},
    {"id": 631, "name": "盐酸精氨酸"},
    {"id": 563, "name": "盐酸维拉帕米"},
    {"id": 753, "name": "盐酸肾上腺素"},
    {"id": 132, "name": "盐酸胺碘酮"},
    {"id": 185, "name": "盐酸艾司洛尔"},
    {"id": 739, "name": "盐酸苯海拉明"},
    {"id": 398, "name": "盐酸莫西沙星氯化钠"},
    {"id": 61, "name": "硝酸甘油"},
    {"id": 852, "name": "硫酸妥布霉素"},
    {"id": 1029, "name": "硫酸镁"},
    {"id": 262, "name": "硫酸阿托品"},
    {"id": 224, "name": "硫酸阿米卡星"},
    {"id": 983, "name": "碳酸氢钠"},
    {"id": 978, "name": "维生素B1"},
    {"id": 979, "name": "维生素B6"},
    {"id": 509, "name": "维生素C"},
    {"id": 510, "name": "维生素K1"},
    {"id": 735, "name": "缩宫素"},
    {"id": 725, "name": "罗库溴铵"},
    {"id": 647, "name": "羟乙基淀粉130/0.4氯化钠"},
    {"id": 619, "name": "肌氨肽苷"},
    {"id": 36, "name": "肌苷"},
    {"id": 800, "name": "脑苷肌肽"},
    {"id": 774, "name": "苯磺顺阿曲库铵"},
    {"id": 391, "name": "葡萄糖酸钙"},
    {"id": 419, "name": "贝伐珠单抗"},
    {"id": 610, "name": "赖脯胰岛素"},
    {"id": 609, "name": "那屈肝素钙"},
    {"id": 608, "name": "重组人血小板生成素"},
    {"id": 137, "name": "重酒石酸去甲肾上腺素"},
    {"id": 3, "name": "钆特酸葡胺"},
    {"id": 946, "name": "门冬胰岛素"},
    {"id": 700, "name": "阿加曲班"},
]

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")


def check_drug_status(drug_id):
    """检查单个药品的状态"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return "missing", "文件不存在"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        
        # 检查关键字段是否为空
        empty_fields = []
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions']
        
        for field in key_fields:
            value = manual.get(field, '')
            if not value or value.strip() == '':
                empty_fields.append(field)
        
        # 检查source字段
        source = manual.get('source', '')
        
        if empty_fields:
            return "incomplete", f"缺少: {', '.join(empty_fields)}"
        elif not source or source == '':
            return "no_source", "有内容但无来源"
        elif source != "湖南药事服务网":
            return "wrong_source", f"来源: {source}"
        else:
            return "complete", "完整"
            
    except Exception as e:
        return "error", f"错误: {e}"


def main():
    """主函数"""
    print("=" * 80)
    print("药品下载状态检查 (L224-352)")
    print("=" * 80)
    
    status_count = {
        "complete": 0,
        "incomplete": 0,
        "no_source": 0,
        "wrong_source": 0,
        "missing": 0,
        "error": 0
    }
    
    incomplete_drugs = []
    no_source_drugs = []
    wrong_source_drugs = []
    missing_drugs = []
    
    for drug in DRUGS_LIST:
        status, message = check_drug_status(drug['id'])
        status_count[status] += 1
        
        if status == "incomplete":
            incomplete_drugs.append((drug, message))
        elif status == "no_source":
            no_source_drugs.append((drug, message))
        elif status == "wrong_source":
            wrong_source_drugs.append((drug, message))
        elif status == "missing":
            missing_drugs.append((drug, message))
    
    # 打印统计
    print(f"\n总计: {len(DRUGS_LIST)} 个药品")
    print(f"  ✅ 完整: {status_count['complete']} 个")
    print(f"  ⚠️  信息不完整: {status_count['incomplete']} 个")
    print(f"  ⚠️  无来源标注: {status_count['no_source']} 个")
    print(f"  ⚠️  来源非湖南药事服务网: {status_count['wrong_source']} 个")
    print(f"  ❌ 文件不存在: {status_count['missing']} 个")
    print(f"  ❌ 读取错误: {status_count['error']} 个")
    
    # 打印需要处理的药品
    if incomplete_drugs:
        print("\n" + "=" * 80)
        print(f"【信息不完整】({len(incomplete_drugs)} 个)")
        print("=" * 80)
        for drug, msg in incomplete_drugs:
            print(f"  ID: {drug['id']:<6} 名称: {drug['name']:<30} {msg}")
    
    if no_source_drugs:
        print("\n" + "=" * 80)
        print(f"【无来源标注】({len(no_source_drugs)} 个)")
        print("=" * 80)
        for drug, msg in no_source_drugs:
            print(f"  ID: {drug['id']:<6} 名称: {drug['name']:<30}")
    
    if wrong_source_drugs:
        print("\n" + "=" * 80)
        print(f"【来源非湖南药事服务网】({len(wrong_source_drugs)} 个)")
        print("=" * 80)
        for drug, msg in wrong_source_drugs:
            print(f"  ID: {drug['id']:<6} 名称: {drug['name']:<30} {msg}")
    
    if missing_drugs:
        print("\n" + "=" * 80)
        print(f"【文件不存在】({len(missing_drugs)} 个)")
        print("=" * 80)
        for drug, msg in missing_drugs:
            print(f"  ID: {drug['id']:<6} 名称: {drug['name']:<30}")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
