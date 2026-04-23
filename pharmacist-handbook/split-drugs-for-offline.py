#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将药品数据分割成多个小文件，用于单机版优化加载
"""

import json
import os

def split_drugs():
    # 读取主数据文件
    with open('data/drugs/drugs.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取JSON数据
    import re
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    if not match:
        print("无法解析数据")
        return
    
    drugs = json.loads(match.group(1))
    print(f"总药品数: {len(drugs)}")
    
    # 创建离线数据目录
    offline_dir = 'data/offline'
    os.makedirs(offline_dir, exist_ok=True)
    
    # 创建索引文件（只包含基本信息）
    drug_index = []
    for drug in drugs:
        drug_index.append({
            'id': drug['id'],
            'name': drug['name'],
            'full_name': drug.get('full_name', ''),
            'dosage_form': drug.get('dosage_form', ''),
            'types': drug.get('types', []),
            'pinyin': drug.get('pinyin', ''),
            'pinyin_initials': drug.get('pinyin_initials', ''),
            'manufacturers': drug.get('manufacturers', []),
            'specifications': drug.get('specifications', [])
        })
    
    # 保存索引文件
    with open(f'{offline_dir}/drug-index.json', 'w', encoding='utf-8') as f:
        json.dump(drug_index, f, ensure_ascii=False)
    
    print(f"索引文件已保存: {len(drug_index)} 条记录")
    
    # 按字母分组保存详细数据
    groups = {}
    for drug in drugs:
        first_char = drug.get('pinyin_initials', 'other')[0].upper() if drug.get('pinyin_initials') else 'other'
        if first_char not in groups:
            groups[first_char] = []
        groups[first_char].append(drug)
    
    # 保存分组数据
    for group_name, group_drugs in groups.items():
        with open(f'{offline_dir}/drugs-{group_name}.json', 'w', encoding='utf-8') as f:
            json.dump(group_drugs, f, ensure_ascii=False)
        print(f"分组 {group_name}: {len(group_drugs)} 条记录")
    
    # 创建加载脚本
    loader_js = '''// 离线版数据加载器
const DrugDataLoader = {
    index: null,
    cache: {},
    
    // 加载索引
    async loadIndex() {
        if (this.index) return this.index;
        
        try {
            const response = await fetch('data/offline/drug-index.json');
            this.index = await response.json();
            return this.index;
        } catch (error) {
            console.error('加载索引失败:', error);
            // 回退到主数据文件
            return typeof drugIndex !== 'undefined' ? drugIndex : [];
        }
    },
    
    // 根据首字母加载分组数据
    async loadGroup(initial) {
        const key = initial.toUpperCase();
        
        if (this.cache[key]) return this.cache[key];
        
        try {
            const response = await fetch(`data/offline/drugs-${key}.json`);
            const data = await response.json();
            this.cache[key] = data;
            return data;
        } catch (error) {
            console.error(`加载分组 ${key} 失败:`, error);
            return [];
        }
    },
    
    // 获取单个药品详情
    async getDrugDetail(drugId) {
        // 先查找索引
        if (!this.index) {
            await this.loadIndex();
        }
        
        const drugInfo = this.index.find(d => d.id === drugId);
        if (!drugInfo) return null;
        
        // 加载对应分组
        const initial = (drugInfo.pinyin_initials || 'other')[0].toUpperCase();
        const group = await this.loadGroup(initial);
        
        return group.find(d => d.id === drugId);
    },
    
    // 搜索药品
    async searchDrugs(query) {
        if (!this.index) {
            await this.loadIndex();
        }
        
        const lowerQuery = query.toLowerCase();
        return this.index.filter(drug => {
            return (drug.name && drug.name.toLowerCase().includes(lowerQuery)) ||
                   (drug.full_name && drug.full_name.toLowerCase().includes(lowerQuery)) ||
                   (drug.pinyin && drug.pinyin.toLowerCase().includes(lowerQuery));
        });
    }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DrugDataLoader };
}
'''
    
    with open(f'{offline_dir}/loader.js', 'w', encoding='utf-8') as f:
        f.write(loader_js)
    
    print("\n数据分割完成！")
    print(f"索引文件: {offline_dir}/drug-index.json")
    print(f"分组文件: {len(groups)} 个")
    print(f"加载脚本: {offline_dir}/loader.js")

if __name__ == '__main__':
    split_drugs()
