#!/usr/bin/env python3
"""
药品数据转换脚本
将Excel药品目录转换为JavaScript数据文件
供纯静态前端使用
"""

import openpyxl
import json
import re
import os
from pathlib import Path
from pypinyin import lazy_pinyin, Style

# 路径配置
BASE_DIR = Path("/Users/chenheng/Projects_AI/Project_Pharmacist")
EXCEL_FILE = BASE_DIR / "原始材料/药品目录 20260227.xlsx"
RAW_MATERIALS_DIR = BASE_DIR / "原始材料"
OUTPUT_DIR = BASE_DIR / "pharmacist-handbook/data"

def parse_price(price):
    """解析价格，处理异常值"""
    if not price:
        return 0
    if isinstance(price, (int, float)):
        return float(price)
    # 处理字符串异常值
    price_str = str(price).strip()
    if price_str in ['#N/A', 'N/A', 'NA', '-', '']:
        return 0
    try:
        return float(price_str)
    except ValueError:
        return 0

def extract_drug_name(full_name):
    """从完整名称中提取药品名称"""
    # 去除括号内容，如 (甲)、(乙)、[国基] 等
    name = re.sub(r'[\(（\[【].*?[\)）\]】]', '', full_name)
    # 去除多余空格
    name = name.strip()
    return name

def extract_drug_type(full_name):
    """提取药品类型标记"""
    types = []
    if '(甲)' in full_name or '（甲）' in full_name:
        types.append('甲类')
    if '(乙)' in full_name or '（乙）' in full_name:
        types.append('乙类')
    if '[国基]' in full_name or '【国基】' in full_name:
        types.append('国家基药')
    if '[市基]' in full_name or '【市基】' in full_name:
        types.append('市基药')
    return types

def simplify_manufacturer(manufacturer):
    """简化厂家名称"""
    if not manufacturer:
        return ""
    # 去除括号内的委托生产信息
    manufacturer = re.sub(r'[\(（].*?[\)）]', '', manufacturer)
    # 去除常见后缀
    manufacturer = re.sub(r'(股份有限公司|有限公司|有限责任公司|公司)$', '', manufacturer)
    # 去除省份前缀（可选）
    # manufacturer = re.sub(r'^(北京|上海|广州|深圳|江苏|浙江|山东|四川|重庆|天津|河北|山西|辽宁|吉林|黑龙江|安徽|福建|江西|河南|湖北|湖南|广东|海南|贵州|云南|陕西|甘肃|青海|台湾|内蒙古|广西|西藏|宁夏|新疆|香港|澳门)', '', manufacturer)
    return manufacturer.strip()

# 常见剂型关键词
DOSAGE_FORMS = [
    '片', '胶囊', '颗粒', '散', '丸', '滴丸',
    '注射液', '注射剂', '注射用', '输液',
    '软膏', '乳膏', '凝胶', '贴膏', '贴剂',
    '滴眼液', '眼膏', '滴耳液', '滴鼻液', '喷雾剂', '气雾剂',
    '栓剂', '泡腾片', '咀嚼片', '缓释片', '控释片', '肠溶片',
    '口服溶液', '口服混悬液', '糖浆', '合剂', '酊剂',
    '混悬剂', '乳剂', '洗剂', '搽剂', '涂剂', '膜剂'
]

def extract_dosage_form(name):
    """从药品名中提取剂型"""
    # 按优先级匹配剂型（长的先匹配）
    sorted_forms = sorted(DOSAGE_FORMS, key=len, reverse=True)
    for form in sorted_forms:
        if form in name:
            return form
    return "其他"

def extract_generic_name(name):
    """提取药品通用名（去除剂型后缀）"""
    # 去除剂型后缀
    sorted_forms = sorted(DOSAGE_FORMS, key=len, reverse=True)
    generic_name = name
    for form in sorted_forms:
        if generic_name.endswith(form):
            generic_name = generic_name[:-len(form)]
            break
    return generic_name.strip()

