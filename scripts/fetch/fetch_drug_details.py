#!/usr/bin/env python3
"""
重新抓取药品详细信息
使用更可靠的解析方法
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

# 129个注射液药品列表
DRUGS_TO_UPDATE = [
    {"id": 113, "name": "5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3185"},
    {"id": 114, "name": "50%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3185"},
    {"id": 569, "name": "※※▲银杏叶提取物", "url": "https://www.hnysfww.com/goods.php?id=381"},
    {"id": 721, "name": "※※醒脑静", "url": "https://www.hnysfww.com/goods.php?id=7438"},
    {"id": 794, "name": "※▲丁甘交联玻璃酸钠", "url": "https://www.hnysfww.com/goods.php?id=13625"},
    {"id": 766, "name": "※▲丹红", "url": "https://www.hnysfww.com/goods.php?id=5149"},
    {"id": 745, "name": "※▲伊奈利珠单抗", "url": "https://www.hnysfww.com/goods.php?id=13524"},
    {"id": 540, "name": "※▲利拉鲁肽", "url": "https://www.hnysfww.com/goods.php?id=1345"},
    {"id": 793, "name": "※▲右酮洛芬氨丁三醇", "url": "https://www.hnysfww.com/goods.php?id=2746"},
    {"id": 733, "name": "※▲司库奇尤单抗", "url": "https://www.hnysfww.com/goods.php?id=12950"},
    {"id": 997, "name": "※▲天麻素", "url": "https://www.hnysfww.com/goods.php?id=737"},
    {"id": 785, "name": "※▲奥马珠单抗", "url": "https://www.hnysfww.com/goods.php?id=3572"},
    {"id": 859, "name": "※▲左西孟旦", "url": "https://www.hnysfww.com/goods.php?id=31"},
    {"id": 795, "name": "※▲布比卡因脂质体", "url": "https://www.hnysfww.com/goods.php?id=2866"},
    {"id": 592, "name": "※▲帕妥珠曲妥珠单抗", "url": "https://www.hnysfww.com/goods.php?id=13793"},
    {"id": 729, "name": "※▲度拉糖肽", "url": "https://www.hnysfww.com/goods.php?id=11059"},
    {"id": 749, "name": "※▲度普利尤单抗", "url": "https://www.hnysfww.com/goods.php?id=13078"},
    {"id": 768, "name": "※▲德谷胰岛素利拉鲁肽", "url": "https://www.hnysfww.com/goods.php?id=13362"},
    {"id": 581, "name": "※▲替雷利珠单抗", "url": "https://www.hnysfww.com/goods.php?id=12939"},
    {"id": 791, "name": "※▲瑞帕妥单抗", "url": "https://www.hnysfww.com/goods.php?id=13566"},
    {"id": 789, "name": "※▲盐酸伊立替康脂质体", "url": "https://www.hnysfww.com/goods.php?id=2539"},
    {"id": 849, "name": "※▲盐酸艾司氯胺酮", "url": "https://www.hnysfww.com/goods.php?id=12935"},
    {"id": 757, "name": "※▲盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 738, "name": "※▲甲磺酸萘莫司他", "url": "https://www.hnysfww.com/goods.php?id=13003"},
    {"id": 869, "name": "※▲硫酸艾沙康唑", "url": "https://www.hnysfww.com/goods.php?id=13079"},
    {"id": 799, "name": "※▲胞磷胆碱钠", "url": "https://www.hnysfww.com/goods.php?id=13689"},
    {"id": 803, "name": "※▲舒更葡糖钠", "url": "https://www.hnysfww.com/goods.php?id=2914"},
    {"id": 586, "name": "※▲西妥昔单抗", "url": "https://www.hnysfww.com/goods.php?id=3568"},
    {"id": 571, "name": "※▲贝伐珠单抗", "url": "https://www.hnysfww.com/goods.php?id=3569"},
    {"id": 604, "name": "※▲达雷妥尤单抗", "url": "https://www.hnysfww.com/goods.php?id=12944"},
    {"id": 916, "name": "七叶皂苷钠", "url": "https://www.hnysfww.com/goods.php?id=3060"},
    {"id": 103, "name": "丙氨酰谷氨酰胺", "url": "https://www.hnysfww.com/goods.php?id=3096"},
    {"id": 629, "name": "丙泊酚", "url": "https://www.hnysfww.com/goods.php?id=2920"},
    {"id": 788, "name": "丙种球蛋白", "url": "https://www.hnysfww.com/goods.php?id=3541"},
    {"id": 847, "name": "东莨菪碱", "url": "https://www.hnysfww.com/goods.php?id=513"},
    {"id": 105, "name": "中长链脂肪乳", "url": "https://www.hnysfww.com/goods.php?id=3084"},
    {"id": 639, "name": "乌拉地尔", "url": "https://www.hnysfww.com/goods.php?id=57"},
    {"id": 263, "name": "乳果糖", "url": "https://www.hnysfww.com/goods.php?id=1463"},
    {"id": 595, "name": "乳酸环丙沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2091"},
    {"id": 558, "name": "人血白蛋白", "url": "https://www.hnysfww.com/goods.php?id=3539"},
    {"id": 547, "name": "人胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1308"},
    {"id": 549, "name": "低分子量肝素钙", "url": "https://www.hnysfww.com/goods.php?id=1122"},
    {"id": 606, "name": "低钙腹膜透析液", "url": "https://www.hnysfww.com/goods.php?id=3205"},
    {"id": 439, "name": "依托咪酯", "url": "https://www.hnysfww.com/goods.php?id=2919"},
    {"id": 804, "name": "依达拉奉", "url": "https://www.hnysfww.com/goods.php?id=736"},
    {"id": 837, "name": "依达拉奉右莰醇", "url": "https://www.hnysfww.com/goods.php?id=13688"},
    {"id": 905, "name": "促肝细胞生长素", "url": "https://www.hnysfww.com/goods.php?id=990"},
    {"id": 277, "name": "克林霉素磷酸酯", "url": "https://www.hnysfww.com/goods.php?id=2002"},
    {"id": 826, "name": "兰地洛尔", "url": "https://www.hnysfww.com/goods.php?id=13519"},
    {"id": 411, "name": "利多卡因", "url": "https://www.hnysfww.com/goods.php?id=2863"},
    {"id": 833, "name": "利奈唑胺葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=2087"},
    {"id": 1024, "name": "前列地尔", "url": "https://www.hnysfww.com/goods.php?id=358"},
    {"id": 830, "name": "力肽", "url": "https://www.hnysfww.com/goods.php?id=3095"},
    {"id": 832, "name": "匹维溴铵", "url": "https://www.hnysfww.com/goods.php?id=1491"},
    {"id": 628, "name": "去乙酰毛花苷", "url": "https://www.hnysfww.com/goods.php?id=47"},
    {"id": 684, "name": "去氨加压素", "url": "https://www.hnysfww.com/goods.php?id=1271"},
    {"id": 387, "name": "地塞米松", "url": "https://www.hnysfww.com/goods.php?id=1257"},
    {"id": 388, "name": "地西泮", "url": "https://www.hnysfww.com/goods.php?id=730"},
    {"id": 435, "name": "地佐辛", "url": "https://www.hnysfww.com/goods.php?id=1014"},
    {"id": 887, "name": "地特胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1314"},
    {"id": 281, "name": "地衣芽孢杆菌活菌", "url": "https://www.hnysfww.com/goods.php?id=1492"},
    {"id": 107, "name": "复方氨基酸", "url": "https://www.hnysfww.com/goods.php?id=3097"},
    {"id": 934, "name": "复方脑肽节苷脂", "url": "https://www.hnysfww.com/goods.php?id=13691"},
    {"id": 688, "name": "多烯磷脂酰胆碱", "url": "https://www.hnysfww.com/goods.php?id=1523"},
    {"id": 295, "name": "多索茶碱", "url": "https://www.hnysfww.com/goods.php?id=1605"},
    {"id": 900, "name": "夫西地酸", "url": "https://www.hnysfww.com/goods.php?id=1998"},
    {"id": 234, "name": "奥美拉唑", "url": "https://www.hnysfww.com/goods.php?id=1534"},
    {"id": 781, "name": "奥马珠单抗", "url": "https://www.hnysfww.com/goods.php?id=3572"},
    {"id": 779, "name": "奥硝唑氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 6, "name": "奥扎格雷", "url": "https://www.hnysfww.com/goods.php?id=1128"},
    {"id": 5, "name": "奥扎格雷钠", "url": "https://www.hnysfww.com/goods.php?id=1128"},
    {"id": 658, "name": "妥布霉素地塞米松", "url": "https://www.hnysfww.com/goods.php?id=1983"},
    {"id": 656, "name": "姜黄素", "url": "https://www.hnysfww.com/goods.php?id=13690"},
    {"id": 444, "name": "尼可刹米", "url": "https://www.hnysfww.com/goods.php?id=52"},
    {"id": 741, "name": "尼莫地平", "url": "https://www.hnysfww.com/goods.php?id=94"},
    {"id": 585, "name": "尿激酶", "url": "https://www.hnysfww.com/goods.php?id=1119"},
    {"id": 681, "name": "左卡尼汀", "url": "https://www.hnysfww.com/goods.php?id=3100"},
    {"id": 736, "name": "左氧氟沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2090"},
    {"id": 86, "name": "布地奈德", "url": "https://www.hnysfww.com/goods.php?id=1566"},
    {"id": 624, "name": "布美他尼", "url": "https://www.hnysfww.com/goods.php?id=1205"},
    {"id": 1014, "name": "垂体后叶", "url": "https://www.hnysfww.com/goods.php?id=1478"},
    {"id": 565, "name": "庆大霉素普鲁卡因维B12", "url": "https://www.hnysfww.com/goods.php?id=2006"},
    {"id": 1027, "name": "康艾", "url": "https://www.hnysfww.com/goods.php?id=13687"},
    {"id": 641, "name": "康莱特", "url": "https://www.hnysfww.com/goods.php?id=13686"},
    {"id": 77, "name": "异丙嗪", "url": "https://www.hnysfww.com/goods.php?id=2645"},
    {"id": 35, "name": "异丙肾上腺素", "url": "https://www.hnysfww.com/goods.php?id=145"},
    {"id": 431, "name": "异甘草酸镁", "url": "https://www.hnysfww.com/goods.php?id=1522"},
    {"id": 461, "name": "枸橼酸芬太尼", "url": "https://www.hnysfww.com/goods.php?id=1002"},
    {"id": 560, "name": "枸橼酸舒芬太尼", "url": "https://www.hnysfww.com/goods.php?id=1005"},
    {"id": 786, "name": "氨甲环酸", "url": "https://www.hnysfww.com/goods.php?id=1088"},
    {"id": 55, "name": "氨茶碱", "url": "https://www.hnysfww.com/goods.php?id=1603"},
    {"id": 917, "name": "氨溴索", "url": "https://www.hnysfww.com/goods.php?id=1586"},
    {"id": 432, "name": "氯化钾", "url": "https://www.hnysfww.com/goods.php?id=3188"},
    {"id": 130, "name": "氯化钠", "url": "https://www.hnysfww.com/goods.php?id=3186"},
    {"id": 434, "name": "氯化琥珀胆碱", "url": "https://www.hnysfww.com/goods.php?id=2910"},
    {"id": 634, "name": "法莫替丁", "url": "https://www.hnysfww.com/goods.php?id=1540"},
    {"id": 631, "name": "注射用水", "url": "https://www.hnysfww.com/goods.php?id=3117"},
    {"id": 563, "name": "泮托拉唑", "url": "https://www.hnysfww.com/goods.php?id=1535"},
    {"id": 753, "name": "泽布替尼", "url": "https://www.hnysfww.com/goods.php?id=12940"},
    {"id": 132, "name": "浓氯化钠", "url": "https://www.hnysfww.com/goods.php?id=3187"},
    {"id": 185, "name": "消旋山莨菪碱", "url": "https://www.hnysfww.com/goods.php?id=515"},
    {"id": 739, "name": "脂肪乳氨基酸葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3086"},
    {"id": 398, "name": "舒血宁", "url": "https://www.hnysfww.com/goods.php?id=5150"},
    {"id": 61, "name": "艾司洛尔", "url": "https://www.hnysfww.com/goods.php?id=64"},
    {"id": 852, "name": "艾司奥美拉唑", "url": "https://www.hnysfww.com/goods.php?id=1536"},
    {"id": 1029, "name": "艾迪", "url": "https://www.hnysfww.com/goods.php?id=5148"},
    {"id": 262, "name": "苄星青霉素", "url": "https://www.hnysfww.com/goods.php?id=1975"},
    {"id": 224, "name": "苯巴比妥", "url": "https://www.hnysfww.com/goods.php?id=728"},
    {"id": 983, "name": "血必净", "url": "https://www.hnysfww.com/goods.php?id=5147"},
    {"id": 978, "name": "西咪替丁", "url": "https://www.hnysfww.com/goods.php?id=1539"},
    {"id": 979, "name": "谷氨酸钠", "url": "https://www.hnysfww.com/goods.php?id=3119"},
    {"id": 509, "name": "谷胱甘肽", "url": "https://www.hnysfww.com/goods.php?id=1521"},
    {"id": 510, "name": "谷红", "url": "https://www.hnysfww.com/goods.php?id=987"},
    {"id": 735, "name": "贝伐珠单抗", "url": "https://www.hnysfww.com/goods.php?id=3569"},
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

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = text.strip()
    return text

def fetch_drug_info(url):
    """从网页抓取药品详细信息"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 初始化药品信息
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
        
        # 查找药品详情区域
        # 尝试多种可能的选择器
        detail_div = soup.find('div', class_='detail') or \
                     soup.find('div', class_='goods-detail') or \
                     soup.find('div', id='detail') or \
                     soup.find('div', class_='content')
        
        if detail_div:
            text = detail_div.get_text(separator='\n', strip=True)
        else:
            # 如果没有找到特定区域，获取整个body文本
            text = soup.get_text(separator='\n', strip=True)
        
        # 提取适应症
        indications_patterns = [
            r'适应[证症][:：]\s*([^\n]+(?:\n(?![\[【](?:禁忌|不良|用法|药物相互作用|注意事项|药理作用)[\]】]).*)*)',
            r'【适应[证症]】\s*([^\n]+(?:\n(?![【\[]).*)*)',
        ]
        for pattern in indications_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                drug_info['indications'] = clean_text(match.group(1))
                break
        
        # 提取用法用量
        dosage_patterns = [
            r'用法与用量[:：]\s*([^\n]+(?:\n(?![\[【](?:禁忌|不良|药物相互作用|注意事项|药理作用)[\]】]).*)*)',
            r'【用法与用量】\s*([^\n]+(?:\n(?![【\[]).*)*)',
            r'用法用量[:：]\s*([^\n]+(?:\n(?![\[【]).*)*)',
        ]
        for pattern in dosage_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                drug_info['dosage'] = clean_text(match.group(1))
                break
        
        # 提取禁忌症
        contraindications_patterns = [
            r'禁忌[:：]\s*([^\n]+(?:\n(?![\[【](?:不良|药物相互作用|注意事项|药理作用)[\]】]).*)*)',
            r'【禁忌】\s*([^\n]+(?:\n(?![【\[]).*)*)',
        ]
        for pattern in contraindications_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                drug_info['contraindications'] = clean_text(match.group(1))
                break
        
        # 提取不良反应
        adverse_patterns = [
            r'不良反应[:：]\s*([^\n]+(?:\n(?![\[【](?:药物相互作用|注意事项|药理作用)[\]】]).*)*)',
            r'【不良反应】\s*([^\n]+(?:\n(?![【\[]).*)*)',
        ]
        for pattern in adverse_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                drug_info['adverse_reactions'] = clean_text(match.group(1))
                break
        
        # 提取药物相互作用
        interactions_patterns = [
            r'药物相互作用[:：]\s*([^\n]+(?:\n(?![\[【](?:注意事项|药理作用)[\]】]).*)*)',
            r'【药物相互作用】\s*([^\n]+(?:\n(?![【\[]).*)*)',
        ]
        for pattern in interactions_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                drug_info['interactions'] = clean_text(match.group(1))
                break
        
        # 提取注意事项
        precautions_patterns = [
            r'注意事项[:：]\s*([^\n]+(?:\n(?![\[【](?:药理作用)[\]】]).*)*)',
            r'【注意事项】\s*([^\n]+(?:\n(?![【\[]).*)*)',
        ]
        for pattern in precautions_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                drug_info['precautions'] = clean_text(match.group(1))
                break
        
        # 检查是否抓取到有效数据
        has_data = any(v.strip() for v in drug_info.values())
        
        if not has_data:
            return None, "未找到药品详细信息"
        
        return drug_info, None
        
    except Exception as e:
        return None, str(e)

