#!/usr/bin/env python3
"""
列出没有详细信息的药品清单
"""
import json
import sys
sys.path.insert(0, '/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook')

def main():
    with open('data/drugs.js', 'r') as f:
        content = f.read()
    start = content.find('[')
    end = content.rfind(']')
    data = json.loads(content[start:end+1])

    # 没有详细信息的药品
    without_manual = [d for d in data if not (d.get('manual') and d['manual'].get('source'))]
    
    print('='*70)
    print(f'📋 没有详细信息的药品清单 (共 {len(without_manual)} 个)')
    print('='*70)
    
    # 按剂型分组
    by_dosage_form = {}
    for drug in without_manual:
        form = drug.get('dosage_form', '未知剂型')
        if form not in by_dosage_form:
            by_dosage_form[form] = []
        by_dosage_form[form].append(drug)
    
    # 输出统计
    print(f'\n📊 按剂型分类统计：')
    for form in sorted(by_dosage_form.keys()):
        print(f'  {form}: {len(by_dosage_form[form])} 个')
    
    print(f'\n' + '='*70)
    print('📄 药品详细列表（前200个）：')
    print('='*70)
    
    # 输出前200个药品
    count = 0
    for drug in without_manual[:200]:
        count += 1
        name = drug.get('name', '')
        form = drug.get('dosage_form', '')
        full_name = drug.get('full_name', '')
        print(f'{count}. {name} | {form} | {full_name}')
    
    if len(without_manual) > 200:
        print(f'\n... 还有 {len(without_manual) - 200} 个药品未显示')
    
    # 保存完整列表到文件
    output_file = 'data/drugs_without_manual.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'没有详细信息的药品清单 (共 {len(without_manual)} 个)\n')
        f.write('='*70 + '\n\n')
        for i, drug in enumerate(without_manual, 1):
            name = drug.get('name', '')
            form = drug.get('dosage_form', '')
            full_name = drug.get('full_name', '')
            f.write(f'{i}. {name} | {form} | {full_name}\n')
    
    print(f'\n✅ 完整清单已保存至: {output_file}')

if __name__ == '__main__':
    main()