def merge_drugs_by_generic_name(drugs):
    """按通用名合并药品，剂型不同视为不同药物，仅规格不同视为同一药物"""
    print("\n正在清洗和合并药品数据...")
    
    # 按通用名+剂型分组
    drug_groups = {}
    
    for drug in drugs:
        name = drug['name']
        dosage_form = extract_dosage_form(name)
        generic_name = extract_generic_name(name)
        
        # 使用通用名+剂型作为唯一键
        key = f"{generic_name}_{dosage_form}"
        
        if key not in drug_groups:
            drug_groups[key] = {
                'generic_name': generic_name,
                'dosage_form': dosage_form,
                'full_name': drug['full_name'],
                'chemical_name': drug['chemical_name'],
                'types': drug['types'],
                'specifications': [],  # 规格列表
                'manufacturers': set(),  # 厂家集合
                'manual': drug.get('manual'),
                'source_drugs': []  # 原始药品记录
            }
        
        # 添加规格信息
        spec_info = {
            'specification': drug['specification'],
            'manufacturer': drug['manufacturer'],
            'full_manufacturer': drug['full_manufacturer'],
            'price': drug['price'],
            'unit': drug['unit'],
            'code': drug['code'],
            'approval_number': drug['approval_number'],
            'insurance_code': drug['insurance_code']
        }
        drug_groups[key]['specifications'].append(spec_info)
        drug_groups[key]['manufacturers'].add(drug['manufacturer'])
        drug_groups[key]['source_drugs'].append(drug)
    
    # 转换为最终格式
    merged_drugs = []
    for idx, (key, group) in enumerate(drug_groups.items(), 1):
        merged_drug = {
            'id': idx,
            'name': group['generic_name'],
            'dosage_form': group['dosage_form'],
            'full_name': group['full_name'],
            'chemical_name': group['chemical_name'],
            'types': group['types'],
            'manufacturers': sorted(list(group['manufacturers'])),
            'specifications': group['specifications'],
            'spec_count': len(group['specifications']),
            'manual': group['manual'] or {
                'indications': '',
                'dosage': '',
                'contraindications': '',
                'adverse_reactions': '',
                'interactions': '',
                'pregnancy_category': '',
                'pharmacokinetics': '',
                'precautions': '',
                'atc_code': '',
                'source_file': ''
            }
        }
        merged_drugs.append(merged_drug)
    
    print(f"合并完成: {len(drugs)} 条原始数据 -> {len(merged_drugs)} 条合并数据")
    print(f"平均每药物规格数: {sum(d['spec_count'] for d in merged_drugs) / len(merged_drugs):.1f}")
    
    return merged_drugs

def generate_pinyin(text):
    """生成拼音（全拼和首字母）"""
    if not text:
        return {"full": "", "initials": ""}
    
    try:
        # 全拼
        full_pinyin = ''.join(lazy_pinyin(text))
        # 首字母
        initials = ''.join(lazy_pinyin(text, style=Style.FIRST_LETTER))
        
        return {
            "full": full_pinyin.lower(),
            "initials": initials.lower()
        }
    except Exception as e:
        print(f"  拼音生成失败 '{text}': {e}")
        return {"full": "", "initials": ""}

def add_pinyin_to_drugs(drugs):
    """为所有药品添加拼音字段"""
    print("\n正在生成拼音数据...")
    
    for drug in drugs:
        # 为药品名生成拼音
        name_pinyin = generate_pinyin(drug['name'])
        drug['pinyin'] = name_pinyin['full']
        drug['pinyin_initials'] = name_pinyin['initials']
        
        # 为剂型生成拼音
        form_pinyin = generate_pinyin(drug['dosage_form'])
        drug['dosage_form_pinyin'] = form_pinyin['full']
        drug['dosage_form_initials'] = form_pinyin['initials']
    
    print(f"✓ 已为 {len(drugs)} 个药品生成拼音")
    return drugs

