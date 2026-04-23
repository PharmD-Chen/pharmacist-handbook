#!/usr/bin/env python3
"""
检查药物手册内容并自动修复常见问题 - 改进版 V2
改进点：
1. 智能提取溶媒选择（基于给药途径分类）
2. 结构化精简（保留关键信息，去除冗余描述）
3. 正确提取药代动力学参数
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')

def smart_extract_solvent(full_dosage: str) -> Optional[str]:
    """
    智能提取溶媒选择
    按给药途径分类提取，生成标准格式
    """
    if not full_dosage:
        return None
    
    solvents = []
    text = full_dosage.lower()
    
    # 定义溶媒关键词映射
    solvent_keywords = {
        '注射用水': '注射用水',
        '灭菌注射用水': '注射用水',
        '生理盐水': '0.9%氯化钠注射液',
        '氯化钠注射液': '0.9%氯化钠注射液',
        '葡萄糖注射液': '葡萄糖注射液',
        '5%葡萄糖': '5%葡萄糖注射液',
        '10%葡萄糖': '10%葡萄糖注射液',
        '葡萄糖氯化钠': '葡萄糖氯化钠注射液',
        '乳酸钠林格': '乳酸钠林格注射液',
        '复方氯化钠': '复方氯化钠注射液',
        '利多卡因': '利多卡因注射液',
    }
    
    # 1. 提取肌内注射溶媒
    im_patterns = [
        r'肌内注射[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖|利多卡印)[^。；]*?)溶解',
        r'肌注[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖|利多卡印)[^。；]*?)溶解',
    ]
    im_solvent = None
    for pattern in im_patterns:
        match = re.search(pattern, text)
        if match:
            im_solvent = match.group(1).strip()
            # 标准化
            for key, value in solvent_keywords.items():
                if key in im_solvent:
                    im_solvent = value
                    break
            solvents.append(f'肌注：用{im_solvent}溶解')
            break
    
    # 2. 提取静脉注射溶媒
    iv_patterns = [
        r'静脉注射[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖)[^。；]*?)溶解',
        r'静注[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖)[^。；]*?)溶解',
    ]
    iv_solvent = None
    for pattern in iv_patterns:
        match = re.search(pattern, text)
        if match:
            iv_solvent = match.group(1).strip()
            for key, value in solvent_keywords.items():
                if key in iv_solvent:
                    iv_solvent = value
                    break
            solvents.append(f'静注：用{iv_solvent}溶解')
            break
    
    # 3. 提取静脉滴注溶媒
    drip_patterns = [
        r'静脉滴注[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖|乳酸钠林格)[^。；]*?)(?:稀释|滴注)',
        r'静滴[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖|乳酸钠林格)[^。；]*?)(?:稀释|滴注)',
        r'滴注[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水|氯化钠|葡萄糖)[^。；]*?)稀释',
    ]
    drip_solvent = None
    for pattern in drip_patterns:
        match = re.search(pattern, text)
        if match:
            drip_solvent = match.group(1).strip()
            for key, value in solvent_keywords.items():
                if key in drip_solvent:
                    drip_solvent = value
                    break
            solvents.append(f'静滴：用{drip_solvent}稀释')
            break
    
    # 4. 提取皮下注射溶媒
    sc_patterns = [
        r'皮下注射[：:]?[^。；]*?(\d+%?[^。；]*?(?:注射用水|生理盐水)[^。；]*?)溶解',
    ]
    for pattern in sc_patterns:
        match = re.search(pattern, text)
        if match:
            sc_solvent = match.group(1).strip()
            for key, value in solvent_keywords.items():
                if key in sc_solvent:
                    sc_solvent = value
                    break
            solvents.append(f'皮下：用{sc_solvent}溶解')
            break
    
    if solvents:
        return '；'.join(solvents)
    return None


def structured_simplify(text: str, field_type: str, max_length: int = 180) -> str:
    """
    结构化精简文本
    根据不同字段类型采用不同的精简策略
    """
    if not text:
        return text
    
    # 去除HTML标签
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip()
    
    if field_type == 'indications':
        # 适应症：提取疾病名称，使用编号格式
        # 去除详细描述，保留核心适应症
        diseases = []
        # 匹配常见的疾病模式
        disease_patterns = [
            r'用于([^，。；]+?)(?:的治疗|的预防|所致|引起|缓解)',
            r'治疗([^，。；]+?)(?:，|。|；)',
            r'(?:适用于|用于)([^，。；]+?)(?:，|。|；)',
        ]
        for pattern in disease_patterns:
            matches = re.findall(pattern, text)
            diseases.extend([m.strip() for m in matches if len(m.strip()) < 30])
        
        if diseases:
            # 去重并限制数量
            unique_diseases = list(dict.fromkeys(diseases))[:8]
            return '用于' + '；'.join(unique_diseases) + '。'
        
        # 如果无法提取，简化原文
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) > 3:
            return lines[0][:max_length-3] + '...'
        return text[:max_length]
    
    elif field_type == 'dosage':
        # 用法用量：按人群和给药途径分类
        # 提取关键剂量信息
        dosage_info = []
        
        # 成人剂量
        adult_match = re.search(r'成人[：:]?([^。；]*?(?:\d+(?:\.\d+)?(?:mg|g|ml|μg|U|单位)[^。；]*?))', text)
        if adult_match:
            dosage_info.append('成人：' + adult_match.group(1).strip()[:50])
        
        # 儿童剂量
        child_match = re.search(r'儿童[：:]?([^。；]*?(?:\d+(?:\.\d+)?(?:mg|g|ml|μg|U|单位)[^。；]*?))', text)
        if child_match:
            dosage_info.append('儿童：' + child_match.group(1).strip()[:50])
        
        if dosage_info:
            return '；'.join(dosage_info)
        
        # 提取第一个完整的剂量说明
        first_dose = re.search(r'([^。；]{10,100}?[。；])', text)
        if first_dose:
            return first_dose.group(1).strip()
        
        return text[:max_length]
    
    elif field_type == 'contraindications':
        # 禁忌症：提取禁忌人群/情况
        contras = []
        contra_patterns = [
            r'([对本品|对[^。；]*?过敏)[^。；]*?禁用',
            r'(孕妇|哺乳期|儿童|老年人)[^。；]*?禁用',
            r'([高|低][^。；]*?血症)[^。；]*?禁用',
        ]
        for pattern in contra_patterns:
            matches = re.findall(pattern, text)
            contras.extend(matches)
        
        if contras:
            return '；'.join(list(dict.fromkeys(contras))[:5]) + '禁用。'
        
        # 简化原文
        return text[:max_length].replace('<br>', ' ')
    
    elif field_type == 'adverse_reactions':
        # 不良反应：提取反应类型
        reactions = []
        # 匹配常见不良反应描述
        reaction_patterns = [
            r'(?:常见|可见|包括)([^：。；]+?)(?:反应|症状|不良)',
            r'([皮疹|恶心|呕吐|腹泻|头痛|头晕|过敏|发热|疼痛|瘙痒][^。；]*?)',
        ]
        
        # 提取具体的不良反应名称
        common_reactions = ['皮疹', '恶心', '呕吐', '腹泻', '头痛', '头晕', '发热', '瘙痒', '过敏', '疼痛', '乏力', '嗜睡']
        found_reactions = []
        for reaction in common_reactions:
            if reaction in text:
                found_reactions.append(reaction)
        
        if found_reactions:
            return '常见：' + '、'.join(found_reactions[:8]) + '等。'
        
        return text[:max_length].replace('<br>', ' ')
    
    elif field_type == 'precautions':
        # 注意事项：提取警告信息
        warnings = []
        warning_keywords = ['慎用', '禁用', '注意', '监测', '避免', '不宜']
        
        for keyword in warning_keywords:
            if keyword in text:
                # 提取包含关键词的短语
                pattern = rf'[^。；]*?{keyword}[^。；]*?[。；]'
                matches = re.findall(pattern, text)
                warnings.extend([m.strip() for m in matches[:2]])
        
        if warnings:
            return ''.join(list(dict.fromkeys(warnings))[:3])[:max_length]
        
        return text[:max_length].replace('<br>', ' ')
    
    elif field_type == 'pharmacokinetics':
        # 药代动力学：提取关键参数
        params = []
        
        # 提取半衰期
        t_half = re.search(r'半衰期.*?([\d\.]+\s*(?:h|小时|min|分钟))', text)
        if t_half:
            params.append(f't1/2约{t_half.group(1)}')
        
        # 提取蛋白结合率
        protein = re.search(r'蛋白结合率.*?([\d\.]+\s*%?)', text)
        if protein:
            params.append(f'蛋白结合率{protein.group(1)}')
        
        # 提取达峰时间
        t_max = re.search(r'达峰时间.*?([\d\.]+\s*(?:h|小时))', text)
        if t_max:
            params.append(f'Tmax约{t_max.group(1)}')
        
        # 提取代谢排泄信息
        if '肝脏' in text or '肝' in text:
            params.append('肝脏代谢')
        if '肾脏' in text or '肾' in text:
            params.append('肾脏排泄')
        
        if params:
            return '，'.join(params) + '。'
        
        return None
    
    # 默认处理
    return text[:max_length]


def fix_interactions(text: str) -> str:
    """
    修正药物相互作用字段
    如果内容异常，返回标准格式
    """
    if not text:
        return '暂未发现有临床意义的药物相互作用。'
    
    # 检查是否包含非相互作用内容
    abnormal_keywords = ['本品为', '保存不当', '如发现', '药液', '浑浊', '沉淀', '慎用', '注意', '监测']
    abnormal_count = sum(1 for kw in abnormal_keywords if kw in text)
    
    if abnormal_count >= 2 or len(text) > 300:
        # 内容异常，可能是提取错误
        return '暂未发现有临床意义的药物相互作用。'
    
    return text


def check_and_fix_drug_v2(drug_id: int) -> Tuple[bool, List[str]]:
    """
    检查并修复单个药物 - V2版本
    返回(是否修改, 修改记录)
    """
    file_path = DATA_DIR / f'{drug_id}.json'
    if not file_path.exists():
        return False, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_data = json.dumps(data, ensure_ascii=False, sort_keys=True)
    manual = data.get('manual', {})
    name = data.get('name', '')
    dosage_form = data.get('dosage_form', '')
    changes = []
    
    is_injection = '注射' in name or '注射' in dosage_form
    
    # 修复1：注射剂型添加溶媒选择（使用智能提取）
    if is_injection and not manual.get('solvent'):
        full_dosage = manual.get('full_dosage', '')
        if full_dosage:
            solvent = smart_extract_solvent(full_dosage)
            if solvent:
                manual['solvent'] = solvent
                changes.append('添加溶媒选择')
    
    # 修复2：精简版内容过长（使用结构化精简）
    fields_to_simplify = {
        'indications': ('indications', 180),
        'dosage': ('dosage', 180),
        'contraindications': ('contraindications', 150),
        'adverse_reactions': ('adverse_reactions', 180),
        'precautions': ('precautions', 180),
    }
    
    for field, (field_type, max_len) in fields_to_simplify.items():
        content = manual.get(field, '')
        full_field = f'full_{field}'
        full_content = manual.get(full_field, '')
        
        # 如果精简版过长或包含HTML标签
        if content and (len(content) > max_len or '<br>' in content or '<' in content):
            if full_content:
                # 使用结构化精简
                simplified = structured_simplify(full_content, field_type, max_len)
                if simplified and len(simplified) < len(content):
                    manual[field] = simplified
                    changes.append(f'结构化精简{field}')
            else:
                # 没有完整版，直接精简现有内容
                simplified = structured_simplify(content, field_type, max_len)
                if simplified and len(simplified) < len(content):
                    manual[field] = simplified
                    changes.append(f'结构化精简{field}')
    
    # 修复3：修正interactions字段
    interactions = manual.get('interactions', '')
    fixed_interactions = fix_interactions(interactions)
    if fixed_interactions != interactions:
        manual['interactions'] = fixed_interactions
        changes.append('修正interactions字段')
    
    # 修复4：修正药代动力学（如果内容异常）
    pk = manual.get('pharmacokinetics', '')
    full_pk = manual.get('full_pharmacokinetics', '')
    
    # 检查药代动力学是否异常（过短或被截断）
    if pk and (len(pk) < 20 or pk.endswith('...') or '。' not in pk):
        if full_pk:
            new_pk = structured_simplify(full_pk, 'pharmacokinetics', 200)
            if new_pk:
                manual['pharmacokinetics'] = new_pk
                changes.append('修正药代动力学')
        else:
            # 没有完整版，清空异常内容
            manual['pharmacokinetics'] = ''
            changes.append('清空异常药代动力学')
    
    # 检查是否有修改
    new_data = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if new_data != original_data:
        # 保存修改
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, changes
    
    return False, []


def process_batch(start_idx: int, end_idx: int, all_ids: List[int]) -> Dict:
    """处理一批药物"""
    results = {
        'checked': 0,
        'fixed': 0,
        'details': []
    }
    
    batch_ids = all_ids[start_idx:end_idx]
    
    print(f'\n{"="*70}')
    print(f'处理第 {start_idx+1}-{min(end_idx, len(all_ids))} 个药物 (共 {len(all_ids)} 个)')
    print(f'{"="*70}')
    
    for drug_id in batch_ids:
        results['checked'] += 1
        modified, changes = check_and_fix_drug_v2(drug_id)
        
        if modified:
            results['fixed'] += 1
            results['details'].append({
                'id': drug_id,
                'changes': changes
            })
            # 读取药物名称
            file_path = DATA_DIR / f'{drug_id}.json'
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ ID {drug_id}: {data.get('name', '')}")
            for change in changes:
                print(f"   - {change}")
    
    print(f'\n本批次: 检查 {results["checked"]} 个, 修复 {results["fixed"]} 个')
    return results


def main():
    # 获取所有药物ID
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    all_ids = [d['id'] for d in index]
    all_ids.sort()
    
    print(f'共有 {len(all_ids)} 个药物')
    print('每20个药物为一组进行处理（V2改进版）')
    print('\n改进点：')
    print('1. 智能溶媒提取 - 按给药途径分类提取')
    print('2. 结构化精简 - 根据字段类型采用不同策略')
    print('3. 药代动力学修正 - 提取关键参数而非截断')
    
    # 先处理前100个药物作为测试
    batch_size = 20
    total_fixed = 0
    
    for i in range(0, min(100, len(all_ids)), batch_size):
        results = process_batch(i, i + batch_size, all_ids)
        total_fixed += results['fixed']
        
        if i + batch_size < len(all_ids) and i + batch_size < 100:
            print(f'\n已完成 {min(i+batch_size, 100)}/100 个药物')
    
    # 汇总
    print(f'\n{"="*70}')
    print('前100个药物处理完成（V2改进版）！')
    print(f'共修复 {total_fixed} 个药物')
    print(f'{"="*70}')


if __name__ == '__main__':
    main()
