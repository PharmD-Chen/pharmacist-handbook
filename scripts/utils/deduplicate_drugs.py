#!/usr/bin/env python3
"""根据剂型区分重复药品并自动去重，保留最新记录"""

import re
from collections import OrderedDict

def parse_drug_entry(line, line_num):
    """解析药品条目，提取名称、剂型、网址等信息"""
    # 列表格式: `- 药品名 https://...`
    list_match = re.match(r'^-\s*([^\n]+?)\s+(https://www\.hnysfww\.com/goods\.php\?id=\d+)', line)
    if list_match:
        name = list_match.group(1).strip()
        url = list_match.group(2).strip()
        # 从名称中尝试提取剂型
        dosage_form = extract_dosage_form_from_name(name)
        return {
            'name': name,
            'dosage_form': dosage_form,
            'url': url,
            'line_num': line_num,
            'source': 'list'
        }
    
    # 表格格式: `| 序号 | 药品名 | 剂型 | 规格 | 网址 |`
    table_match = re.match(r'\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*\[链接\]\((https://www\.hnysfww\.com/goods\.php\?id=\d+)\)\s*\|', line)
    if table_match:
        name = table_match.group(1).strip()
        dosage_form = table_match.group(2).strip()
        url = table_match.group(4).strip()
        return {
            'name': name,
            'dosage_form': dosage_form,
            'url': url,
            'line_num': line_num,
            'source': 'table'
        }
    
    return None

def extract_dosage_form_from_name(name):
    """从药品名称中提取剂型"""
    # 常见剂型关键词
    dosage_keywords = [
        '片', '胶囊', '颗粒', '丸', '散', '滴丸',
        '注射液', '注射用', '粉针', '输液',
        '软膏', '乳膏', '凝胶', '贴剂', '栓剂',
        '滴眼液', '眼膏', '滴鼻液', '滴耳液',
        '口服溶液', '糖浆', '混悬液', '合剂',
        '喷雾剂', '吸入用', '含漱液', '外用溶液',
        '膜', '海绵', '纱布'
    ]
    
    for keyword in dosage_keywords:
        if keyword in name:
            return keyword
    return '其他'

def normalize_name(name):
    """标准化药品名称用于比较"""
    # 去除※▲标记
    name = re.sub(r'^[※▲]+', '', name)
    # 去除甲乙类标记
    name = re.sub(r'^\([^)]+\)', '', name)
    # 去除[国基]等标记
    name = re.sub(r'\[[^\]]+\]', '', name)
    # 去除空格
    name = re.sub(r'\s+', '', name)
    return name.strip()

def deduplicate_drugs(content):
    """去重药品，根据剂型区分，保留最新记录（行号大的为最新）"""
    lines = content.split('\n')
    
    # 用于存储唯一的药品: {(标准化名称, 剂型): 最新条目}
    unique_drugs = OrderedDict()
    
    # 统计信息
    total_entries = 0
    duplicate_groups = {}
    
    for line_num, line in enumerate(lines, 1):
        entry = parse_drug_entry(line, line_num)
        if entry:
            total_entries += 1
            normalized_name = normalize_name(entry['name'])
            dosage_form = entry['dosage_form']
            key = (normalized_name, dosage_form)
            
            if key in unique_drugs:
                # 发现重复，保留行号大的（最新的）
                old_entry = unique_drugs[key]
                if entry['line_num'] > old_entry['line_num']:
                    # 记录重复信息
                    if key not in duplicate_groups:
                        duplicate_groups[key] = [old_entry]
                    duplicate_groups[key].append(entry)
                    # 保留新的
                    unique_drugs[key] = entry
                else:
                    # 记录重复信息
                    if key not in duplicate_groups:
                        duplicate_groups[key] = [entry]
                    duplicate_groups[key].append(old_entry)
            else:
                unique_drugs[key] = entry
    
    return unique_drugs, duplicate_groups, total_entries

def rebuild_content(content, unique_drugs):
    """根据去重后的药品重建文件内容"""
    lines = content.split('\n')
    
    # 收集需要保留的行号
    keep_line_nums = set()
    for entry in unique_drugs.values():
        keep_line_nums.add(entry['line_num'])
    
    # 重建内容
    new_lines = []
    for line_num, line in enumerate(lines, 1):
        # 保留非药品行（标题、分隔符等）
        if line_num in keep_line_nums or not is_drug_line(line):
            new_lines.append(line)
    
    return '\n'.join(new_lines)

def is_drug_line(line):
    """判断是否为药品条目行"""
    # 列表格式
    if re.match(r'^-\s*[^\n]+\s+https://www\.hnysfww\.com', line):
        return True
    # 表格格式
    if re.match(r'\|\s*\d+\s*\|', line):
        return True
    return False

def main():
    input_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md'
    backup_file = '/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总_backup.md'
    
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 60)
    print("药品网址汇总 - 去重处理")
    print("=" * 60)
    
    # 备份原文件
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n📦 已备份原文件: {backup_file}")
    
    # 去重
    unique_drugs, duplicate_groups, total_entries = deduplicate_drugs(content)
    
    print(f"\n📊 统计信息:")
    print(f"   原始条目数: {total_entries}")
    print(f"   去重后条目数: {len(unique_drugs)}")
    print(f"   重复组数: {len(duplicate_groups)}")
    print(f"   删除重复数: {total_entries - len(unique_drugs)}")
    
    # 显示重复详情
    if duplicate_groups:
        print(f"\n🔍 重复详情（显示前10组）:")
        print("-" * 60)
        for idx, (key, entries) in enumerate(list(duplicate_groups.items())[:10], 1):
            name, dosage = key
            print(f"\n{idx}. {name} ({dosage})")
            print(f"   重复次数: {len(entries)} 次")
            for i, e in enumerate(entries, 1):
                print(f"   第{i}次: 行{e['line_num']} - {e['name']}")
    
    # 重建内容
    new_content = rebuild_content(content, unique_drugs)
    
    # 保存新文件
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ 去重完成！")
    print(f"   已更新文件: {input_file}")
    print(f"   保留条目: {len(unique_drugs)} 个")

if __name__ == '__main__':
    main()