def load_excel_data():
    """加载Excel数据"""
    print(f"正在加载Excel文件: {EXCEL_FILE}")
    
    wb = openpyxl.load_workbook(EXCEL_FILE)
    sheet = wb.active
    
    drugs = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row[0]:  # 跳过空行
            continue
            
        drug_code = row[0]  # 药品代码
        chemical_name = row[1]  # 药品化学名
        full_name = row[2]  # 药品名称（完整）
        specification = row[3]  # 药品规格
        manufacturer = row[4]  # 厂家名称
        price = row[5]  # 零售价
        unit = row[6]  # 单位
        supplier = row[7]  # 供货单位
        approval_number = row[8]  # 批准文号
        insurance_code = row[9]  # 医保代码
        
        # 提取纯药品名和类型
        drug_name = extract_drug_name(full_name)
        drug_types = extract_drug_type(full_name)
        
        # 简化厂家名
        simple_manufacturer = simplify_manufacturer(manufacturer)
        
        drug = {
            "id": len(drugs) + 1,
            "code": drug_code,
            "name": drug_name,
            "chemical_name": chemical_name,
            "full_name": full_name,
            "specification": specification,
            "manufacturer": simple_manufacturer,
            "full_manufacturer": manufacturer,
            "price": parse_price(price),
            "unit": unit,
            "supplier": supplier,
            "approval_number": approval_number.strip() if approval_number else "",
            "insurance_code": insurance_code,
            "types": drug_types,
            "pinyin": "",  # 预留拼音字段
            "manual": None  # 手册内容，后续补充
        }
        
        drugs.append(drug)
    
    print(f"成功加载 {len(drugs)} 条药品数据")
    return drugs

def load_manual_data():
    """加载药品手册数据（从原始材料目录）"""
    manuals = {}
    
    # 查找所有.md文件
    md_files = list(RAW_MATERIALS_DIR.glob("*.md"))
    print(f"找到 {len(md_files)} 个手册文件")
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析文件名获取药品名
            # 格式: "苯海索 Trihexyphenidyl〔N04AA01〕.md"
            filename = md_file.stem
            
            # 提取中文名（第一个空格前的内容）
            chinese_name = filename.split()[0] if ' ' in filename else filename
            
            # 提取ATC编码
            atc_match = re.search(r'〔(.*?)〕', filename)
            atc_code = atc_match.group(1) if atc_match else ""
            
            # 解析Markdown表格内容
            manual_data = parse_manual_content(content)
            manual_data['atc_code'] = atc_code
            manual_data['source_file'] = filename
            
            manuals[chinese_name] = manual_data
            print(f"  ✓ 加载手册: {chinese_name}")
            
        except Exception as e:
            print(f"  ✗ 加载失败 {md_file.name}: {e}")
    
    return manuals

def parse_manual_content(content):
    """解析手册Markdown内容"""
    manual = {
        "indications": "",
        "dosage": "",
        "contraindications": "",
        "adverse_reactions": "",
        "interactions": "",
        "pregnancy_category": "",
        "pharmacokinetics": "",
        "precautions": ""
    }
    
    # 按行解析表格
    lines = content.split('\n')
    current_field = None
    
    field_mapping = {
        "适应症": "indications",
        "用法用量": "dosage",
        "禁忌": "contraindications",
        "不良反应": "adverse_reactions",
        "药物相互作用": "interactions",
        "FDA妊娠分级": "pregnancy_category",
        "药代动力学": "pharmacokinetics",
        "注意事项": "precautions"
    }
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('| --'):
            continue
        
        # 解析表格行
        if line.startswith('|') and line.endswith('|'):
            cells = [cell.strip() for cell in line[1:-1].split('|')]
            if len(cells) >= 2:
                field_name = cells[0]
                field_value = cells[1]
                
                # 映射到标准字段名
                if field_name in field_mapping:
                    manual[field_mapping[field_name]] = field_value
    
    return manual

