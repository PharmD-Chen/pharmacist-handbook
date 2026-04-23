#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新药品手册信息
从湖南药事服务网获取详细信息并生成精简版
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
        
        # 查找包含药品信息的table
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
    # 方法1：先尝试匹配"功能主治"（中成药常用）
    match = re.search(r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        return clean_text(match.group(1))
    
    # 方法2：再尝试匹配"适应证"（西药常用）
    match = re.search(r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        return clean_text(match.group(1))
    
    return ""

def extract_dosage(text, dosage_form):
    """提取用法用量，根据剂型筛选"""
    match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        full_dosage = clean_text(match.group(1))
        
        # 根据剂型精简
        if '注射' in dosage_form or '粉针' in dosage_form:
            # 注射剂型：保留注射相关内容
            simplified = re.sub(r'口服.*?(?:；|$)', '', full_dosage)
        elif '片' in dosage_form or '胶囊' in dosage_form or '颗粒' in dosage_form:
            # 口服剂型：保留口服相关内容
            simplified = re.sub(r'(?:静脉|肌内|皮下)注射.*?(?:；|$)', '', full_dosage)
        else:
            simplified = full_dosage
        
        # 精简到200字以内
        if len(simplified) > 200:
            simplified = simplified[:197] + "..."
        
        return simplified, full_dosage
    
    return "", ""

def extract_contraindications(text):
    """提取禁忌症"""
    match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        full = clean_text(match.group(1))
        # 精简版
        simplified = re.sub(r'[。；]', '；', full)
        if len(simplified) > 200:
            simplified = simplified[:197] + "..."
        return simplified, full
    return "", ""

def extract_adverse_reactions(text):
    """提取不良反应"""
    match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        full = clean_text(match.group(1))
        # 精简版：保留反应名称和分级
        simplified = full
        if len(simplified) > 200:
            simplified = simplified[:197] + "..."
        return simplified, full
    return "", ""

def extract_interactions(text):
    """提取药物相互作用"""
    match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        full = clean_text(match.group(1))
        if len(full) < 50:
            return "暂未发现有临床意义的药物相互作用", full
        return full[:200] if len(full) > 200 else full, full
    return "暂未发现有临床意义的药物相互作用", ""

def extract_precautions(text):
    """提取注意事项"""
    match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
    if match:
        full = clean_text(match.group(1))
        # 精简版
        simplified = full
        if len(simplified) > 200:
            simplified = simplified[:197] + "..."
        return simplified, full
    return "", ""

def extract_pharmacokinetics(text):
    """提取药代动力学参数"""
    # 从药理作用/成份中提取药动学参数
    match = re.search(r'(?:成份/药理作用|药理作用)(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        full = clean_text(match.group(1))
        
        # 提取关键参数
        params = []
        
        # 达峰时间
        tmax_match = re.search(r'(\d+(?:\.\d+)?)\s*小时?达峰', full)
        if tmax_match:
            params.append(f"Tmax: {tmax_match.group(1)}h")
        
        # 半衰期
        t12_match = re.search(r'半衰期.*?([\d\.]+)\s*小时', full)
        if t12_match:
            params.append(f"t1/2: {t12_match.group(1)}h")
        
        # 生物利用度
        bio_match = re.search(r'生物利用度.*?([\d\.]+)%', full)
        if bio_match:
            params.append(f"F: {bio_match.group(1)}%")
        
        # 蛋白结合率
        protein_match = re.search(r'蛋白结合率.*?([\d\.]+)%', full)
        if protein_match:
            params.append(f"Pb: {protein_match.group(1)}%")
        
        simplified = "；".join(params) if params else full[:200]
        return simplified, full
    
    return "", ""

def extract_pregnancy_category(text):
    """提取妊娠分级"""
    match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
    if match:
        return match.group(1)
    return ""

def update_drug_manual(drug_id, url):
    """更新药品手册信息"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    
    if not drug_file.exists():
        return False, "文件不存在"
    
    with open(drug_file, 'r', encoding='utf-8') as f:
        drug_data = json.load(f)
    
    # 检查是否已有完整手册信息
    manual = drug_data.get('manual', {})
    if manual.get('indications') and manual.get('dosage'):
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
    """主函数"""
    # 从清单文件中提取有网址的药品
    # 这里需要手动指定要处理的药品列表
    
    # 示例：处理几个重点药品
    drugs_to_update = [
        (372, "https://www.hnysfww.com/goods.php?id=7949", "灭菌注射用水"),
        (384, "https://www.hnysfww.com/goods.php?id=1248", "糠酸莫米松"),
        (441, "https://www.hnysfww.com/goods.php?id=355", "尼莫地平"),
    ]
    
    print("=" * 80)
    print("批量更新药品手册信息")
    print("=" * 80)
    
    updated = []
    failed = []
    skipped = []
    
    for drug_id, url, drug_name in drugs_to_update:
        print(f"\n处理: {drug_name} (ID: {drug_id})")
        success, message = update_drug_manual(drug_id, url)
        
        if success:
            updated.append({'id': drug_id, 'name': drug_name})
            print(f"✓ 更新成功")
        elif "已有完整信息" in message:
            skipped.append({'id': drug_id, 'name': drug_name, 'reason': message})
            print(f"⊘ 跳过: {message}")
        else:
            failed.append({'id': drug_id, 'name': drug_name, 'reason': message})
            print(f"✗ 失败: {message}")
        
        time.sleep(1)  # 避免请求过快
    
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

if __name__ == '__main__':
    main()