def update_drug_file(drug_id, drug_info):
    """更新药品JSON文件"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return False, "文件不存在"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新manual字段
        if 'manual' not in data:
            data['manual'] = {}
        
        manual = data['manual']
        
        # 更新字段
        for key, value in drug_info.items():
            if value.strip():  # 只更新非空值
                manual[key] = value
                manual[f'full_{key}'] = value
        
        manual['source'] = 'https://www.hnysfww.com'
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True, None
        
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print("=" * 80)
    print("重新抓取129个注射液药品详细信息")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    fail_list = []
    
    for i, drug in enumerate(DRUGS_TO_UPDATE, 1):
        print(f"\n[{i}/{len(DRUGS_TO_UPDATE)}] 处理: {drug['name']} (ID: {drug['id']})")
        print(f"URL: {drug['url']}")
        
        # 抓取数据
        drug_info, error = fetch_drug_info(drug['url'])
        
        if error:
            print(f"✗ 抓取失败: {error}")
            fail_count += 1
            fail_list.append({"id": drug['id'], "name": drug['name'], "error": error})
            continue
        
        # 显示抓取到的数据摘要
        print("抓取到的数据:")
        for key, value in drug_info.items():
            if value.strip():
                preview = value[:50] + "..." if len(value) > 50 else value
                print(f"  - {key}: {preview}")
        
        # 更新文件
        success, error = update_drug_file(drug['id'], drug_info)
        
        if success:
            print(f"✓ 更新成功")
            success_count += 1
        else:
            print(f"✗ 更新失败: {error}")
            fail_count += 1
            fail_list.append({"id": drug['id'], "name": drug['name'], "error": error})
        
        # 每10个暂停一下
        if i % 10 == 0:
            print(f"\n已处理 {i} 个药品，暂停5秒...")
            time.sleep(5)
        else:
            time.sleep(1)
    
    # 输出统计
    print("\n" + "=" * 80)
    print("处理完成!")
    print("=" * 80)
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"总计: {len(DRUGS_TO_UPDATE)} 个")
    
    if fail_list:
        print("\n失败的药品:")
        for item in fail_list:
            print(f"  - ID {item['id']} {item['name']}: {item['error']}")

if __name__ == "__main__":
    main()
