#!/usr/bin/env python3
"""更新药品网址汇总文件，添加所有816个药品的详细信息"""

import re

def parse_drugs_without_manual():
    """解析 drugs_without_manual.txt 文件"""
    drugs = []
    
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/pharmacist-handbook/data/drugs_without_manual.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析每一行
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('没有') or line.startswith('==='):
            continue
        
        # 匹配格式: 序号. 药品名 | 剂型 | 规格 网址
        match = re.match(r'^(\d+)\.\s+(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)(?:\s+(https://\S+))?$', line)
        if match:
            seq = match.group(1)
            name = match.group(2).strip()
            form = match.group(3).strip()
            spec = match.group(4).strip()
            url = match.group(5) if match.group(5) else ''
            
            drugs.append({
                'seq': seq,
                'name': name,
                'form': form,
                'spec': spec,
                'url': url
            })
    
    return drugs

def generate_markdown_table(drugs):
    """生成Markdown表格"""
    lines = []
    lines.append('| 序号 | 药品名称 | 剂型 | 规格 | 网址 |')
    lines.append('|------|----------|------|------|------|')
    
    for drug in drugs:
        url_display = f'[链接]({drug["url"]})' if drug['url'] else '待补充'
        lines.append(f"| {drug['seq']} | {drug['name']} | {drug['form']} | {drug['spec']} | {url_display} |")
    
    return '\n'.join(lines)

def main():
    # 解析药品列表
    print("正在解析药品列表...")
    drugs = parse_drugs_without_manual()
    print(f"共解析到 {len(drugs)} 个药品")
    
    # 统计有网址和没有网址的
    with_url = [d for d in drugs if d['url']]
    without_url = [d for d in drugs if not d['url']]
    print(f"有网址: {len(with_url)} 个")
    print(f"无网址: {len(without_url)} 个")
    
    # 生成完整表格
    print("正在生成Markdown表格...")
    table_content = generate_markdown_table(drugs)
    
    # 读取现有汇总文件
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md', 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # 找到第三部分的位置并替换
    section3_start = existing_content.find('## 三、暂无详细信息的药品')
    if section3_start == -1:
        print("错误：找不到第三部分")
        return
    
    # 构建新的第三部分
    new_section3 = f'''## 三、暂无详细信息的药品

以下{len(drugs)}个药品暂无详细信息，需要逐步补充：

### 完整药品列表

{table_content}

> **说明**：
> - 共 {len(drugs)} 个药品
> - 有网址: {len(with_url)} 个
> - 无网址: {len(without_url)} 个（需要人工查找补充）'''
    
    # 找到第三部分结束位置（下一个##或文件结束）
    next_section = existing_content.find('##', section3_start + 1)
    if next_section == -1:
        next_section = len(existing_content)
    
    # 替换内容
    new_content = existing_content[:section3_start] + new_section3 + existing_content[next_section:]
    
    # 更新统计信息
    stats_pattern = r'\| 暂无详细信息 \| \d+个 \| 📋 待完善 \|'
    new_stats = f'| 暂无详细信息 | {len(drugs)}个 | 📋 待完善 |'
    new_content = re.sub(stats_pattern, new_stats, new_content)
    
    total = 2 + 151 + len(drugs)  # 已补充 + 缺少说明书 + 暂无详细信息
    total_pattern = r'\| \*\*合计\*\* \| \*\*\d+个\*\* \| - \|'
    new_total = f'| **合计** | **{total}个** | - |'
    new_content = re.sub(total_pattern, new_total, new_content)
    
    # 保存文件
    with open('/Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✅ 更新完成！")
    print(f"文件已保存到: /Users/chenheng/Projects_AI/Project_Pharmacist/药品网址汇总.md")

if __name__ == '__main__':
    main()
