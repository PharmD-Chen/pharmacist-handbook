#!/usr/bin/env python3
"""
从湖南药事服务网获取盐酸肾上腺素和葡萄糖酸钙注射液的详细信息
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

# 需要更新的两个药品
DRUGS_TO_UPDATE = [
    {"id": 753, "name": "盐酸肾上腺素", "url": "https://www.hnysfww.com/goods.php?id=141"},
    {"id": 391, "name": "葡萄糖酸钙", "url": "https://www.hnysfww.com/goods.php?id=3199"},
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
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()


def extract_section_text(soup, section_title):
    """提取特定章节的文本"""
    # 查找包含章节标题的元素
    for elem in soup.find_all(['div', 'p', 'strong', 'b', 'h3', 'h4']):
        text = elem.get_text().strip()
        if section_title in text:
            # 找到标题后，获取其后的内容
            content = []
            next_elem = elem.find_next_sibling()
            while next_elem:
                if next_elem.name in ['div', 'p']:
                    content_text = clean_text(next_elem.get_text())
                    if content_text and not any(title in content_text for title in ['适应证', '用法与用量', '禁忌', '不良反应', '药物相互作用', '注意事项', '药理作用']):
                        content.append(content_text)
                    else:
                        break
                next_elem = next_elem.find_next_sibling()
            
            if content:
                return '\n'.join(content)
    
    return ""


def fetch_drug_info(url):
    """从网页抓取药品详细信息"""
    try:
        print(f"正在抓取: {url}")
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
        
        # 提取FDA妊娠分级
        if 'FDA妊娠分级' in text_content:
            pregnancy_match = re.search(r'FDA妊娠分级[:：](.+?)(?:(?:适应|用法|禁忌|不良|药物相互作用|注意事项|药理作用)|$)', text_content, re.DOTALL)
            if pregnancy_match:
                drug_info['pregnancy_category'] = clean_text(pregnancy_match.group(1))
        
        # 提取药理作用（用于药代动力学）
        if '药理作用' in text_content:
            pharmacokinetics_match = re.search(r'药理作用[:：](.+?)(?:(?:适应|用法|禁忌|不良|药物相互作用|注意事项)|$)', text_content, re.DOTALL)
            if pharmacokinetics_match:
                drug_info['pharmacokinetics'] = clean_text(pharmacokinetics_match.group(1))
        
        return drug_info
        
    except Exception as e:
        print(f"抓取失败: {url}, 错误: {e}")
        return None


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
                # 同时更新full_字段
                drug_data['manual'][f'full_{key}'] = value
        
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
        
        print(f"已更新: {drug_data.get('name', drug_id)}")
        return True
        
    except Exception as e:
        print(f"更新失败 {drug_id}: {e}")
        return False


def main():
    """主函数"""
    print("开始从湖南药事服务网获取药品信息...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for drug in DRUGS_TO_UPDATE:
        print(f"\n处理: {drug['name']} (ID: {drug['id']})")
        print(f"URL: {drug['url']}")
        
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
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"处理完成: 成功 {success_count}, 失败 {fail_count}")


if __name__ == '__main__':
    main()
