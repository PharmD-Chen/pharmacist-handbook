#!/usr/bin/env python3
"""
药品数据分批加载优化脚本
将大的 drugs.js 分割成：
1. drugs_index.js - 轻量级索引（仅包含搜索所需字段）
2. drugs_detail_*.js - 分批的详细数据（每批约100个药品）
"""

import json
import re
import os

def extract_drug_data(js_file_path):
    """从 drugs.js 提取药品数据"""
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 drugIndex 数组
    match = re.search(r'const drugIndex = (\[.*?\]);', content, re.DOTALL)
    if not match:
        raise ValueError("无法找到 drugIndex 数据")
    
    # 解析 JSON
    json_str = match.group(1)
    drugs = json.loads(json_str)
    return drugs

def create_index_data(drugs):
    """创建轻量级索引数据"""
    index = []
    for drug in drugs:
        index_item = {
            "id": drug.get("id"),
            "name": drug.get("name"),
            "full_name": drug.get("full_name"),
            "chemical_name": drug.get("chemical_name"),
            "dosage_form": drug.get("dosage_form"),
            "types": drug.get("types", []),
            "manufacturers": drug.get("manufacturers", []),
            "pinyin": drug.get("pinyin", ""),
            "pinyin_initials": drug.get("pinyin_initials", ""),
            # 只保留第一个规格的基本信息用于显示
            "spec_summary": drug.get("specifications", [{}])[0].get("specification", "") if drug.get("specifications") else "",
            "manufacturer_summary": drug.get("manufacturers", [""])[0] if drug.get("manufacturers") else ""
        }
        index.append(index_item)
    return index

def split_detail_data(drugs, batch_size=100):
    """将详细数据分批"""
    batches = []
    for i in range(0, len(drugs), batch_size):
        batch = drugs[i:i + batch_size]
        batches.append(batch)
    return batches

def save_js_file(data, file_path, var_name):
    """保存为 JS 文件"""
    js_content = f"// 药品数据 - 生成于 2026-04-23\n"
    js_content += f"// 共 {len(data)} 条记录\n\n"
    js_content += f"const {var_name} = "
    js_content += json.dumps(data, ensure_ascii=False, indent=2)
    js_content += ";\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    return os.path.getsize(file_path)

def main():
    input_file = "docs/data/drugs/drugs.js"
    output_dir = "docs/data/drugs"
    
    print("=" * 60)
    print("药品数据分批加载优化")
    print("=" * 60)
    
    # 1. 读取原始数据
    print("\n1. 读取原始数据...")
    drugs = extract_drug_data(input_file)
    print(f"   共 {len(drugs)} 个药品")
    
    # 2. 创建索引文件
    print("\n2. 创建轻量级索引...")
    index_data = create_index_data(drugs)
    index_file = os.path.join(output_dir, "drugs_index.js")
    index_size = save_js_file(index_data, index_file, "drugIndex")
    print(f"   索引文件: {index_file}")
    print(f"   大小: {index_size / 1024:.1f} KB")
    
    # 3. 分批保存详细数据
    print("\n3. 分批保存详细数据...")
    batches = split_detail_data(drugs, batch_size=100)
    print(f"   分成 {len(batches)} 批，每批约 100 个药品")
    
    batch_files = []
    for i, batch in enumerate(batches):
        batch_file = os.path.join(output_dir, f"drugs_detail_{i+1}.js")
        batch_size = save_js_file(batch, batch_file, f"drugDetailBatch{i+1}")
        batch_files.append(batch_file)
        print(f"   批次 {i+1}: {len(batch)} 个药品, {batch_size / 1024:.1f} KB")
    
    # 4. 创建加载器文件
    print("\n4. 创建数据加载器...")
    loader_content = f"""// 药品数据加载器 - 分批加载
// 生成于 2026-04-23

// 药品索引（轻量级，优先加载）
let drugIndex = [];

// 已加载的详细数据缓存
const drugDetailCache = {{}};

// 批次映射表（药品ID -> 批次号）
const drugBatchMap = {{}};

// 初始化批次映射
function initBatchMap() {{
  const batchSize = 100;
  for (let i = 0; i < {len(drugs)}; i++) {{
    drugBatchMap[i + 1] = Math.floor(i / batchSize) + 1;
  }}
}}

// 加载索引
async function loadDrugIndex() {{
  try {{
    const response = await fetch('data/drugs/drugs_index.js');
    const text = await response.text();
    const match = text.match(/const drugIndex = (\\[.*?\\]);/s);
    if (match) {{
      drugIndex = JSON.parse(match[1]);
      console.log('✅ 药品索引加载完成:', drugIndex.length, '条');
      initBatchMap();
      return drugIndex;
    }}
  }} catch (e) {{
    console.error('❌ 加载药品索引失败:', e);
  }}
  return [];
}}

// 按需加载药品详情
async function loadDrugDetail(drugId) {{
  // 检查缓存
  if (drugDetailCache[drugId]) {{
    return drugDetailCache[drugId];
  }}
  
  // 确定批次
  const batchNum = drugBatchMap[drugId];
  if (!batchNum) {{
    console.error('未找到药品批次:', drugId);
    return null;
  }}
  
  try {{
    const response = await fetch(`data/drugs/drugs_detail_${{batchNum}}.js`);
    const text = await response.text();
    const match = text.match(/const drugDetailBatch\\d+ = (\\[.*?\\]);/s);
    if (match) {{
      const batch = JSON.parse(match[1]);
      // 缓存整个批次
      batch.forEach(drug => {{
        drugDetailCache[drug.id] = drug;
      }});
      return drugDetailCache[drugId];
    }}
  }} catch (e) {{
    console.error('❌ 加载药品详情失败:', drugId, e);
  }}
  return null;
}}

// 预加载相邻批次（优化体验）
async function preloadAdjacentBatches(currentBatch) {{
  const adjacent = [currentBatch - 1, currentBatch + 1];
  for (const batchNum of adjacent) {{
    if (batchNum > 0 && batchNum <= {len(batches)} && !window[`drugDetailBatch${{batchNum}}`]) {{
      try {{
        const script = document.createElement('script');
        script.src = `data/drugs/drugs_detail_${{batchNum}}.js`;
        script.async = true;
        document.head.appendChild(script);
      }} catch (e) {{
        console.log('预加载批次失败:', batchNum);
      }}
    }}
  }}
}}

// 导出接口
window.DrugDataLoader = {{
  loadIndex: loadDrugIndex,
  loadDetail: loadDrugDetail,
  preloadAdjacent: preloadAdjacentBatches,
  get index() {{ return drugIndex; }},
  get cache() {{ return drugDetailCache; }}
}};
"""
    
    loader_file = os.path.join(output_dir, "drugs_loader.js")
    with open(loader_file, 'w', encoding='utf-8') as f:
        f.write(loader_content)
    print(f"   加载器文件: {loader_file}")
    
    # 5. 统计信息
    print("\n" + "=" * 60)
    print("优化完成!")
    print("=" * 60)
    print(f"原始文件大小: 8.2 MB")
    print(f"索引文件大小: {index_size / 1024:.1f} KB")
    print(f"分批文件数量: {len(batches)} 个")
    print(f"平均每批大小: ~{sum(os.path.getsize(f) for f in batch_files) / len(batch_files) / 1024:.1f} KB")
    print("\n加载策略:")
    print("1. 首次加载: 仅加载索引 (~100KB)")
    print("2. 搜索显示: 使用索引数据")
    print("3. 查看详情: 按需加载对应批次")
    print("4. 预加载: 自动加载相邻批次")

if __name__ == "__main__":
    main()
