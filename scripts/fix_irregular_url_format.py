#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复异常格式的网址提取
处理如：| 356 | 盐酸安罗替尼 | 胶囊 | ※▲(乙10%)盐酸安罗替尼胶囊 | 待补充 |https://... 这种格式
"""

import json
import re
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
DRUGS_DIR = PROJECT_ROOT / "pharmacist-handbook/data/drugs"
BACKUP_MD_FILE = PROJECT_ROOT / "药品网址汇总_backup.md"

def parse_irregular_format():
    """解析异常格式的网址"""
    drug_urls = {}
    
    with open(BACKUP_MD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配异常格式: | 序号 | 药品名称 | 剂型 | 规格 | 待补充 |https://...
    # 或者: | 序号 | 药品名称 | 剂型 | 规格 | 文字 |https://...
    irregular_pattern = r'\|\s*\d+\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*[^|]+\s*\|\s*(https://www\.hnysfww\.com/goods\.php\?id=\d+)'
    
    matches = re.findall(irregular_pattern, content)
    for match in matches:
        drug_name = match[0].strip()
        dosage_form = match[1].strip()
        specification = match[2].strip()
        url = match[3].strip()
        
        # 清理药品名称（去除特殊标记）
        clean_name = re.sub(r'[※▲\(\)（）]', '', drug_name).strip()
        
        drug_urls[clean_name] = {
            'name': drug_name,
            'dosage_form': dosage_form,
            'specification': specification,
            'url': url
        }
    
    return drug_urls

def load_drug(drug_id):
    """加载药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    if not drug_file.exists():
        return None
    with open(drug_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_drug(drug_id, drug_data):
    """保存药品数据"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    with open(drug_file, 'w', encoding='utf-8') as f:
        json.dump(drug_data, f, ensure_ascii=False, indent=2)

def update_drug_url(drug_id, url):
    """更新单个药品的URL"""
    drug_data = load_drug(drug_id)
    
    if not drug_data:
        return False, "文件不存在"
    
    # 检查是否已有URL
    existing_url = drug_data.get('url', {})
    if existing_url.get('hnysfww') == url:
        return False, "URL已存在且相同"
    
    # 更新URL
    drug_data['url'] = {
        'hnysfww': url,
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    }
    
    # 保存文件
    save_drug(drug_id, drug_data)
    
    return True, "更新成功"

def main():
    """主函数"""
    print("=" * 80)
    print("修复异常格式的网址提取")
    print("=" * 80)
    
    # 解析异常格式的网址
    print("\n正在解析药品网址汇总_backup.md中的异常格式...")
    drug_urls = parse_irregular_format()
    print(f"找到 {len(drug_urls)} 个异常格式的药品网址")
    
    # 显示找到的药品
    if drug_urls:
        print("\n找到的药品:")
        for name, info in drug_urls.items():
            print(f"  - {name}: {info['url']}")
    
    # 加载药品索引
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)
    
    # 统计
    updated = []
    already_has = []
    not_found = []
    
    print("\n开始匹配和更新...")
    
    for clean_name, info in drug_urls.items():
        url = info['url']
        
        # 在索引中查找匹配的药品
        matched = False
        for drug in drugs_index:
            drug_id = drug['id']
            drug_name = drug['name']
            
            # 清理药品名称进行匹配
            clean_drug_name = re.sub(r'[※▲\(\)（）]', '', drug_name).strip()
            
            if clean_name == clean_drug_name:
                matched = True
                
                # 检查当前状态
                drug_data = load_drug(drug_id)
                if not drug_data:
                    not_found.append({
                        'id': drug_id,
                        'name': drug_name,
                        'reason': '文件不存在'
                    })
                    continue
                
                existing_url = drug_data.get('url', {})
                if existing_url.get('hnysfww'):
                    already_has.append({
                        'id': drug_id,
                        'name': drug_name,
                        'url': url
                    })
                    continue
                
                # 更新药品文件
                success, message = update_drug_url(drug_id, url)
                if success:
                    updated.append({
                        'id': drug_id,
                        'name': drug_name,
                        'url': url
                    })
                    print(f"✓ ID {drug_id}: {drug_name}")
                else:
                    not_found.append({
                        'id': drug_id,
                        'name': drug_name,
                        'reason': message
                    })
                break
        
        if not matched:
            not_found.append({
                'id': None,
                'name': clean_name,
                'reason': '未在索引中找到匹配'
            })
    
    # 输出统计
    print("\n" + "=" * 80)
    print("更新统计")
    print("=" * 80)
    print(f"文档中找到: {len(drug_urls)} 个")
    print(f"成功更新: {len(updated)} 个")
    print(f"已有网址: {len(already_has)} 个")
    print(f"未找到: {len(not_found)} 个")
    
    if updated:
        print("\n已更新的药品:")
        for item in updated:
            print(f"  - ID {item['id']}: {item['name']}")
    
    if not_found:
        print("\n未找到的药品:")
        for item in not_found:
            if item['id']:
                print(f"  - ID {item['id']}: {item['name']} - {item['reason']}")
            else:
                print(f"  - {item['name']} - {item['reason']}")
    
    print("\n" + "=" * 80)
    print("处理完成！")
    print("=" * 80)

if __name__ == '__main__':
    main()
