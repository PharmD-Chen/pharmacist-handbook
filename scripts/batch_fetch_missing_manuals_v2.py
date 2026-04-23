#!/usr/bin/env python3
"""
批量获取缺失说明书内容的药品
从湖南药事服务网获取并更新JSON文件
"""

import json
import re
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# 药品数据目录
DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

# 需要更新的药品列表（从文档中解析）
DRUGS_TO_UPDATE = [
    {"id": 730, "name": "胰酶", "url": "https://www.hnysfww.com/goods.php?id=500"},
    {"id": 750, "name": "除湿止痒", "url": "https://www.hnysfww.com/goods.php?id=8218"},
    {"id": 783, "name": "氟伐他汀钠", "url": "https://www.hnysfww.com/goods.php?id=311"},
    {"id": 792, "name": "※▲酮洛芬凝胶", "url": "https://www.hnysfww.com/goods.php?id=2717"},
    {"id": 798, "name": "丙酸氟替卡松", "url": "https://www.hnysfww.com/goods.php?id=1654"},
    {"id": 810, "name": "复方甲氧那明", "url": "https://www.hnysfww.com/goods.php?id=1668"},
    {"id": 812, "name": "非诺贝特", "url": "https://www.hnysfww.com/goods.php?id=13546"},
    {"id": 813, "name": "芬太尼透皮", "url": "https://www.hnysfww.com/goods.php?id=1005"},
    {"id": 822, "name": "氧氟沙星", "url": "https://www.hnysfww.com/goods.php?id=2088"},
    {"id": 827, "name": "噻托溴铵粉雾剂", "url": "https://www.hnysfww.com/goods.php?id=1631"},
    {"id": 836, "name": "麝香痔疮栓", "url": "https://www.hnysfww.com/goods.php?id=4733"},
    {"id": 842, "name": "缬沙坦", "url": "https://www.hnysfww.com/goods.php?id=203"},
    {"id": 845, "name": "血塞通", "url": "https://www.hnysfww.com/goods.php?id=5180"},
    {"id": 865, "name": "盐酸班布特罗", "url": "https://www.hnysfww.com/goods.php?id=1608"},
    {"id": 878, "name": "浓替硝唑含漱液", "url": "https://www.hnysfww.com/goods.php?id=2331"},
    {"id": 884, "name": "碳酸锂", "url": "https://www.hnysfww.com/goods.php?id=851"},
    {"id": 896, "name": "※▲苯磺酸克利加巴林", "url": "https://www.hnysfww.com/goods.php?id=13775"},
    {"id": 897, "name": "丹参酮", "url": "https://www.hnysfww.com/goods.php?id=5289"},
    {"id": 921, "name": "酒石酸长春瑞滨软", "url": "https://www.hnysfww.com/goods.php?id=2543"},
    {"id": 935, "name": "多烯磷脂酰胆碱", "url": "https://www.hnysfww.com/goods.php?id=634"},
    {"id": 942, "name": "抗凝血用枸橼酸钠溶液", "url": "https://www.hnysfww.com/goods.php?id=1139"},
    {"id": 945, "name": "※注射用糜蛋白酶", "url": "https://www.hnysfww.com/goods.php?id=3664"},
    {"id": 950, "name": "麻仁软", "url": "https://www.hnysfww.com/goods.php?id=7032"},
    {"id": 964, "name": "坤泰", "url": "https://www.hnysfww.com/goods.php?id=6672"},
    {"id": 965, "name": "兰索拉唑肠溶", "url": "https://www.hnysfww.com/goods.php?id=414"},
    {"id": 973, "name": "积雪苷霜", "url": "https://www.hnysfww.com/goods.php?id=8146"},
    {"id": 981, "name": "他克莫司", "url": "https://www.hnysfww.com/goods.php?id=1806"},
    {"id": 989, "name": "※▲乌帕替尼", "url": "https://www.hnysfww.com/goods.php?id=13235"},
    {"id": 993, "name": "胃复春", "url": "https://www.hnysfww.com/goods.php?id=6303"},
    {"id": 1002, "name": "盐酸丙美卡因", "url": "https://www.hnysfww.com/goods.php?id=2862"},
    {"id": 1008, "name": "※▲麦考酚钠", "url": "https://www.hnysfww.com/goods.php?id=1808"},
    {"id": 1012, "name": "硫酸钡干", "url": "https://www.hnysfww.com/goods.php?id=3319"},
    {"id": 1022, "name": "大活络", "url": "https://www.hnysfww.com/goods.php?id=7242"},
    {"id": 1026, "name": "甲磺酸二氢麦角碱", "url": "https://www.hnysfww.com/goods.php?id=982"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def extract_field(text, field_name, next_fields):
    """提取字段内容"""
    pattern = rf'{field_name}(.+?)(?:{"|".join(next_fields)}|$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return clean_text(match.group(1))
    return ""

def fetch_drug_info(url):
    """从网页获取药品信息"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if not tables:
            return None

        text = tables[0].get_text()

        # 提取各字段
        info = {}

        # 适应证/功能主治
        indications = ""
        match = re.search(r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            indications = clean_text(match.group(1))
        else:
            match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
            if match:
                indications = clean_text(match.group(1))
        info['indications'] = indications

        # 用法用量
        dosage = ""
        match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            dosage = clean_text(match.group(1))
        info['dosage'] = dosage

        # 禁忌
        contraindications = ""
        match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            contraindications = clean_text(match.group(1))
        info['contraindications'] = contraindications

        # 不良反应
        adverse_reactions = ""
        match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            adverse_reactions = clean_text(match.group(1))
        info['adverse_reactions'] = adverse_reactions

        # 药物相互作用
        interactions = ""
        match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            interactions = clean_text(match.group(1))
        info['interactions'] = interactions

        # 注意事项
        precautions = ""
        match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
        if match:
            precautions = clean_text(match.group(1))
        info['precautions'] = precautions

        # 妊娠分级
        pregnancy = ""
        match = re.search(r'妊娠期用药安全分级\s*([A-Z]\s*级?)', text)
        if match:
            pregnancy = match.group(1)
        else:
            match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
            if match:
                pregnancy = match.group(1)
        info['pregnancy_category'] = pregnancy

        return info

    except Exception as e:
        print(f"    获取失败: {e}")
        return None

def update_drug_json(drug_id, drug_info, url):
    """更新药品JSON文件"""
    json_file = DATA_DIR / f'{drug_id}.json'

    if not json_file.exists():
        print(f"    JSON文件不存在")
        return False

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 更新URL
        if 'url' not in data:
            data['url'] = {}
        data['url']['hnysfww'] = url

        # 更新手册内容
        if 'manual' not in data:
            data['manual'] = {}

        manual = data['manual']

        # 更新各字段（精简版和详细版相同）
        if drug_info.get('indications'):
            manual['indications'] = drug_info['indications']
            manual['full_indications'] = drug_info['indications']

        if drug_info.get('dosage'):
            manual['dosage'] = drug_info['dosage']
            manual['full_dosage'] = drug_info['dosage']

        if drug_info.get('contraindications'):
            manual['contraindications'] = drug_info['contraindications']
            manual['full_contraindications'] = drug_info['contraindications']

        if drug_info.get('adverse_reactions'):
            manual['adverse_reactions'] = drug_info['adverse_reactions']
            manual['full_adverse_reactions'] = drug_info['adverse_reactions']

        if drug_info.get('interactions'):
            manual['interactions'] = drug_info['interactions']
            manual['full_interactions'] = drug_info['interactions']

        if drug_info.get('precautions'):
            manual['precautions'] = drug_info['precautions']
            manual['full_precautions'] = drug_info['precautions']

        if drug_info.get('pregnancy_category'):
            manual['pregnancy_category'] = drug_info['pregnancy_category']

        # 保存文件
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    except Exception as e:
        print(f"    更新失败: {e}")
        return False

def main():
    print('=' * 80)
    print('批量获取缺失说明书内容的药品')
    print('=' * 80)
    print()

    success_count = 0
    fail_count = 0

    for i, drug in enumerate(DRUGS_TO_UPDATE, 1):
        drug_id = drug['id']
        name = drug['name']
        url = drug['url']

        print(f'[{i}/{len(DRUGS_TO_UPDATE)}] ID:{drug_id} {name}')
        print(f'    网址: {url}')

        # 获取药品信息
        drug_info = fetch_drug_info(url)

        if drug_info:
            # 更新JSON文件
            if update_drug_json(drug_id, drug_info, url):
                print(f'    ✅ 更新成功')
                success_count += 1
            else:
                print(f'    ❌ 更新失败')
                fail_count += 1
        else:
            print(f'    ❌ 获取信息失败')
            fail_count += 1

        # 延迟避免请求过快
        time.sleep(1)
        print()

    print('=' * 80)
    print('处理完成!')
    print(f'  - 成功: {success_count}个')
    print(f'  - 失败: {fail_count}个')
    print(f'  - 总计: {len(DRUGS_TO_UPDATE)}个')
    print('=' * 80)

if __name__ == '__main__':
    main()