def merge_manual_data(drugs, manuals):
    """将手册数据合并到药品数据中"""
    matched = 0
    
    for drug in drugs:
        drug_name = drug['name']
        chemical_name = drug['chemical_name']
        
        # 尝试匹配药品名
        if drug_name in manuals:
            drug['manual'] = manuals[drug_name]
            matched += 1
            print(f"  ✓ 匹配手册: {drug_name}")
        elif chemical_name in manuals:
            drug['manual'] = manuals[chemical_name]
            matched += 1
            print(f"  ✓ 匹配手册(化学名): {chemical_name}")
        else:
            # 创建空手册结构
            drug['manual'] = {
                "indications": "",
                "dosage": "",
                "contraindications": "",
                "adverse_reactions": "",
                "interactions": "",
                "pregnancy_category": "",
                "pharmacokinetics": "",
                "precautions": "",
                "atc_code": "",
                "source_file": ""
            }
    
    print(f"\n手册匹配完成: {matched}/{len(drugs)} 个药品有手册数据")
    return drugs

def generate_js_file(drugs):
    """生成JavaScript数据文件"""
    import datetime
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_DIR / "drugs.js"
    
    # 生成JS内容 - 简化格式，避免可能的解析问题
    js_content = "// 药品数据文件\n"
    js_content += f"// 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"// 药品数量: {len(drugs)}\n\n"
    js_content += "const DRUGS_DATA = "
    js_content += json.dumps(drugs, ensure_ascii=False, indent=2)
    js_content += ";\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\n✓ JavaScript数据文件已生成: {output_file}")
    print(f"  文件大小: {output_file.stat().st_size / 1024:.1f} KB")

def generate_summary(drugs):
    """生成数据统计摘要"""
    total = len(drugs)
    with_manual = sum(1 for d in drugs if d['manual'] and d['manual'].get('indications'))
    total_specs = sum(d['spec_count'] for d in drugs)
    
    # 统计类型
    type_stats = {}
    for drug in drugs:
        for t in drug.get('types', []):
            type_stats[t] = type_stats.get(t, 0) + 1
    
    # 统计剂型
    form_stats = {}
    for drug in drugs:
        form = drug.get('dosage_form', '其他')
        form_stats[form] = form_stats.get(form, 0) + 1
    
    print("\n" + "="*60)
    print("数据转换完成摘要")
    print("="*60)
    print(f"总药品数: {total} (合并后)")
    print(f"总规格数: {total_specs}")
    print(f"平均每药物规格数: {total_specs/total:.1f}")
    print(f"有手册数据: {with_manual} ({with_manual/total*100:.1f}%)")
    print(f"\n药品类型分布:")
    for t, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {t}: {count}个")
    print(f"\n剂型分布 (Top 10):")
    for form, count in sorted(form_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {form}: {count}个")
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("药品数据转换工具")
    print("="*60)
    
    # 1. 加载Excel数据
    raw_drugs = load_excel_data()
    
    # 2. 加载手册数据
    print("\n正在加载药品手册...")
    manuals = load_manual_data()
    
    # 3. 合并手册数据到原始药品
    print("\n正在合并手册数据...")
    raw_drugs = merge_manual_data(raw_drugs, manuals)
    
    # 4. 清洗和合并药品数据
    # 按通用名合并，剂型不同视为不同药物，仅规格不同视为同一药物
    drugs = merge_drugs_by_generic_name(raw_drugs)
    
    # 5. 生成拼音数据
    drugs = add_pinyin_to_drugs(drugs)
    
    # 6. 生成JS文件
    print("\n正在生成JavaScript文件...")
    generate_js_file(drugs)
    
    # 7. 生成摘要
    generate_summary(drugs)
    
    print("\n✅ 数据转换完成！")
    print(f"输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
