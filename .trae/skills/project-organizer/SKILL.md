---
name: "project-organizer"
description: "整理药品手册项目文件结构，包括分类Python脚本、报告文件和数据文件。Invoke when user asks to organize project files or clean up the directory structure."
---

# 项目文件整理规则

## 目标
整理 `/Users/chenheng/Projects_AI/Project_Pharmacist` 项目的文件结构，使其清晰有序。

## 文件夹结构规范

### 1. 根目录保留文件
只保留核心数据文件：
- `药品网址汇总.md` - 主数据源
- `已补充药品网址.txt` - 补充数据
- `README.md` - 项目说明（如有）

### 2. scripts/ 文件夹
存放所有 Python 脚本：
- `add_*.py` - 添加数据脚本
- `analyze_*.py` - 分析脚本
- `batch_*.py` - 批量处理脚本
- `check_*.py` - 检查脚本
- `clean_*.py` - 清理脚本
- `compress_*.py` - 压缩脚本
- `convert_*.py` - 转换脚本
- `create_*.py` - 创建脚本
- `extract_*.py` - 提取脚本
- `fetch_*.py` - 获取数据脚本
- `fix_*.py` - 修复脚本
- `generate_*.py` - 生成脚本
- `list_*.py` - 列表脚本
- `organize_*.py` - 整理脚本
- `read_*.py` - 读取脚本
- `split_*.py` - 分割脚本
- `update_*.py` - 更新脚本
- `validate_*.py` - 验证脚本

### 3. reports/ 文件夹
存放报告和日志文件：
- `*_report.txt` - 分析报告
- `*_list.txt` - 列表文件
- `第一批次*.txt` - 批次报告
- `第一批次*.json` - 批次数据

### 4. backup/ 文件夹
存放数据备份：
- 旧的数据文件
- 中间生成的文件
- 不再使用的备份

### 5. 原始材料/ 文件夹
存放原始输入文件：
- Excel 文件
- PDF 文件
- 其他原始文档

### 6. pharmacist-handbook/ 文件夹
前端网站目录：
- `index.html` - 主页面
- `data/` - 数据目录
  - `drugs/` - 药品 JSON 文件
    - `index.json` - 药品索引
    - `[1-1032].json` - 各药品数据
  - `backup/` - 中间文件备份

## 执行步骤

1. 创建必要的文件夹（如果不存在）
2. 将 Python 脚本移动到 scripts/
3. 将报告文件移动到 reports/
4. 将中间文件移动到 backup/
5. 保留核心数据文件在根目录
6. 统计并报告整理结果

## 注意事项

- 移动前检查文件是否已在目标位置
- 保留系统文件（如 .DS_Store）不动
- 整理完成后显示新的文件夹结构
- 报告移动的文件数量和保留的文件数量
