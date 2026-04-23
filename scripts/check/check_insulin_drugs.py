#!/usr/bin/env python3
"""
检查胰岛素类药品的状态
"""

import json
from pathlib import Path

# 胰岛素类药品列表
INSULIN_DRUGS = [
    {"id": 768, "name": "※▲德谷胰岛素利拉鲁肽", "url": "https://www.hnysfww.com/goods.php?id=13362"},
    {"id": 263, "name": "人胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1318"},
    {"id": 830, "name": "地特胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1315"},
    {"id": 107, "name": "德谷门冬双胰岛素", "url": "https://www.hnysfww.com/goods.php?id=12964"},
    {"id": 681, "name": "甘精胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1314"},
    {"id": 610, "name": "赖脯胰岛素", "url": "https://www.hnysfww.com/goods.php?id=13390"},
    {"id": 946, "name": "门冬胰岛素", "url": "https://www.hnysfww.com/goods.php?id=1312"},
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
print("胰岛素类药品状态检查")
print("=" * 100)
print(f"{'ID':<6} {'药品名称':<25} {'状态':<15} {'来源':<20} {'备注'}")
print("-" * 100)

complete_count = 0
incomplete_count = 0

for drug in INSULIN_DRUGS:
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
    
    print(f"{drug['id']:<6} {drug['name']:<25} {status_icon} {status:<12} {source:<20} {message}")

print("=" * 100)
print(f"总计: {len(INSULIN_DRUGS)} 个 | ✅ 完整: {complete_count} 个 | ⚠️ 需处理: {incomplete_count} 个")
print("=" * 100)
