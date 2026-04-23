#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复药品数据中的药代动力学字段
将药理作用（作用机制）与药代动力学参数区分开
"""

import json
import re

def fix_pharmacokinetics():
    # 读取药品数据
    with open('pharmacist-handbook/data/drugs/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取JSON数据
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("无法解析数据")
        return
    
    drugs = json.loads(match.group(1))
    print(f"总药品数: {len(drugs)}")
    
    # 药代动力学关键词
    pk_keywords = [
        '半衰期', 't1/2', 't½', '消除半衰期',
        '峰浓度', 'Cmax', 'C-max', '最大血药浓度',
        '达峰时间', 'Tmax', 'T-max', '达峰时间',
        '蛋白结合率', '血浆蛋白结合', '结合率',
        '生物利用度', '绝对生物利用度', '相对生物利用度',
        '分布容积', '表观分布容积', 'Vd',
        '清除率', 'CL', '肾清除率', '肝清除率',
        '代谢', '肝脏代谢', 'CYP', 'P450', '酶代谢',
        '排泄', '肾脏排泄', '胆汁排泄', '粪便排泄', '尿液排泄',
        '血药浓度', '血浆浓度', '血清浓度',
        'AUC', '曲线下面积', '药时曲线下面积',
        '稳态血药浓度', 'Css', '稳态浓度',
        '吸收', '吸收率', '吸收速度',
        '分布', '组织分布', '血脑屏障', '胎盘屏障'
    ]
    
    # 药理作用关键词（需要从pharmacokinetics中移除的）
    pd_keywords = [
        '作用机制', '机制', '抑制', '激动', '拮抗', '阻断',
        '受体', '酶', '合成', '释放', '促进', '减少',
        '血小板', '血栓素', '前列腺素', '抗炎', '镇痛',
        '抗菌', '杀菌', '抑菌', '抗病毒', '抗肿瘤',
        '降压', '降糖', '降脂', '抗凝', '抗血小板',
        '支气管扩张', '血管收缩', '血管舒张',
        '中枢', '外周', '神经', '肌肉'
    ]
    
    fixed_count = 0
    
    for drug in drugs:
        manual = drug.get('manual', {})
        pk_content = manual.get('pharmacokinetics', '')
        full_pk_content = manual.get('full_pharmacokinetics', '')
        
        if not pk_content:
            continue
        
        # 检查内容是否主要是药理作用而非药代动力学
        pk_score = sum(1 for kw in pk_keywords if kw in pk_content)
        pd_score = sum(1 for kw in pd_keywords if kw in pk_content)
        
        # 如果药理作用关键词远多于药代动力学关键词，说明内容被错误归类
        if pd_score > pk_score * 2 and pk_score < 3:
            print(f"\n发现错误归类: {drug['name']}")
            print(f"  当前内容: {pk_content[:100]}...")
            print(f"  药代动力学关键词: {pk_score}, 药理作用关键词: {pd_score}")
            
            # 将内容移到药理作用字段（如果不存在）
            if 'pharmacodynamics' not in manual:
                manual['pharmacodynamics'] = pk_content
            if 'full_pharmacodynamics' not in manual and full_pk_content:
                manual['full_pharmacodynamics'] = full_pk_content
            
            # 清空药代动力学字段（或设置为提示信息）
            manual['pharmacokinetics'] = '暂无药代动力学数据'
            if 'full_pharmacokinetics' in manual:
                manual['full_pharmacokinetics'] = '暂无药代动力学数据'
            
            fixed_count += 1
    
    print(f"\n共修复 {fixed_count} 个药品的数据归类")
    
    # 保存修复后的数据
    output = f'''// 药品手册数据 - 更新于 2026-04-17
// 共 {len(drugs)} 个药品
// 修复说明：区分了药理作用和药代动力学字段

const drugIndex = {json.dumps(drugs, ensure_ascii=False, indent=2)};

// 导出数据（用于Node.js环境）
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{ drugIndex }};
}}
'''
    
    # 备份原文件
    import shutil
    shutil.copy('pharmacist-handbook/data/drugs/drugs.js', 'pharmacist-handbook/data/drugs/drugs.js.bak')
    print("\n已备份原文件到 drugs.js.bak")
    
    # 保存新文件
    with open('pharmacist-handbook/data/drugs/drugs.js', 'w', encoding='utf-8') as f:
        f.write(output)
    
    print("已保存修复后的数据到 drugs.js")

if __name__ == '__main__':
    fix_pharmacokinetics()
