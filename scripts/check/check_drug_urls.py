#!/usr/bin/env python3
"""
检查所有药品是否都有网址对应
"""
import json
from pathlib import Path

# 项目根目录
PROJECT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
DRUGS_DIR = PROJECT_DIR / 'pharmacist-handbook' / 'data' / 'drugs'

def check_drug_urls():
    """检查所有药品的网址情况"""
    
    # 读取药品索引
    with open(DRUGS_DIR / 'index.json', 'r', encoding='utf-8') as f:
        drugs_index = json.load(f)
    
    # 统计
    total_drugs = len(drugs_index)
    drugs_with_url = 0
    drugs_without_url = []
    drugs_with_hnysfww_url = 0
    drugs_with_other_url = 0
    
    print("=" * 80)
    print("药品网址检查报告")
    print("=" * 80)
    print(f"\n总药品数: {total_drugs}")
    
    # 检查每个药品
    for drug in drugs_index:
        drug_id = drug['id']
        drug_name = drug['name']
        
        # 读取药品详情文件
        drug_file = DRUGS_DIR / f'{drug_id}.json'
        
        if not drug_file.exists():
            drugs_without_url.append({
                'id': drug_id,
                'name': drug_name,
                'reason': '药品文件不存在'
            })
            continue
        
        try:
            with open(drug_file, 'r', encoding='utf-8') as f:
                drug_data = json.load(f)
            
            # 检查是否有url字段
            if 'url' not in drug_data:
                drugs_without_url.append({
                    'id': drug_id,
                    'name': drug_name,
                    'reason': '缺少url字段'
                })
                continue
            
            url_data = drug_data.get('url', {})
            
            # 检查是否有湖南药事服务网网址
            if 'hnysfww' in url_data and url_data['hnysfww']:
                drugs_with_hnysfww_url += 1
                drugs_with_url += 1
            elif url_data:
                # 有其他网址
                drugs_with_other_url += 1
                drugs_with_url += 1
            else:
                # url字段存在但为空
                drugs_without_url.append({
                    'id': drug_id,
                    'name': drug_name,
                    'reason': 'url字段为空'
                })
                
        except Exception as e:
            drugs_without_url.append({
                'id': drug_id,
                'name': drug_name,
                'reason': f'读取文件错误: {str(e)}'
            })
    
    # 打印统计结果
    print(f"\n【统计结果】")
    print(f"✓ 有湖南药事服务网网址: {drugs_with_hnysfww_url}")
    print(f"✓ 有其他网址: {drugs_with_other_url}")
    print(f"✗ 缺少网址: {len(drugs_without_url)}")
    print(f"覆盖率: {(drugs_with_url / total_drugs * 100):.1f}%")
    
    # 打印缺少网址的药品
    if drugs_without_url:
        print(f"\n【缺少网址的药品】({len(drugs_without_url)}个)")
        print("-" * 80)
        for drug in drugs_without_url[:50]:  # 只显示前50个
            print(f"ID {drug['id']:4d}: {drug['name'][:30]:30s} - {drug['reason']}")
        
        if len(drugs_without_url) > 50:
            print(f"\n... 还有 {len(drugs_without_url) - 50} 个药品缺少网址")
    
    # 保存报告
    report_file = PROJECT_DIR / 'output' / 'drug_url_check_report.txt'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("药品网址检查报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"总药品数: {total_drugs}\n")
        f.write(f"有湖南药事服务网网址: {drugs_with_hnysfww_url}\n")
        f.write(f"有其他网址: {drugs_with_other_url}\n")
        f.write(f"缺少网址: {len(drugs_without_url)}\n")
        f.write(f"覆盖率: {(drugs_with_url / total_drugs * 100):.1f}%\n\n")
        
        if drugs_without_url:
            f.write(f"【缺少网址的药品列表】({len(drugs_without_url)}个)\n")
            f.write("-" * 80 + "\n")
            for drug in drugs_without_url:
                f.write(f"ID {drug['id']:4d}: {drug['name']} - {drug['reason']}\n")
    
    print(f"\n✓ 报告已保存: {report_file}")
    
    return drugs_without_url

if __name__ == '__main__':
    check_drug_urls()
