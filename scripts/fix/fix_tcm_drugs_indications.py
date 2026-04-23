#!/usr/bin/env python3
"""
修复中成药indications字段 - 使用"功能主治"替代"适应证"
"""
import json
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

# 项目根目录
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'

# 需要修复的中成药列表
TCM_DRUGS = [
    {'id': 371, 'name': '湿润烧伤膏'},
    {'id': 383, 'name': '康复新液'},
    {'id': 389, 'name': '天丹通络'},
    {'id': 390, 'name': '天舒'},
    {'id': 472, 'name': '六味地黄'},
    {'id': 487, 'name': '※▲※▲清开灵'},
    {'id': 488, 'name': '脉络宁口服液'},
    {'id': 502, 'name': '白脉'},
    {'id': 524, 'name': '※▲连榆烧伤膏'},
    {'id': 526, 'name': '※▲香丹'},
    {'id': 626, 'name': '解郁除烦'},
    {'id': 874, 'name': '活血止痛膏'},
    {'id': 882, 'name': '西帕依固龈液'},
    {'id': 883, 'name': '复方阿胶浆'},
    {'id': 885, 'name': '牛黄清心'},
    {'id': 918, 'name': '胆宁'},
    {'id': 927, 'name': '※▲儿茶上清'},
    {'id': 933, 'name': '华佗再造'},
    {'id': 968, 'name': '金匮肾气'},
    {'id': 1010, 'name': '祛风骨痛凝胶膏'},
    {'id': 1015, 'name': '筋骨伤'},
    {'id': 1021, 'name': '大川芎口服液'},
    {'id': 1032, 'name': '桂林西瓜霜'},
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    return text.strip()

def extract_tcm_fields(text):
    """提取中成药各字段 - 优先使用中成药字段名"""
    info = {}
    
    # 1. 功能主治（中成药使用"功能主治"）
    match = re.search(r'功能主治(.+?)(?:成份|药理作用|用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['indications'] = content
        info['full_indications'] = content
    
    # 2. 成份/药理作用
    match = re.search(r'成份/药理作用(.+?)(?:用法用量|不良反应|禁忌|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['pharmacokinetics'] = content
        info['full_pharmacokinetics'] = content
    
    # 3. 用法用量
    match = re.search(r'用法与?用量(.+?)(?:不良反应|禁忌|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['dosage'] = content
        info['full_dosage'] = content
    
    # 4. 禁忌症（中成药常用"禁忌症"）
    match = re.search(r'禁忌症?(.+?)(?:不良反应|药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['contraindications'] = content
        info['full_contraindications'] = content
    
    # 5. 不良反应
    match = re.search(r'不良反应(.+?)(?:药物相互作用|注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['adverse_reactions'] = content
        info['full_adverse_reactions'] = content
    
    # 6. 药物相互作用
    match = re.search(r'药物相互作用(.+?)(?:注意事项|贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['interactions'] = content
        info['full_interactions'] = content
    
    # 7. 注意事项
    match = re.search(r'注意事项(.+?)(?:贮藏|$)', text, re.DOTALL)
    if match:
        content = clean_text(match.group(1))
        info['precautions'] = content
        info['full_precautions'] = content
    
    return info

def fetch_drug_info(url):
    """从网站获取药品信息"""
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含药品信息的table
        tables = soup.find_all('table')
        if tables:
            text = tables[0].get_text()
            return extract_tcm_fields(text)
        return None
    except Exception as e:
        print(f"  获取失败: {str(e)}")
        return None

def update_tcm_drugs():
    """更新中成药数据"""
    print("=" * 80)
    print("修复中成药indications字段")
    print("=" * 80)
    
    updated_count = 0
    failed_drugs = []
    
    for drug in TCM_DRUGS:
        drug_id = drug['id']
        drug_name = drug['name']
        
        print(f"\n处理: ID {drug_id} - {drug_name}")
        
        # 读取药品文件
        drug_file = DRUGS_DIR / f'{drug_id}.json'
        if not drug_file.exists():
            print(f"  ✗ 文件不存在")
            failed_drugs.append({'id': drug_id, 'name': drug_name, 'reason': '文件不存在'})
            continue
        
        try:
            with open(drug_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            # 检查是否有网址
            url_data = drug_data.get('url', {})
            hnysfww_url = url_data.get('hnysfww', '')
            
            if not hnysfww_url:
                print(f"  ✗ 无湖南药事服务网网址")
                failed_drugs.append({'id': drug_id, 'name': drug_name, 'reason': '无网址'})
                continue
            
            # 获取网站数据
            print(f"  正在抓取: {hnysfww_url}")
            new_info = fetch_drug_info(hnysfww_url)
            
            if not new_info:
                print(f"  ✗ 抓取失败")
                failed_drugs.append({'id': drug_id, 'name': drug_name, 'reason': '抓取失败'})
                continue
            
            # 更新manual字段
            manual = drug_data.get('manual', {})
            
            # 只更新之前为空的字段
            for key, value in new_info.items():
                if not manual.get(key) or manual.get(key) == 'null' or manual.get(key) == '':
                    manual[key] = value
                    print(f"  ✓ 更新 {key}")
            
            # 确保source字段
            manual['source'] = '湖南药事服务网'
            
            drug_data['manual'] = manual
            
            # 保存文件
            with open(drug_file, 'w', encoding='utf-8') as f:
                json.dump(drug_data, f, ensure_ascii=False, indent=2)
            
            updated_count += 1
            print(f"  ✓ 更新完成")
            
            # 延迟避免请求过快
            time.sleep(1)
            
        except Exception as e:
            print(f"  ✗ 错误: {str(e)}")
            failed_drugs.append({'id': drug_id, 'name': drug_name, 'reason': str(e)})
    
    print(f"\n{'=' * 80}")
    print(f"处理完成: 成功 {updated_count}/{len(TCM_DRUGS)}")
    
    if failed_drugs:
        print(f"\n失败的药品 ({len(failed_drugs)}个):")
        for drug in failed_drugs:
            print(f"  ID {drug['id']}: {drug['name']} - {drug['reason']}")
    
    return updated_count, failed_drugs

if __name__ == '__main__':
    update_tcm_drugs()
