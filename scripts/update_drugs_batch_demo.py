#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新药品手册信息 - 演示版本（处理前10个药品）
"""

import json
import re
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import time

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    text = re.sub(r' +', ' ', text)
    return text.strip()

def fetch_drug_info(url):
    """从湖南药事服务网获取药品信息"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        if tables:
            text = tables[0].get_text()
            return text
        return None
    except Exception as e:
        print(f"获取网页失败: {e}")
        return None

def extract_indications(text):
    """提取适应症/功能主治"""
    patterns = [
        r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)',
        r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return clean_text(match.group(1))
    return ""

def extract_dosage(text, dosage_form):
    """提取用法用量"""
    match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if not match:
        return "", ""
    
    full = clean_text(match.group(1))
    
    # 精简
    if len(full) > 150:
        key_info = re.findall(r'(?:成人|儿童|老年|一次|一日|每次|每日)[^。；]*', full)
        if key_info:
            simplified = '；'.join(key_info[:3])
        else:
            simplified = full[:147] + "..."
    else:
        simplified = full
    
    return simplified, full

def extract_contraindications(text):
    """提取禁忌症"""
    match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if not match:
        return "", ""
    
    full = clean_text(match.group(1))
    
    if len(full) > 150:
        key_points = re.findall(r'[^。；]*(?:禁用|过敏者|慎用)[^。；]*', full)
        if key_points:
            simplified = '；'.join(key_points[:3])
        else:
            simplified = full[:147] + "..."
    else:
        simplified = full
    
    return simplified, full

def extract_adverse_reactions(text):
    """提取不良反应"""
    match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if not match:
        return "", ""
    
    full = clean_text(match.group(1))
    
    if len(full) > 150:
        key_reactions = re.findall(r'(?:常见|偶见|罕见)[^。；]*', full)
        if key_reactions:
            simplified = '；'.join(key_reactions[:3])
        else:
            simplified = full[:147] + "..."
    else:
        simplified = full
    
    return simplified, full

def extract_interactions(text):
    """提取药物相互作用"""
    match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
    if not match:
        return "暂未发现有临床意义的药物相互作用", ""
    
    full = clean_text(match.group(1))
    
    if len(full) < 20:
        return "暂未发现有临床意义的药物相互作用", full
    
    if len(full) > 150:
        key_interactions = re.findall(r'[^。；]*(?:合用|联用|与)[^。；]*(?:增加|减少|增强|减弱)[^。；]*', full)
        if key_interactions:
            simplified = '；'.join(key_interactions[:2])
        else:
            simplified = full[:147] + "..."
    else:
        simplified = full
    
    return simplified, full

def extract_precautions(text):
    """提取注意事项"""
    match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
    if not match:
        return "", ""
    
    full = clean_text(match.group(1))
    
    if len(full) > 150:
        key_points = re.findall(r'[^。；]*(?:慎用|监测|定期检查|注意)[^。；]*', full)
        if key_points:
            simplified = '；'.join(key_points[:3])
        else:
            simplified = full[:147] + "..."
    else:
        simplified = full
    
    return simplified, full

def extract_pharmacokinetics(text):
    """提取药代动力学参数"""
    patterns = [
        r'药代动力学(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)',
        r'药理作用(.+?)(?:药代动力学|用法用量|不良反应|禁忌|注意事项|贮藏|$)',
    ]
    
    full = ""
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            full = clean_text(match.group(1))
            break
    
    if not full:
        return "", ""
    
    # 提取关键参数
    params = []
    
    tmax_match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', full)
    if tmax_match:
        params.append(f"Tmax: {tmax_match.group(1)}h")
    
    t12_match = re.search(r'半衰期.*?([\d\.]+)\s*小时', full)
    if t12_match:
        params.append(f"t1/2: {t12_match.group(1)}h")
    
    bio_match = re.search(r'生物利用度.*?([\d\.]+)%', full)
    if bio_match:
        params.append(f"F: {bio_match.group(1)}%")
    
    protein_match = re.search(r'蛋白结合率.*?([\d\.]+)%', full)
    if protein_match:
        params.append(f"Pb: {protein_match.group(1)}%")
    
    simplified = "；".join(params) if params else full[:150]
    
    return simplified, full

def extract_pregnancy_category(text):
    """提取妊娠分级"""
    match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
    if match:
        return match.group(1)
    return ""

