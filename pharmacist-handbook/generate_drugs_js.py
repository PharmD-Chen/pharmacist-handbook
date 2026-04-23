#!/usr/bin/env python3
"""
生成drugs.js数据文件，用于前端静态部署
"""

import json
from pathlib import Path

DATA_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs')
OUTPUT_FILE = DATA_DIR / 'drugs.js'

def generate_drugs_js():
    """生成drugs.js文件"""
    print('='*70)
    print('生成drugs.js数据文件')
    print('='*70)
    
    # 读取index.json
    with open(DATA_DIR / 'index.json', 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    drugs_data = []
    
    for drug_summary in index:
        drug_id = drug_summary['id']
        file_path = DATA_DIR / f'{drug_id}.json'
        
        if not file_path.exists():
            print(f'⚠️  跳过 ID {drug_id}: 文件不存在')
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            # 构建简化版数据结构
            simplified = {
                'id': drug_data['id'],
                'name': drug_data['name'],
                'full_name': drug_data.get('full_name', ''),
                'chemical_name': drug_data.get('chemical_name', ''),
                'dosage_form': drug_data.get('dosage_form', ''),
                'types': drug_data.get('types', []),
                'manufacturers': drug_data.get('manufacturers', []),
                'specifications': drug_data.get('specifications', []),
                'pinyin': drug_data.get('pinyin', ''),
                'pinyin_initials': drug_data.get('pinyin_initials', ''),
                'dosage_form_pinyin': drug_data.get('dosage_form_pinyin', ''),
                'dosage_form_initials': drug_data.get('dosage_form_initials', ''),
                'manual': drug_data.get('manual', {}),
                'url': drug_data.get('url', {})
            }
            
            drugs_data.append(simplified)
            
        except Exception as e:
            print(f'❌ 错误 ID {drug_id}: {e}')
    
    # 生成drugs.js文件
    js_content = f"""// 药品手册数据 - 自动生成于 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// 共 {len(drugs_data)} 个药品

const drugIndex = {json.dumps(drugs_data, ensure_ascii=False, indent=2)};

// 导出数据
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndex }};
}}
"""
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f'\n✅ 成功生成drugs.js')
    print(f'   共包含 {len(drugs_data)} 个药品')
    print(f'   文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB')
    print(f'   保存路径: {OUTPUT_FILE}')
    print('='*70)

if __name__ == '__main__':
    generate_drugs_js()
