#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新所有有网址的药品手册信息
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
    # 去除多余的空格
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
        
        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if tables:
            text = tables[0].get_text()
            return text
        return None
    except Exception as e:
        print(f"获取网页失败: {e}")
        return None

def extract_field(text, pattern_list):
    """通用字段提取函数"""
    for pattern in pattern_list:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return clean_text(match.group(1))
    return ""

def extract_indications(text):
    """提取适应症/功能主治"""
    patterns = [
        r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)',
        r'适应证(.+?)(?:药理作用|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
    ]
    return extract_field(text, patterns)

def extract_pharmacology(text):
    """提取药理作用/成份"""
    patterns = [
        r'成份/药理作用(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)',
        r'药理作用(.+?)(?:药代动力学|用法用量|不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
    ]
    return extract_field(text, patterns)

def extract_dosage(text, dosage_form):
    """提取用法用量，根据剂型筛选"""
    patterns = [
        r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)',
    ]
    full_dosage = extract_field(text, patterns)
    
    if not full_dosage:
        return "", ""
    
    # 根据剂型精简
    if '注射' in dosage_form or '粉针' in dosage_form:
        # 注射剂型：保留注射相关内容，去除口服
        simplified = re.sub(r'口服.*?(?:；|$)', '', full_dosage)
    elif '片' in dosage_form or '胶囊' in dosage_form or '颗粒' in dosage_form or '丸' in dosage_form:
        # 口服剂型：保留口服相关内容，去除注射
        simplified = re.sub(r'(?:静脉|肌内|皮下)注射.*?(?:；|$)', '', full_dosage)
    elif '软膏' in dosage_form or '乳膏' in dosage_form or '凝胶' in dosage_form:
        # 外用剂型：保留外用相关内容
        simplified = re.sub(r'(?:口服|注射).*?(?:；|$)', '', full_dosage)
    else:
        simplified = full_dosage
    
    # 精简到150字以内
    if len(simplified) > 150:
        # 尝试提取关键信息
        key_info = re.findall(r'(?:成人|儿童|老年|一次|一日|每次|每日)[^。；]*', simplified)
        if key_info:
            simplified = '；'.join(key_info[:3])
        else:
            simplified = simplified[:147] + "..."
    
    return simplified, full_dosage

def extract_contraindications(text):
    """提取禁忌症"""
    patterns = [
        r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)',
    ]
    full = extract_field(text, patterns)
    
    if not full:
        return "", ""
    
    # 精简版：提取关键禁忌
    # 保留"禁用"、"过敏者"等关键词
    simplified = full
    if len(simplified) > 150:
        # 提取禁用相关的内容
        key_points = re.findall(r'[^。；]*(?:禁用|过敏者|慎用)[^。；]*', simplified)
        if key_points:
            simplified = '；'.join(key_points[:3])
        else:
            simplified = simplified[:147] + "..."
    
    return simplified, full

def extract_adverse_reactions(text):
    """提取不良反应"""
    patterns = [
        r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)',
    ]
    full = extract_field(text, patterns)
    
    if not full:
        return "", ""
    
    # 精简版：保留反应名称
    simplified = full
    if len(simplified) > 150:
        # 提取常见不良反应
        key_reactions = re.findall(r'(?:常见|偶见|罕见)[^。；]*', simplified)
        if key_reactions:
            simplified = '；'.join(key_reactions[:3])
        else:
            simplified = simplified[:147] + "..."
    
    return simplified, full

def extract_interactions(text):
    """提取药物相互作用"""
    patterns = [
        r'药物相互作用(.+?)(?:注意事项|贮藏|$)',
    ]
    full = extract_field(text, patterns)
    
    if not full or len(full) < 20:
        return "暂未发现有临床意义的药物相互作用", full
    
    # 精简版
    simplified = full
    if len(simplified) > 150:
        # 提取关键相互作用
        key_interactions = re.findall(r'[^。；]*(?:合用|联用|与)[^。；]*(?:增加|减少|增强|减弱)[^。；]*', simplified)
        if key_interactions:
            simplified = '；'.join(key_interactions[:2])
        else:
            simplified = simplified[:147] + "..."
    
    return simplified, full

def extract_precautions(text):
    """提取注意事项"""
    patterns = [
        r'注意事项(.+?)(?:贮藏|$)',
    ]
    full = extract_field(text, patterns)
    
    if not full:
        return "", ""
    
    # 精简版
    simplified = full
    if len(simplified) > 150:
        # 提取关键注意事项
        key_points = re.findall(r'[^。；]*(?:慎用|监测|定期检查|注意)[^。；]*', simplified)
        if key_points:
            simplified = '；'.join(key_points[:3])
        else:
            simplified = simplified[:147] + "..."
    
    return simplified, full

def extract_pharmacokinetics(text):
    """提取药代动力学参数"""
    patterns = [
        r'药代动力学(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)',
    ]
    full = extract_field(text, patterns)
    
    if not full:
        # 尝试从药理作用中提取
        full = extract_pharmacology(text)
    
    if not full:
        return "", ""
    
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
    
    # 代谢和排泄
    metabolism_match = re.search(r'(经[^。]*?代谢)', full)
    if metabolism_match:
        params.append(metabolism_match.group(1))
    
    excretion_match = re.search(r'(经[^。]*?排泄|经[^。]*?排出)', full)
    if excretion_match:
        params.append(excretion_match.group(1))
    
    simplified = "；".join(params) if params else full[:150]
    
    return simplified, full