def update_drug_manual(drug_id, url, drug_name):
    """更新药品手册信息"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    
    if not drug_file.exists():
        return False, "文件不存在"
    
    with open(drug_file, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    # 检查是否已有完整手册信息
    manual = drug_data.get('manual', {})
    if manual.get('indications') and len(manual.get('indications', '')) > 10:
        return False, "已有完整信息"
    
    # 获取网页内容
    text = fetch_drug_info(url)
    if not text:
        return False, "获取网页失败"
    
    # 提取各字段
    dosage_form = drug_data.get('dosage_form', '')
    
    indications = extract_indications(text)
    dosage_simplified, dosage_full = extract_dosage(text, dosage_form)
    contraindications_simplified, contraindications_full = extract_contraindications(text)
    adverse_reactions_simplified, adverse_reactions_full = extract_adverse_reactions(text)
    interactions_simplified, interactions_full = extract_interactions(text)
    precautions_simplified, precautions_full = extract_precautions(text)
    pharmacokinetics_simplified, pharmacokinetics_full = extract_pharmacokinetics(text)
    pregnancy_category = extract_pregnancy_category(text)
    
    # 更新手册信息
    drug_data['manual'] = {
        'indications': indications[:300] if len(indications) > 300 else indications,
        'full_indications': indications,
        'dosage': dosage_simplified,
        'full_dosage': dosage_full,
        'contraindications': contraindications_simplified,
        'full_contraindications': contraindications_full,
        'adverse_reactions': adverse_reactions_simplified,
        'full_adverse_reactions': adverse_reactions_full,
        'interactions': interactions_simplified,
        'full_interactions': interactions_full,
        'precautions': precautions_simplified,
        'full_precautions': precautions_full,
        'pharmacokinetics': pharmacokinetics_simplified,
        'full_pharmacokinetics': pharmacokinetics_full,
        'pregnancy_category': pregnancy_category,
        'source': '湖南药事服务网'
    }
    
    # 更新URL
    drug_data['url'] = {
        'hnysfww': url,
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    }
    
    # 保存文件
    with open(drug_file, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)
    
    return True, "更新成功"

def main():
    """主函数 - 处理前10个药品作为演示"""
    
    drugs_to_update = [
        (372, "https://www.hnysfww.com/goods.php?id=7949", "灭菌注射用水"),
        (384, "https://www.hnysfww.com/goods.php?id=1248", "糠酸莫米松"),
        (441, "https://www.hnysfww.com/goods.php?id=355", "尼莫地平"),
        (476, "https://www.hnysfww.com/goods.php?id=1604", "硫酸沙丁胺醇吸入"),
        (478, "https://www.hnysfww.com/goods.php?id=1765", "盐酸坦索罗辛缓释"),
        (514, "https://www.hnysfww.com/goods.php?id=2995", "布林佐胺"),
        (515, "https://www.hnysfww.com/goods.php?id=2708", "布洛芬缓释"),
        (522, "https://www.hnysfww.com/goods.php?id=693", "注射用苯巴比妥钠"),
        (525, "https://www.hnysfww.com/goods.php?id=13214", "未确瑞基奥仑赛"),
        (530, "https://www.hnysfww.com/goods.php?id=415", "雷贝拉唑钠"),
    ]
    
    print("=" * 80)
    print("批量更新药品手册信息（演示版本 - 前10个药品）")
    print("=" * 80)
    print(f"共 {len(drugs_to_update)} 个药品需要处理\n")
    
    updated = []
    skipped = []
    failed = []
    
    for i, (drug_id, url, drug_name) in enumerate(drugs_to_update, 1):
        print(f"[{i}/{len(drugs_to_update)}] 处理: {drug_name} (ID: {drug_id})")
        success, message = update_drug_manual(drug_id, url, drug_name)
        
        if success:
            updated.append({'id': drug_id, 'name': drug_name})
            print(f"  ✓ 更新成功")
        elif "已有完整信息" in message:
            skipped.append({'id': drug_id, 'name': drug_name})
            print(f"  ⊘ 跳过（已有信息）")
        else:
            failed.append({'id': drug_id, 'name': drug_name, 'reason': message})
            print(f"  ✗ 失败: {message}")
        
        time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print("更新统计")
    print("=" * 80)
    print(f"成功更新: {len(updated)} 个")
    print(f"跳过: {len(skipped)} 个")
    print(f"失败: {len(failed)} 个")
    
    if updated:
        print("\n已更新的药品:")
        for item in updated:
            print(f"  - ID {item['id']}: {item['name']}")
    
    if failed:
        print("\n失败的药品:")
        for item in failed:
            print(f"  - ID {item['id']}: {item['name']} - {item['reason']}")
    
    print("\n" + "=" * 80)
    print("提示：如需处理更多药品，请修改脚本中的 drugs_to_update 列表")
    print("=" * 80)

if __name__ == '__main__':
    main()
