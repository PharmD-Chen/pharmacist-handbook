#!/usr/bin/env python3
"""整理根目录文件"""

import os
import shutil
from pathlib import Path

def main():
    root_dir = Path('/Users/chenheng/Projects_AI/Project_Pharmacist')
    
    # 创建文件夹
    scripts_dir = root_dir / 'scripts'
    reports_dir = root_dir / 'reports'
    backup_dir = root_dir / 'backup'
    
    scripts_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)
    backup_dir.mkdir(exist_ok=True)
    
    # 需要保留在根目录的核心文件
    core_files = {
        '药品网址汇总.md',
        '已补充药品网址.txt',
        'README.md',
    }
    
    # 需要移动到 scripts 的 Python 脚本
    script_patterns = [
        'add_*.py',
        'analyze_*.py',
        'batch_*.py',
        'check_*.py',
        'clean_*.py',
        'compress_*.py',
        'convert_*.py',
        'create_*.py',
        'extract_*.py',
        'fetch_*.py',
        'fix_*.py',
        'generate_*.py',
        'list_*.py',
        'organize_*.py',
        'read_*.py',
        'split_*.py',
        'update_*.py',
        'validate_*.py',
    ]
    
    # 需要移动到 reports 的报告文件
    report_patterns = [
        '*_report.txt',
        '*_list.txt',
        '第一批次*.txt',
        '第一批次*.json',
    ]
    
    moved_scripts = 0
    moved_reports = 0
    moved_backup = 0
    
    # 移动脚本文件
    for pattern in script_patterns:
        for file_path in root_dir.glob(pattern):
            if file_path.is_file() and file_path.name not in core_files:
                dest = scripts_dir / file_path.name
                shutil.move(str(file_path), str(dest))
                print(f"📜 已移动脚本: {file_path.name} -> scripts/")
                moved_scripts += 1
    
    # 移动报告文件
    for pattern in report_patterns:
        for file_path in root_dir.glob(pattern):
            if file_path.is_file() and file_path.name not in core_files:
                dest = reports_dir / file_path.name
                shutil.move(str(file_path), str(dest))
                print(f"📊 已移动报告: {file_path.name} -> reports/")
                moved_reports += 1
    
    print(f"\n✅ 整理完成！")
    print(f"📜 已移动 {moved_scripts} 个脚本到 scripts/")
    print(f"📊 已移动 {moved_reports} 个报告到 reports/")
    
    # 统计剩余文件
    remaining_files = [f.name for f in root_dir.iterdir() if f.is_file()]
    print(f"\n📁 根目录保留 {len(remaining_files)} 个文件:")
    for f in sorted(remaining_files):
        print(f"   - {f}")
    
    # 显示文件夹结构
    print(f"\n📂 新的文件夹结构:")
    print(f"   scripts/ - {len(list(scripts_dir.glob('*.py')))} 个Python脚本")
    print(f"   reports/ - {len(list(reports_dir.glob('*.txt'))) + len(list(reports_dir.glob('*.json')))} 个报告文件")
    print(f"   backup/ - 数据备份")
    print(f"   原始材料/ - 原始Excel等文件")
    print(f"   pharmacist-handbook/ - 前端网站")

if __name__ == '__main__':
    main()
