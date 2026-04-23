#!/usr/bin/env python3
"""
重新获取来源非湖南药事服务网的12个药品信息
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

# 12个来源不正确的药品
DRUGS_TO_UPDATE = [
    {"id": 113, "name": "5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3185"},
    {"id": 114, "name": "50%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=3185"},
    {"id": 794, "name": "※▲丁甘交联玻璃酸钠", "url": "https://www.hnysfww.com/goods.php?id=13625"},
    {"id": 35, "name": "盐酸利多卡因", "url": "https://www.hnysfww.com/goods.php?id=2864"},
    {"id": 432, "name": "盐酸曲马多", "url": "https://www.hnysfww.com/goods.php?id=1029"},
    {"id": 130, "name": "盐酸氨溴索", "url": "https://www.hnysfww.com/goods.php?id=1586"},
    {"id": 631, "name": "盐酸精氨酸", "url": "https://www.hnysfww.com/goods.php?id=3117"},
    {"id": 1029, "name": "硫酸镁", "url": "https://www.hnysfww.com/goods.php?id=1499"},
    {"id": 262, "name": "硫酸阿托品", "url": "https://www.hnysfww.com/goods.php?id=511"},
    {"id": 983, "name": "碳酸氢钠", "url": "https://www.hnysfww.com/goods.php?id=3231"},
    {"id": 509, "name": "维生素C", "url": "https://www.hnysfww.com/goods.php?id=3076"},
    {"id": 137, "name": "重酒石酸去甲肾上腺素", "url": "https://www.hnysfww.com/goods.php?id=142"},
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
        
        # 提取FDA妊娠分级
        if 'FDA妊娠分级' in text_content:
            pregnancy_match = re.search(r'FDA妊娠分级[:：](.+?)(?:(?:适应|用法|禁忌|不良|药物相互作用|注意事项|药理作用)|$)', text_content, re.DOTALL)
            if pregnancy_match:
                drug_info['pregnancy_category'] = clean_text(pregnancy_match.group(1))
        
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
            if value and value.strip():  # 只更新非空值
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
    print("重新获取12个来源不正确的药品信息")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    
    for i, drug in enumerate(DRUGS_TO_UPDATE, 1):
        print(f"\n[{i}/12] 处理: {drug['name']} (ID: {drug['id']})")
        
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
        
        # 添加延迟，避免请求过快
        if i < len(DRUGS_TO_UPDATE):
            time.sleep(2)
    
    print("\n" + "=" * 80)
    print(f"处理完成: 成功 {success_count}, 失败 {fail_count}")
    print("=" * 80)


if __name__ == '__main__':
    main()
