#!/usr/bin/env python3
"""
从湖南药事服务网获取抗生素类药品信息
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

# 抗生素类药品列表
ANTIBIOTIC_DRUGS = [
    {"id": 282, "name": "左氧氟沙星片", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 970, "name": "甲硝唑片", "url": "https://www.hnysfww.com/goods.php?id=2328"},
    {"id": 495, "name": "盐酸莫西沙星片", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 677, "name": "阿奇霉素片", "url": "https://www.hnysfww.com/goods.php?id=2016"},
    {"id": 757, "name": "※▲盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 916, "name": "※硫酸庆大霉素", "url": "https://www.hnysfww.com/goods.php?id=1977"},
    {"id": 439, "name": "克林霉素磷酸酯", "url": "https://www.hnysfww.com/goods.php?id=2039"},
    {"id": 804, "name": "利奈唑胺葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=2115"},
    {"id": 281, "name": "左氧氟沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 658, "name": "注射用头孢地嗪钠/5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=1916"},
    {"id": 656, "name": "注射用头孢曲松钠/氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1907"},
    {"id": 86, "name": "甲硝唑氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2328"},
    {"id": 77, "name": "盐酸克林霉素", "url": "https://www.hnysfww.com/goods.php?id=2038"},
    {"id": 398, "name": "盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 224, "name": "硫酸阿米卡星", "url": "https://www.hnysfww.com/goods.php?id=1980"},
    {"id": 980, "name": "头孢克洛", "url": ""},
    {"id": 944, "name": "头孢拉定", "url": ""},
    {"id": 991, "name": "阿莫西林", "url": ""},
    {"id": 878, "name": "浓替硝唑含漱液", "url": ""},
    {"id": 902, "name": "青霉素皮试剂", "url": ""},
    {"id": 765, "name": "※▲※注射用头孢他啶", "url": ""},
    {"id": 764, "name": "※▲注射用头孢曲松钠", "url": ""},
    {"id": 1031, "name": "※注射用头孢哌酮钠舒巴坦钠", "url": ""},
    {"id": 331, "name": "注射用头孢哌酮钠舒巴坦钠", "url": ""},
    {"id": 763, "name": "注射用头孢曲松钠", "url": ""},
    {"id": 536, "name": "注射用苄星青霉素", "url": ""},
    {"id": 698, "name": "注射用青霉素钠", "url": ""},
    {"id": 280, "name": "左氧氟沙星滴眼液", "url": ""},
    {"id": 200, "name": "头孢克肟", "url": ""},
    {"id": 618, "name": "头孢克洛干", "url": ""},
    {"id": 531, "name": "阿奇霉素干", "url": ""},
]

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}


def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()


def fetch_drug_info(url):
    """从网页抓取药品详细信息"""
    try:
        print(f"  正在抓取: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        
        # 尝试从页面中提取药品信息
        text_content = soup.get_text()
        
        # 提取适应症
        if '适应证' in text_content or '适应症' in text_content:
            indications_match = re.search(r'适应[证症][:：](.+?)(?:用法|禁忌|不良|药物相互作用|$)', text_content, re.DOTALL)
            if indications_match:
                drug_info['indications'] = clean_text(indications_match.group(1))
        
        # 提取用法用量
        if '用法与用量' in text_content or '用法用量' in text_content:
            dosage_match = re.search(r'用法与?用量[:：](.+?)(?:禁忌|不良|药物相互作用|药理作用|$)', text_content, re.DOTALL)
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
        
        # 提取FDA妊娠分级
        if 'FDA妊娠分级' in text_content or '妊娠期用药安全分级' in text_content:
            pregnancy_match = re.search(r'(?:FDA妊娠分级|妊娠期用药安全分级)[:：]([A-Z])', text_content)
            if pregnancy_match:
                drug_info['pregnancy_category'] = pregnancy_match.group(1) + "级"
        
        # 提取药理作用
        if '药理作用' in text_content:
            pharmacokinetics_match = re.search(r'药理作用[:：](.+?)(?:(?:适应|用法|禁忌|不良|药物相互作用|注意事项)|$)', text_content, re.DOTALL)
            if pharmacokinetics_match:
                drug_info['pharmacokinetics'] = clean_text(pharmacokinetics_match.group(1))
        
        return drug_info
        
    except Exception as e:
        print(f"  抓取失败: {e}")
        return None


def update_drug_file(drug_id, drug_info):
    """更新药品JSON文件"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        print(f"  ❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        # 更新manual字段
        if 'manual' not in drug_data:
            drug_data['manual'] = {}
        
        # 更新各个字段（只更新非空值）
        updated_fields = []
        for key, value in drug_info.items():
            if value and value.strip():
                drug_data['manual'][key] = value
                drug_data['manual'][f'full_{key}'] = value
                updated_fields.append(key)
        
        # 更新source字段
        drug_data['manual']['source'] = '湖南药事服务网'
        
        # 添加url信息
        if 'url' not in drug_data:
            drug_data['url'] = {}
        drug_data['url']['hnysfww'] = f"https://www.hnysfww.com/goods.php?id={drug_id}"
        drug_data['url']['last_updated'] = time.strftime('%Y-%m-%d')
        
        # 保存更新后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        if updated_fields:
            print(f"  ✅ 已更新字段: {', '.join(updated_fields)}")
        else:
            print(f"  ⚠️  未获取到新字段")
        return True
        
    except Exception as e:
        print(f"  ❌ 更新失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("从湖南药事服务网获取抗生素类药品信息")
    print("=" * 80)
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for i, drug in enumerate(ANTIBIOTIC_DRUGS, 1):
        print(f"\n[{i}/{len(ANTIBIOTIC_DRUGS)}] 处理: {drug['name']} (ID: {drug['id']})")
        
        if not drug['url']:
            print(f"  ⚠️  无湖南药事服务网链接，跳过")
            skip_count += 1
            continue
        
        # 抓取药品信息
        drug_info = fetch_drug_info(drug['url'])
        
        if drug_info:
            # 更新药品文件
            if update_drug_file(drug['id'], drug_info):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        # 添加延迟
        if i < len(ANTIBIOTIC_DRUGS) and ANTIBIOTIC_DRUGS[i]['url']:
            time.sleep(2)
    
    print("\n" + "=" * 80)
    print(f"处理完成: 成功 {success_count}, 跳过 {skip_count}, 失败 {fail_count}")
    print("=" * 80)


if __name__ == '__main__':
    main()
