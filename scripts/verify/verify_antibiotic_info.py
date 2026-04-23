#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证第352行之前抗生素药品信息的完整性和来源
"""

import json
from pathlib import Path

DATA_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs")

# 第352行之前有网址的抗生素药品
ANTIBIOTIC_DRUGS = [
    {"id": 86, "name": "甲硝唑氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2328"},
    {"id": 77, "name": "盐酸克林霉素", "url": "https://www.hnysfww.com/goods.php?id=2038"},
    {"id": 224, "name": "硫酸阿米卡星", "url": "https://www.hnysfww.com/goods.php?id=1980"},
    {"id": 398, "name": "盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 281, "name": "左氧氟沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 439, "name": "克林霉素磷酸酯", "url": "https://www.hnysfww.com/goods.php?id=2039"},
    {"id": 656, "name": "注射用头孢曲松钠/氯化钠", "url": "https://www.hnysfww.com/goods.php?id=1907"},
    {"id": 658, "name": "注射用头孢地嗪钠/5%葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=1916"},
    {"id": 757, "name": "※▲盐酸莫西沙星氯化钠", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 804, "name": "利奈唑胺葡萄糖", "url": "https://www.hnysfww.com/goods.php?id=2115"},
    {"id": 916, "name": "※硫酸庆大霉素", "url": "https://www.hnysfww.com/goods.php?id=1977"},
    {"id": 282, "name": "左氧氟沙星片", "url": "https://www.hnysfww.com/goods.php?id=2089"},
    {"id": 495, "name": "盐酸莫西沙星片", "url": "https://www.hnysfww.com/goods.php?id=2092"},
    {"id": 677, "name": "阿奇霉素片", "url": "https://www.hnysfww.com/goods.php?id=2016"},
    {"id": 970, "name": "甲硝唑片", "url": "https://www.hnysfww.com/goods.php?id=2328"},
]

def check_drug_info(drug_id, drug_name, url):
    """检查单个药品的信息"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return {"status": "missing", "message": "文件不存在"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        
        # 检查关键字段
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions']
        empty_fields = []
        field_lengths = {}
        
        for field in key_fields:
            value = manual.get(field, '')
            if not value or value.strip() == '':
                empty_fields.append(field)
            else:
                field_lengths[field] = len(value)
        
        # 检查来源
        source = manual.get('source', '')
        file_url = data.get('url', {}).get('hnysfww', '')
        
        # 验证网址是否匹配
        url_match = (file_url == url)
        
        if empty_fields:
            return {
                "status": "incomplete",
                "message": f"缺少: {', '.join(empty_fields)}",
                "source": source,
                "url_match": url_match,
                "file_url": file_url,
                "expected_url": url
            }
        elif source != "湖南药事服务网":
            return {
                "status": "wrong_source",
                "message": f"来源: {source}",
                "source": source,
                "url_match": url_match,
                "file_url": file_url,
                "expected_url": url
            }
        elif not url_match:
            return {
                "status": "url_mismatch",
                "message": "网址不匹配",
                "source": source,
                "url_match": url_match,
                "file_url": file_url,
                "expected_url": url
            }
        else:
            return {
                "status": "verified",
                "message": "完整且来源正确",
                "source": source,
                "url_match": url_match,
                "file_url": file_url,
                "expected_url": url,
                "field_lengths": field_lengths
            }
        
    except Exception as e:
        return {"status": "error", "message": f"错误: {e}"}

def main():
    """主函数"""
    print("=" * 120)
    print("验证第352行之前抗生素药品信息 - 完整性和来源检查")
    print("=" * 120)
    print(f"{'ID':<6} {'药品名称':<28} {'状态':<12} {'来源':<15} {'网址匹配':<8} {'备注'}")
    print("-" * 120)
    
    verified_count = 0
    issue_count = 0
    
    for drug in ANTIBIOTIC_DRUGS:
        result = check_drug_info(drug['id'], drug['name'], drug['url'])
        
        status_icon = "❓"
        if result['status'] == 'verified':
            status_icon = "✅"
            verified_count += 1
        elif result['status'] in ['incomplete', 'wrong_source', 'url_mismatch', 'error']:
            status_icon = "⚠️"
            issue_count += 1
        
        url_match_str = "是" if result.get('url_match') else "否"
        
        print(f"{drug['id']:<6} {drug['name']:<28} {status_icon} {result['status']:<10} {result.get('source', 'N/A'):<15} {url_match_str:<8} {result['message']}")
        
        # 如果有问题，显示详细信息
        if result['status'] == 'url_mismatch':
            print(f"       文件中的网址: {result.get('file_url', 'N/A')}")
            print(f"       期望的网址:   {result.get('expected_url', 'N/A')}")
    
    print("=" * 120)
    print(f"验证完成: ✅ 验证通过 {verified_count} 个 | ⚠️ 有问题 {issue_count} 个")
    print("=" * 120)
    
    if issue_count > 0:
        print("\n⚠️ 警告：部分药品存在问题，需要检查！")
    else:
        print("\n✅ 所有第352行之前的抗生素药品信息完整且来源正确！")

if __name__ == "__main__":
    main()
