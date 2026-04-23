#!/usr/bin/env python3
"""
批量更新注射液药品信息
从 hnysfww.com 爬取药品详细信息并更新到药品手册
"""

import json
import re
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# 基础配置
BASE_URL = "https://www.hnysfww.com"
DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 129个注射液药品列表
INJECTION_DRUGS = [
    {"id": 113, "name": "5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3185"},
    {"id": 114, "name": "50%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3185"},
    {"id": 569, "name": "银杏叶提取物", "url": "https://www.hnysfww.com/goods.php?id=381"},
    {"id": 721, "name": "醒脑静", "url": "https://www.hnysfww.com/goods.php?id=7438"},
    {"id": 794, "name": "丁甘交联玻璃酸钠", "url": "https://www.hnysfww.com/goods.php?id=13625"},
    {"id": 766, "name": "丹红", "url": "https://www.hnysfww.com/goods.php?id=5149"},
    {"id": 745, "name": "伊奈利珠单抗", "url": "https://www.hnysfww.com/goods.php?id=13524"},
    {"id": 540, "name": "利拉鲁肽", "url": "https://www.hnysfww.com/goods.php?id=1345"},
    {"id": 793, "name": "右酮洛芬氨丁三醇", "url": "https://www.hnysfww.com/goods.php?id=2746"},
    {"id": 733, "name": "司库奇尤单抗", "url": "https://www.hnysfww.com/goods.php?id=12950"},
    {"id": 997, "name": "天麻素", "url": "https://www.hnysfww.com/goods.php?id=737"},
    {"id": 785, "name": "奥马珠单抗", "url": "https://www.hnysfww.com/goods.php?id=3572"},
    {"id": 859, "name": "左西孟旦", "url": "https://www.hnysfww.com/goods.php?id=31"},
    {"id": 795, "name": "布比卡因脂质体", "url": "https://www.hnysfww.com/goods.php?id=2866"},
    {"id": 592, "name": "帕妥珠曲妥珠单抗", "url": "https://www.hnysfww.com/goods.php?id=13793"},
    {"id": 729, "name": "度拉糖肽", "url": "https://www.hnysfww.com/goods.php?id=11059"},
    {"id": 749, "name": "度普利尤单抗", "url": "https://www.hnysfww.com/goods.php?id=13078"},
    {"id": 768, "name": "德谷胰岛素利拉鲁肽", "url": "https://www.hnysfww.com/goods.php?id=13362"},
    {"id": 581, "name": "替雷利珠单抗", "url": "https://www.hnysfww.com/goods.php?id=12939"},
    {"id": 791, "name": "瑞帕妥单抗", "url": "https://www.hnysfww.com/goods.php?id=13566"},
    {"id": 789, "name": "盐酸伊立替康脂质体", "url": "https://www.hnysfww.com/goods.php?id=2539"},
    {"id": 849, "name": "盐酸艾司氯胺酮", "url": "https://www.hnysfww.com/goods.php?id=12935"},
    {"id": 757, "name": "盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 738, "name": "肾康", "url": "https://www.hnysfww.com/goods.php?id=4747"},
    {"id": 869, "name": "脂肪乳氨基酸葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3164"},
    {"id": 799, "name": "英克司兰钠", "url": "https://www.hnysfww.com/goods.php?id=13204"},
    {"id": 803, "name": "血必净", "url": "https://www.hnysfww.com/goods.php?id=5306"},
    {"id": 586, "name": "辅酶Q10", "url": "https://www.hnysfww.com/goods.php?id=24"},
    {"id": 571, "name": "重组人血管内皮抑制素", "url": "https://www.hnysfww.com/goods.php?id=3556"},
    {"id": 604, "name": "地舒单抗", "url": "https://www.hnysfww.com/goods.php?id=12809"},
    {"id": 916, "name": "硫酸庆大霉素", "url": "https://www.hnysfww.com/goods.php?id=1977"},
    {"id": 103, "name": "丁苯酞氯化钠", "url": "https://www.hnysfww.com/goods.php?id=385"},
    {"id": 629, "name": "丹参", "url": "https://www.hnysfww.com/goods.php?id=5156"},
    {"id": 788, "name": "乳酸环丙沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2090"},
    {"id": 847, "name": "亚甲蓝", "url": "https://www.hnysfww.com/goods.php?id=3282"},
    {"id": 105, "name": "人促红素", "url": "https://www.hnysfww.com/goods.php?id=3553"},
    {"id": 639, "name": "人粒细胞刺激因子", "url": "https://www.hnysfww.com/goods.php?id=3545"},
    {"id": 263, "name": "人胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1318"},
    {"id": 595, "name": "伊匹木单抗", "url": "https://www.hnysfww.com/goods.php?id=3586"},
    {"id": 558, "name": "依托泊苷", "url": "https://www.hnysfww.com/goods.php?id=2548"},
    {"id": 547, "name": "依达拉奉氯化钠", "url": "https://www.hnysfww.com/goods.php?id=985"},
    {"id": 549, "name": "依降钙素", "url": "https://www.hnysfww.com/goods.php?id=1462"},
    {"id": 606, "name": "信迪利单抗", "url": "https://www.hnysfww.com/goods.php?id=12906"},
    {"id": 439, "name": "克林霉素磷酸酯", "url": "https://www.hnysfww.com/goods.php?id=2039"},
    {"id": 804, "name": "利奈唑胺葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=2115"},
    {"id": 837, "name": "卡铂", "url": "https://www.hnysfww.com/goods.php?id=2589"},
    {"id": 905, "name": "去乙酰毛花苷", "url": "https://www.hnysfww.com/goods.php?id=4"},
    {"id": 277, "name": "呋塞米", "url": "https://www.hnysfww.com/goods.php?id=1727"},
    {"id": 826, "name": "咪达唑仑", "url": "https://www.hnysfww.com/goods.php?id=719"},
    {"id": 411, "name": "唑来膦酸", "url": "https://www.hnysfww.com/goods.php?id=1457"},
    {"id": 833, "name": "地佐辛", "url": "https://www.hnysfww.com/goods.php?id=1019"},
    {"id": 1024, "name": "地塞米松棕榈酸酯", "url": "https://www.hnysfww.com/goods.php?id=1240"},
    {"id": 830, "name": "地特胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1315"},
    {"id": 832, "name": "地西泮", "url": "https://www.hnysfww.com/goods.php?id=703"},
    {"id": 628, "name": "复方曲肽", "url": "https://www.hnysfww.com/goods.php?id=13247"},
    {"id": 684, "name": "复方氨基酸", "url": "https://www.hnysfww.com/goods.php?id=3127"},
    {"id": 387, "name": "多索茶碱", "url": "https://www.hnysfww.com/goods.php?id=1599"},
    {"id": 388, "name": "多西他赛", "url": "https://www.hnysfww.com/goods.php?id=2547"},
    {"id": 435, "name": "奥沙利铂", "url": "https://www.hnysfww.com/goods.php?id=2592"},
    {"id": 887, "name": "尼莫地平", "url": "https://www.hnysfww.com/goods.php?id=355"},
    {"id": 281, "name": "左氧氟沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 107, "name": "德谷门冬双胰岛素", "url": "https://www.hnysfww.com/goods.php?id=12964"},
    {"id": 934, "name": "托拉塞米", "url": "https://www.hnysfww.com/goods.php?id=1728"},
    {"id": 688, "name": "拉考沙胺", "url": "https://www.hnysfww.com/goods.php?id=861"},
    {"id": 295, "name": "枸橼酸芬太尼", "url": "https://www.hnysfww.com/goods.php?id=1005"},
    {"id": 900, "name": "氟哌啶醇", "url": "https://www.hnysfww.com/goods.php?id=752"},
    {"id": 234, "name": "氟康唑氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2178"},
    {"id": 781, "name": "氢溴酸加兰他敏", "url": "https://www.hnysfww.com/goods.php?id=1001"},
    {"id": 779, "name": "氨甲环酸", "url": "https://www.hnysfww.com/goods.php?id=1106"},
    {"id": 6, "name": "氨茶碱", "url": "https://www.hnysfww.com/goods.php?id=1598"},
    {"id": 5, "name": "氯化钾", "url": "https://www.hnysfww.com/goods.php?id=3193"},
    {"id": 658, "name": "注射用头孢地嗪钠/5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=1916"},
    {"id": 656, "name": "注射用头孢曲松钠/氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1907"},
    {"id": 444, "name": "浓氯化钠", "url": "https://www.hnysfww.com/goods.php?id=3189"},
    {"id": 741, "name": "特立帕肽", "url": "https://www.hnysfww.com/goods.php?id=1465"},
    {"id": 585, "name": "环磷腺苷葡胺", "url": "https://www.hnysfww.com/goods.php?id=25"},
    {"id": 681, "name": "甘精胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1314"},
    {"id": 736, "name": "甲氨蝶呤", "url": "https://www.hnysfww.com/goods.php?id=2481"},
    {"id": 86, "name": "甲硝唑氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2328"},
    {"id": 624, "name": "甲磺酸酚妥拉明", "url": "https://www.hnysfww.com/goods.php?id=153"},
    {"id": 1014, "name": "甲钴胺", "url": "https://www.hnysfww.com/goods.php?id=1076"},
    {"id": 565, "name": "盐酸乌拉地尔", "url": "https://www.hnysfww.com/goods.php?id=229"},
    {"id": 1027, "name": "盐酸二甲弗林", "url": "https://www.hnysfww.com/goods.php?id=943"},
    {"id": 641, "name": "盐酸倍他司汀", "url": "https://www.hnysfww.com/goods.php?id=377"},
    {"id": 77, "name": "盐酸克林霉素", "url": "https://www.hnysfww.com/goods.php?id=2038"},
    {"id": 35, "name": "盐酸利多卡因", "url": "https://www.hnysfww.com/goods.php?id=2864"},
    {"id": 431, "name": "盐酸右美托咪定", "url": "https://www.hnysfww.com/goods.php?id=2922"},
    {"id": 461, "name": "盐酸吗啡", "url": "https://www.hnysfww.com/goods.php?id=1003"},
    {"id": 560, "name": "盐酸哌替啶", "url": "https://www.hnysfww.com/goods.php?id=1004"},
    {"id": 786, "name": "盐酸帕洛诺司琼", "url": "https://www.hnysfww.com/goods.php?id=558"},
    {"id": 55, "name": "盐酸昂丹司琼", "url": "https://www.hnysfww.com/goods.php?id=551"},
    {"id": 917, "name": "盐酸普罗帕酮", "url": "https://www.hnysfww.com/goods.php?id=44"},
    {"id": 432, "name": "盐酸曲马多", "url": "https://www.hnysfww.com/goods.php?id=1029"},
    {"id": 130, "name": "盐酸氨溴索", "url": "https://www.hnysfww.com/goods.php?id=1586"},
    {"id": 434, "name": "盐酸氯丙嗪", "url": "https://www.hnysfww.com/goods.php?id=742"},
    {"id": 634, "name": "盐酸甲氧氯普胺", "url": "https://www.hnysfww.com/goods.php?id=537"},
    {"id": 631, "name": "盐酸精氨酸", "url": "https://www.hnysfww.com/goods.php?id=3117"},
    {"id": 563, "name": "盐酸维拉帕米", "url": "https://www.hnysfww.com/goods.php?id=85"},
    {"id": 753, "name": "盐酸肾上腺素", "url": "https://www.hnysfww.com/goods.php?id=141"},
    {"id": 132, "name": "盐酸胺碘酮", "url": "https://www.hnysfww.com/goods.php?id=78"},
    {"id": 185, "name": "盐酸艾司洛尔", "url": "https://www.hnysfww.com/goods.php?id=64"},
    {"id": 739, "name": "盐酸苯海拉明", "url": "https://www.hnysfww.com/goods.php?id=2645"},
    {"id": 398, "name": "盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 61, "name": "硝酸甘油", "url": "https://www.hnysfww.com/goods.php?id=96"},
    {"id": 852, "name": "硫酸妥布霉素", "url": "https://www.hnysfww.com/goods.php?id=1983"},
    {"id": 1029, "name": "硫酸镁", "url": "https://www.hnysfww.com/goods.php?id=1499"},
    {"id": 262, "name": "硫酸阿托品", "url": "https://www.hnysfww.com/goods.php?id=511"},
    {"id": 224, "name": "硫酸阿米卡星", "url": "https://www.hnysfww.com/goods.php?id=1980"},
    {"id": 983, "name": "碳酸氢钠", "url": "https://www.hnysfww.com/goods.php?id=3231"},
    {"id": 978, "name": "维生素B1", "url": "https://www.hnysfww.com/goods.php?id=3070"},
    {"id": 979, "name": "维生素B6", "url": "https://www.hnysfww.com/goods.php?id=3074"},
    {"id": 509, "name": "维生素C", "url": "https://www.hnysfww.com/goods.php?id=3076"},
    {"id": 510, "name": "维生素K1", "url": "https://www.hnysfww.com/goods.php?id=1098"},
    {"id": 735, "name": "缩宫素", "url": "https://www.hnysfww.com/goods.php?id=1477"},
    {"id": 725, "name": "罗库溴铵", "url": "https://www.hnysfww.com/goods.php?id=2913"},
    {"id": 647, "name": "羟乙基淀粉130/0.4氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1223"},
    {"id": 619, "name": "肌氨肽苷", "url": "https://www.hnysfww.com/goods.php?id=987"},
    {"id": 36, "name": "肌苷", "url": "https://www.hnysfww.com/goods.php?id=638"},
    {"id": 800, "name": "脑苷肌肽", "url": "https://www.hnysfww.com/goods.php?id=988"},
    {"id": 774, "name": "苯磺顺阿曲库铵", "url": "https://www.hnysfww.com/goods.php?id=2912"},
    {"id": 391, "name": "葡萄糖酸钙", "url": "https://www.hnysfww.com/goods.php?id=3199"},
    {"id": 419, "name": "贝伐珠单抗", "url": "https://www.hnysfww.com/goods.php?id=3569"},
    {"id": 610, "name": "赖脯胰岛素", "url": "https://www.hnysfww.com/goods.php?id=13390"},
    {"id": 609, "name": "那屈肝素钙", "url": "https://www.hnysfww.com/goods.php?id=1123"},
    {"id": 608, "name": "重组人血小板生成素", "url": "https://www.hnysfww.com/goods.php?id=3544"},
    {"id": 137, "name": "重酒石酸去甲肾上腺素", "url": "https://www.hnysfww.com/goods.php?id=142"},
    {"id": 3, "name": "钆特酸葡胺", "url": "https://www.hnysfww.com/goods.php?id=3336"},
    {"id": 946, "name": "门冬胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1312"},
    {"id": 700, "name": "阿加曲班", "url": "https://www.hnysfww.com/goods.php?id=1129"},
]


def fetch_drug_info(url):
    """从网页抓取药品详细信息"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取药品信息
        drug_info = {
            'indications': '',
            'dosage': '',
            'contraindications': '',
            'adverse_reactions': '',
            'interactions': '',
            'pregnancy_category': '',
            'pharmacokinetics': '',
            'precautions': ''
        }
        
        # 查找所有文本内容
        text_content = soup.get_text()
        
        # 提取适应症
        if '适应证' in text_content or '适应症' in text_content:
            indications_match = re.search(r'适应[证症][:：](.+?)(?:用法|禁忌|不良|药物相互作用|$)', text_content, re.DOTALL)
            if indications_match:
                drug_info['indications'] = clean_text(indications_match.group(1))
        
        # 提取用法用量
        if '用法与用量' in text_content:
            dosage_match = re.search(r'用法与用量[:：](.+?)(?:禁忌|不良|药物相互作用|药理作用|$)', text_content, re.DOTALL)
            if dosage_match:
                drug_info['dosage'] = clean_text(dosage_match.group(1))
        
        # 提取禁忌症
        if '禁忌' in text_content:
            contraindications_match = re.search(r'禁忌[:：](.+?)(?:不良|药物相互作用|注意事项|$)', text_content, re.DOTALL)
            if contraindications_match:
                drug_info['contraindications'] = clean_text(contraindications_match.group(1))
        
        # 提取不良反应
        if '不良反应' in text_content:
            adverse_match = re.search(r'不良反应[:：](.+?)(?:药物相互作用|注意事项|药理作用|$)', text_content, re.DOTALL)
            if adverse_match:
                drug_info['adverse_reactions'] = clean_text(adverse_match.group(1))
        
        # 提取药物相互作用
        if '药物相互作用' in text_content:
            interactions_match = re.search(r'药物相互作用[:：](.+?)(?:注意事项|药理作用|$)', text_content, re.DOTALL)
            if interactions_match:
                drug_info['interactions'] = clean_text(interactions_match.group(1))
        
        # 提取注意事项
        if '注意事项' in text_content:
            precautions_match = re.search(r'注意事项[:：](.+?)(?:药理作用|$)', text_content, re.DOTALL)
            if precautions_match:
                drug_info['precautions'] = clean_text(precautions_match.group(1))
        
        return drug_info
        
    except Exception as e:
        print(f"抓取失败: {url}, 错误: {e}")
        return None


def clean_text(text):
    """清理文本"""
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = text.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    # 限制长度
    if len(text) > 1000:
        text = text[:1000] + '...'
    return text.strip()


def update_drug_file(drug_id, drug_info):
    """更新药品JSON文件"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 更新manual字段
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        # 更新各个字段
        for key, value in drug_info.items():
            if value:  # 只更新非空值
                drug_data['manual'][key] = value
                # 同时更新full_版本
                drug_data['manual'][f'full_{key}'] = value
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"更新文件失败: {file_path}, 错误: {e}")
        return False


def main():
    """主函数"""
    print("开始更新129个注射液药品信息...")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, drug in enumerate(INJECTION_DRUGS, 1):
        print(f"\n[{i}/129] 处理: {drug['name']} (ID: {drug['id']})")
        print(f"URL: {drug['url']}")
        
        # 抓取信息
        drug_info = fetch_drug_info(drug['url'])
        
        if drug_info:
            # 更新文件
            if update_drug_file(drug['id'], drug_info):
                print(f"✓ 更新成功")
                success_count += 1
            else:
                print(f"✗ 更新失败")
                failed_count += 1
        else:
            print(f"✗ 抓取失败")
            failed_count += 1
        
        # 延时，避免请求过快
        time.sleep(2)
        
        # 每10个药品暂停一下
        if i % 10 == 0:
            print(f"\n已处理 {i} 个药品，暂停5秒...")
            time.sleep(5)
    
    print("\n" + "=" * 60)
    print("处理完成!")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    print(f"总计: {len(INJECTION_DRUGS)} 个")


if __name__ == "__main__":
    main()