def extract_pregnancy_category(text):
    """提取妊娠分级"""
    match = re.search(r'妊娠[^。]*?([A-Z])\s*级', text)
    if match:
        return match.group(1)
    
    # 尝试从注意事项中提取
    match = re.search(r'孕妇.*?([A-Z])\s*级', text)
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
    """主函数"""
    # 从清单文件中提取有网址的药品（用户已手动添加）
    # 这里处理所有在清单中有网址的药品
    
    drugs_to_update = [
        # 西药
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
        (531, "https://www.hnysfww.com/goods.php?id=2016", "阿奇霉素干"),
        (542, "https://www.hnysfww.com/goods.php?id=2943", "阿维A"),
        (543, "https://www.hnysfww.com/goods.php?id=2416", "过氧苯甲酰"),
        (545, "https://www.hnysfww.com/goods.php?id=3985", "一清"),
        (553, "https://www.hnysfww.com/goods.php?id=1326", "格列吡嗪"),
        (557, "https://www.hnysfww.com/goods.php?id=2088", "氧氟沙星"),
        (561, "https://www.hnysfww.com/goods.php?id=1026", "盐酸羟考酮"),
        (564, "https://www.hnysfww.com/goods.php?id=822", "盐酸文拉法辛缓释"),
        (566, "https://www.hnysfww.com/goods.php?id=1728", "托拉塞米"),
        (572, "https://www.hnysfww.com/goods.php?id=2116", "注射用磷霉素钠"),
        (583, "https://www.hnysfww.com/goods.php?id=107", "盐酸地尔硫卓缓释"),
        (587, "https://www.hnysfww.com/goods.php?id=12841", "呋喹替尼"),
        (590, "https://www.hnysfww.com/goods.php?id=2031", "盐酸米诺环素"),
        (591, "https://www.hnysfww.com/goods.php?id=13758", "九味止咳口服液"),
        (597, "https://www.hnysfww.com/goods.php?id=1114", "可溶性止血纱布"),
        (600, "https://www.hnysfww.com/goods.php?id=679", "二甲硅油"),
        (605, "https://www.hnysfww.com/goods.php?id=13017", "生理氯化钠溶液"),
        (621, "https://www.hnysfww.com/goods.php?id=500", "胰酶肠溶"),
        (632, "https://www.hnysfww.com/goods.php?id=1149", "蚓激酶肠溶"),
        (636, "https://www.hnysfww.com/goods.php?id=7183", "全天麻"),
        (643, "https://www.hnysfww.com/goods.php?id=2653", "盐酸氮卓斯汀鼻"),
        (644, "https://www.hnysfww.com/goods.php?id=2653", "盐酸氮卓斯汀"),
        (646, "https://www.hnysfww.com/goods.php?id=390", "羟苯磺酸钙"),
        (649, "https://www.hnysfww.com/goods.php?id=10575", "米拉贝隆"),
        (652, "https://www.hnysfww.com/goods.php?id=979", "奥拉西坦"),
        (653, "https://www.hnysfww.com/goods.php?id=412", "奥美拉唑肠溶"),
        (654, "https://www.hnysfww.com/goods.php?id=1767", "赛洛多辛"),
        (660, "https://www.hnysfww.com/goods.php?id=821", "草酸艾司西酞普兰"),
        (662, "https://www.hnysfww.com/goods.php?id=9015", "利格列汀二甲双胍"),
        (666, "https://www.hnysfww.com/goods.php?id=5393", "心可宁"),
        (667, "https://www.hnysfww.com/goods.php?id=412", "注射用奥美拉唑钠"),
        (670, "https://www.hnysfww.com/goods.php?id=1057", "洛芬待因"),
        (673, "https://www.hnysfww.com/goods.php?id=815", "盐酸氟西汀"),
        (679, "https://www.hnysfww.com/goods.php?id=621", "甘草酸二铵肠溶"),
        (687, "https://www.hnysfww.com/goods.php?id=857", "注射用丙戊酸钠"),
        (690, "https://www.hnysfww.com/goods.php?id=3004", "他氟前列素"),
        (692, "https://www.hnysfww.com/goods.php?id=1655", "布地奈德鼻"),
        (695, "https://www.hnysfww.com/goods.php?id=3012", "复方托吡卡胺"),
        (697, "https://www.hnysfww.com/goods.php?id=3205", "碳酸钙D3"),
        (698, "https://www.hnysfww.com/goods.php?id=1846", "注射用青霉素钠"),
        (699, "https://www.hnysfww.com/goods.php?id=227", "可乐定控释贴"),
        (702, "https://www.hnysfww.com/goods.php?id=1254", "丙酸氯倍他索"),
        (717, "https://www.hnysfww.com/goods.php?id=8019", "五酯"),
        (718, "https://www.hnysfww.com/goods.php?id=98", "单硝酸异山梨酯缓释"),
        (719, "https://www.hnysfww.com/goods.php?id=6830", "稳心"),
        (720, "https://www.hnysfww.com/goods.php?id=1664", "复方甘草"),
        (723, "https://www.hnysfww.com/goods.php?id=13068", "芪黄通秘软"),
        (727, "https://www.hnysfww.com/goods.php?id=4652", "皮肤康洗液"),
        (732, "https://www.hnysfww.com/goods.php?id=13081", "布地格福吸入"),
    ]
    
    print("=" * 80)
    print("批量更新药品手册信息")
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
        
        time.sleep(0.5)  # 避免请求过快
    
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
