#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从湖南药事服务网提取药品信息
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import pandas as pd

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def extract_drug_info(url):
    """从湖南药事服务网提取药品信息"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if not tables:
            return None
        
        text = tables[0].get_text()
        
        # 提取药品名称
        title_match = re.search(r'【药品名称】\s*([^【】]+)', text)
        drug_name = clean_text(title_match.group(1)) if title_match else ""
        
        # 提取适应症/功能主治
        indications = ""
        match = re.search(r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            indications = clean_text(match.group(1))
        else:
            match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
            if match:
                indications = clean_text(match.group(1))
        
        # 提取药理作用/成份
        pharmacokinetics = ""
        match = re.search(r'成份/药理作用(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            pharmacokinetics = clean_text(match.group(1))
        else:
            match = re.search(r'药理作用(.+?)(?:用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
            if match:
                pharmacokinetics = clean_text(match.group(1))
        
        # 提取用法用量
        dosage = ""
        match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            dosage = clean_text(match.group(1))
        
        # 提取禁忌
        contraindications = ""
        match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            contraindications = clean_text(match.group(1))
        
        # 提取不良反应
        adverse_reactions = ""
        match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            adverse_reactions = clean_text(match.group(1))
        
        # 提取药物相互作用
        interactions = ""
        match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
        if match:
            interactions = clean_text(match.group(1))
        
        # 提取注意事项
        precautions = ""
        match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
        if match:
            precautions = clean_text(match.group(1))
        
        # 提取妊娠分级
        pregnancy_category = ""
        match = re.search(r'妊娠期用药安全分级\s*([A-Z]\s*级?)', text)
        if match:
            pregnancy_category = match.group(1)
        else:
            match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
            if match:
                pregnancy_category = match.group(1)
        
        return {
            'drug_name': drug_name,
            'indications': indications,
            'pharmacokinetics': pharmacokinetics,
            'dosage': dosage,
            'contraindications': contraindications,
            'adverse_reactions': adverse_reactions,
            'interactions': interactions,
            'precautions': precautions,
            'pregnancy_category': pregnancy_category,
            'source_text': text[:500]  # 前500字符用于调试
        }
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    # 药品列表
    drugs = [
        {"序号": 1, "通用名": "盐酸拉贝洛尔氯化钠注射液", "url": "https://www.hnysfww.com/goods.php?id=212"},
        {"序号": 2, "通用名": "阿利沙坦酯吲达帕胺缓释片", "url": "https://www.hnysfww.com/goods.php?id=13919"},
        {"序号": 3, "通用名": "阿地溴铵吸入粉雾剂", "url": "https://www.hnysfww.com/goods.php?id=12944"},
        {"序号": 4, "通用名": "吡仑帕奈口服混悬液", "url": "https://www.hnysfww.com/goods.php?id=863"},
        {"序号": 5, "通用名": "复方比那甫西颗粒", "url": "https://www.hnysfww.com/goods.php?id=13880"},
        {"序号": 6, "通用名": "参郁宁神片", "url": "https://www.hnysfww.com/goods.php?id=13634"},
        {"序号": 7, "通用名": "注射用替奈普酶", "url": "https://www.hnysfww.com/goods.php?id=12328"},
        {"序号": 8, "通用名": "注射用美罗培南氯化钠注射液", "url": "https://www.hnysfww.com/goods.php?id=1961"},
        {"序号": 9, "通用名": "苹果酸奈诺沙星氯化钠注射液", "url": "https://www.hnysfww.com/goods.php?id=2085"},
        {"序号": 10, "通用名": "注射用头孢吡肟氯化钠注射液", "url": "https://www.hnysfww.com/goods.php?id=1925"},
        {"序号": 12, "通用名": "玄七健骨片", "url": "https://www.hnysfww.com/goods.php?id=13374"},
        {"序号": 15, "通用名": "替尔泊肽注射液", "url": "https://www.hnysfww.com/goods.php?id=13628"},
        {"序号": 17, "通用名": "依柯胰岛素注射液", "url": "https://www.hnysfww.com/goods.php?id=13785"},
        {"序号": 18, "通用名": "金银花口服液", "url": "https://www.hnysfww.com/goods.php?id=9187"},
        {"序号": 19, "通用名": "肠内营养乳剂（SP）", "url": "https://www.hnysfww.com/goods.php?id=13569"},
        {"序号": 20, "通用名": "益气清肺颗粒", "url": "https://www.hnysfww.com/goods.php?id=13866"},
        {"序号": 22, "通用名": "地塞米松玻璃体内植入剂", "url": "https://www.hnysfww.com/goods.php?id=1240"},
        {"序号": 23, "通用名": "环孢素滴眼液（Ⅱ）", "url": "https://www.hnysfww.com/goods.php?id=1805"},
        {"序号": 24, "通用名": "蛭蛇通络胶囊", "url": "https://www.hnysfww.com/goods.php?id=9960"},
        {"序号": 30, "通用名": "利培酮口服溶液", "url": "https://www.hnysfww.com/goods.php?id=780"},
        {"序号": 31, "通用名": "氨磺必利口崩片", "url": "https://www.hnysfww.com/goods.php?id=772"},
    ]
    
    print("开始提取药品信息...")
    print("=" * 80)
    
    results = []
    for i, drug in enumerate(drugs, 1):
        print(f"\n[{i}/{len(drugs)}] 正在提取: {drug['通用名']}")
        print(f"URL: {drug['url']}")
        
        info = extract_drug_info(drug['url'])
        if info:
            print(f"✓ 成功提取: {info['drug_name'][:30]}...")
            print(f"  - 适应症: {'有' if info['indications'] else '无'} ({len(info['indications'])}字)")
            print(f"  - 用法用量: {'有' if info['dosage'] else '无'} ({len(info['dosage'])}字)")
            print(f"  - 禁忌: {'有' if info['contraindications'] else '无'} ({len(info['contraindications'])}字)")
            
            results.append({
                '序号': drug['序号'],
                '通用名': drug['通用名'],
                'url': drug['url'],
                '提取成功': True,
                'data': info
            })
        else:
            print(f"✗ 提取失败")
            results.append({
                '序号': drug['序号'],
                '通用名': drug['通用名'],
                'url': drug['url'],
                '提取成功': False,
                'data': None
            })
        
        # 礼貌性延迟
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print("提取完成!")
    
    # 保存结果
    success_count = sum(1 for r in results if r['提取成功'])
    print(f"成功: {success_count}/{len(drugs)}")
    
    # 保存到JSON文件
    output_file = '原始材料/新药品信息提取结果.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到: {output_file}")
    
    return results

if __name__ == '__main__':
    main()
