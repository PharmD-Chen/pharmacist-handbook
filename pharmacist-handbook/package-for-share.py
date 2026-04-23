#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包药品手册为共享版本
"""

import os
import shutil
import zipfile
from datetime import datetime

def package_for_share():
    # 创建打包目录
    package_dir = '药品手册2026版-共享版'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # 复制主HTML文件
    shutil.copy('offline-simple.html', f'{package_dir}/index.html')
    
    # 创建数据目录
    os.makedirs(f'{package_dir}/data/drugs', exist_ok=True)
    
    # 复制药品数据
    shutil.copy('data/drugs/drugs.js', f'{package_dir}/data/drugs/drugs.js')
    
    # 创建使用说明
    readme_content = '''上海市养志康复医院药品手册（2026版）
=====================================

使用说明：
1. 解压压缩包
2. 双击打开 index.html 文件
3. 使用浏览器（Chrome、Safari、Edge等）查看

功能特点：
- 支持药品名称搜索
- 支持拼音首字母搜索（如：aspl 搜索阿司匹林）
- 显示药品完整信息：适应症、用法用量、禁忌症、不良反应等

数据更新：2026年1月1日
药品数量：1054种

注意事项：
- 本手册为单机版，无需网络连接
- 建议使用最新版浏览器打开
- 如无法打开，请检查是否完整解压了所有文件

技术支持：医院药学部
'''
    
    with open(f'{package_dir}/使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 创建zip压缩包
    zip_filename = '上海市养志康复医院药品手册2026版.zip'
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # 获取文件大小
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    
    print(f"✅ 打包完成！")
    print(f"📦 压缩包名称: {zip_filename}")
    print(f"📊 文件大小: {zip_size:.2f} MB")
    print(f"📁 包含文件:")
    print(f"   - index.html (主页面)")
    print(f"   - data/drugs/drugs.js (药品数据)")
    print(f"   - 使用说明.txt")
    print(f"\n💡 使用方法:")
    print(f"   1. 解压 {zip_filename}")
    print(f"   2. 双击 index.html 打开")
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    
    return zip_filename

if __name__ == '__main__':
    package_for_share()
