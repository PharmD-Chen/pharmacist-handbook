#!/usr/bin/env python3
"""
整理和清理 output 文件夹中的临时性文件
"""

import shutil
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/output')
ARCHIVE_DIR = Path('/Users/chenheng/Projects_AI/Project_Pharmacist/output/archive')

# 定义文件分类
CORE_FILES = [
    '药品手册内容和网址检查报告.md',  # 最新的完整检查报告
]

TEMP_FILES = [
    'drug_url_check_report.txt',           # 旧的网址检查报告
    'manual_completeness_report.txt',      # 旧的手册完整性报告
    'matched_urls_from_doc.txt',           # 临时匹配结果
    'comprehensive_quality_report.json',   # 旧的质量报告
    '质量分析报告_2026-03-21.md',          # 旧的质量分析
    '仍内容空缺的药品列表_20260321.md',     # 旧的空缺列表
    '仍缺少网址的药品清单.md',              # 旧的清单
    '仍缺少网址的药品清单_已更新.md',        # 中间版本
    '需要补充网址的中成药列表.md',          # 旧的中成药列表
    '中成药更新完成报告.md',                # 旧的更新报告
]

CURRENT_FILES = [
    '仍缺少网址的药品清单_最新.md',          # 当前最新清单
]

def main():
    print('=' * 80)
    print('整理 output 文件夹')
    print('=' * 80)
    print()

    # 创建归档目录
    ARCHIVE_DIR.mkdir(exist_ok=True)
    print(f'📁 归档目录: {ARCHIVE_DIR}')
    print()

    # 统计
    moved_count = 0
    deleted_count = 0
    kept_count = 0

    # 处理临时文件 - 移动到归档
    print('🗂️  移动临时文件到归档目录...')
    for filename in TEMP_FILES:
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            dest_path = ARCHIVE_DIR / filename
            shutil.move(str(file_path), str(dest_path))
            print(f'  移动: {filename}')
            moved_count += 1
    print()

    # 处理当前文件 - 保留
    print('📌 保留当前文件...')
    for filename in CURRENT_FILES:
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            print(f'  保留: {filename}')
            kept_count += 1
    print()

    # 处理核心文件 - 保留
    print('⭐ 保留核心报告...')
    for filename in CORE_FILES:
        file_path = OUTPUT_DIR / filename
        if file_path.exists():
            print(f'  保留: {filename}')
            kept_count += 1
    print()

    # 列出剩余文件
    print('📋 整理后剩余文件:')
    remaining_files = list(OUTPUT_DIR.glob('*'))
    for f in sorted(remaining_files):
        if f.is_file():
            print(f'  - {f.name}')
    print()

    print('=' * 80)
    print('整理完成!')
    print(f'  - 归档文件: {moved_count}个')
    print(f'  - 保留文件: {kept_count}个')
    print(f'  - 总计: {moved_count + kept_count}个')
    print('=' * 80)

if __name__ == '__main__':
    main()
