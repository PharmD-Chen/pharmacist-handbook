#!/usr/bin/env python3
"""
优化中成药字段提取 - 修复字段边界问题
"""
import json
import re
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'

# 23个中成药
TCM_DRUG_IDS = [371, 383, 389, 390, 472, 487, 488, 502, 524, 526, 626, 874, 882, 883, 885, 918, 927, 933, 968, 1010, 1015, 1021, 1032]

def clean_text(text):
    """清理文本"""
    if not text:
        return ""
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ').replace('\u3000', ' ')
    # 移除常见的后续字段混入内容
    text = re.sub(r'\s*剂型与规格.*', '', text)
    text = re.sub(r'\s*哪儿有.*', '', text)
    text = re.sub(r'\s*用法与用量.*', '', text)
    text = re.sub(r'\s*药物相互作用.*', '', text)
    text = re.sub(r'\s*禁忌症.*', '', text)
    return text.strip()

def refine_extraction(drug_id):
    """优化字段提取"""
    drug_file = DRUGS_DIR / f'{drug_id}.json'
    
    try:
        with open(drug_file, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        
        manual = drug_data.get('manual', {})
        
        # 清理各字段中的混入内容
        fields_to_clean = [
            'dosage', 'full_dosage',
            'contraindications', 'full_contraindications',
            'adverse_reactions', 'full_adverse_reactions',
            'interactions', 'full_interactions',
            'precautions', 'full_precautions',
            'pharmacokinetics', 'full_pharmacokinetics'
        ]
        
        for field in fields_to_clean:
            if manual.get(field):
                original = manual[field]
                cleaned = clean_text(original)
                if original != cleaned:
                    manual[field] = cleaned
                    print(f"  清理 {field}: {original[:50]}... -> {cleaned[:50]}...")
        
        # 特殊处理：如果adverse_reactions包含了禁忌症内容，进行分割
        if manual.get('adverse_reactions') and '禁忌症' in manual['adverse_reactions']:
            parts = manual['adverse_reactions'].split('禁忌症')
            if len(parts) == 2:
                manual['adverse_reactions'] = parts[0].strip()
                if not manual.get('contraindications'):
                    manual['contraindications'] = parts[1].strip()
                    manual['full_contraindications'] = parts[1].strip()
                print(f"  分割 adverse_reactions 中的禁忌症内容")
        
        # 特殊处理：如果interactions包含了用法用量内容，进行分割
        if manual.get('interactions') and len(manual['interactions']) > 200:
            # 只保留第一句话（通常是药物相互作用的说明）
            sentences = manual['interactions'].split('。')
            if len(sentences) > 1:
                first_sentence = sentences[0] + '。'
                if '药物相互作用' in first_sentence or '其他药物' in first_sentence:
                    manual['interactions'] = first_sentence
                    manual['full_interactions'] = first_sentence
                    print(f"  精简 interactions")
        
        # 特殊处理：如果precautions包含了其他字段，进行清理
        if manual.get('precautions') and len(manual['precautions']) > 300:
            # 保留到"药物相互作用"之前的内容
            if '药物相互作用' in manual['precautions']:
                parts = manual['precautions'].split('药物相互作用')
                manual['precautions'] = parts[0].strip()
                manual['full_precautions'] = parts[0].strip()
                print(f"  清理 precautions 中的混入内容")
        
        # 特殊处理：如果pharmacokinetics包含了用法用量，进行分割
        if manual.get('pharmacokinetics') and '用法与用量' in manual['pharmacokinetics']:
            parts = manual['pharmacokinetics'].split('用法与用量')
            manual['pharmacokinetics'] = parts[0].strip()
            manual['full_pharmacokinetics'] = parts[0].strip()
            print(f"  分割 pharmacokinetics 中的用法用量内容")
        
        drug_data['manual'] = manual
        
        # 保存文件
        with open(drug_file, 'w', encoding='utf-8') as f:
            json.dump(drug_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("优化中成药字段提取")
    print("=" * 80)
    
    success_count = 0
    
    for drug_id in TCM_DRUG_IDS:
        drug_file = DRUGS_DIR / f'{drug_id}.json'
        if not drug_file.exists():
            print(f"\nID {drug_id}: 文件不存在")
            continue
        
        # 读取药品名称
        with open(drug_file, 'r', encoding='utf-8') as f:
            drug_data = json.load(f)
        drug_name = drug_data.get('name', 'Unknown')
        
        print(f"\n处理: ID {drug_id} - {drug_name}")
        
        if refine_extraction(drug_id):
            success_count += 1
            print(f"  ✓ 完成")
        else:
            print(f"  ✗ 失败")
    
    print(f"\n{'=' * 80}")
    print(f"处理完成: {success_count}/{len(TCM_DRUG_IDS)}")

if __name__ == '__main__':
    main()
