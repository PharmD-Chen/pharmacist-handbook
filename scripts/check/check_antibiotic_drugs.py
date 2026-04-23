#!/usr/bin/env python3
"""
检查抗生素类药品的状态
"""

import json
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


def check_drug(drug_id):
    """检查单个药品"""
    file_path = DATA_DIR / f"{drug_id}.json"
    
    if not file_path.exists():
        return {'status': 'missing', 'message': '文件不存在'}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        manual = data.get('manual', {})
        source = manual.get('source', '')
        
        # 检查关键字段
        key_fields = ['indications', 'dosage', 'contraindications', 'adverse_reactions']
        empty_fields = []
        
        for field in key_fields:
            value = manual.get(field, '')
            if not value or value.strip() == '':
                empty_fields.append(field)
        
        if empty_fields:
            return {'status': 'incomplete', 'message': f"缺少: {', '.join(empty_fields)}", 'source': source}
        elif source != "湖南药事服务网":
            return {'status': 'wrong_source', 'message': f"来源: {source}"}
        else:
            return {'status': 'complete', 'message': '完整', 'source': source}
            
    except Exception as e:
        return {'status': 'error', 'message': f"错误: {e}"}


print("=" * 100)
print("抗生素类药品状态检查")
print("=" * 100)
print(f"{'ID':<6} {'药品名称':<35} {'状态':<15} {'来源':<20} {'备注'}")
print("-" * 100)

complete_count = 0
incomplete_count = 0

for drug in ANTIBIOTIC_DRUGS:
    result = check_drug(drug['id'])
    status = result['status']
    
    if status == 'complete':
        status_icon = '✅'
        complete_count += 1
    elif status == 'incomplete':
        status_icon = '⚠️'
        incomplete_count += 1
    elif status == 'wrong_source':
        status_icon = '⚠️'
        incomplete_count += 1
    else:
        status_icon = '❌'
        incomplete_count += 1
    
    source = result.get('source', '无')
    message = result['message']
    
    print(f"{drug['id']:<6} {drug['name']:<35} {status_icon} {status:<12} {source:<20} {message}")

print("=" * 100)
print(f"总计: {len(ANTIBIOTIC_DRUGS)} 个 | ✅ 完整: {complete_count} 个 | ⚠️ 需处理: {incomplete_count} 个")
print("=" * 100)
