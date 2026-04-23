# Scripts 文件夹说明

本文件夹存放所有Python脚本，按照功能分类存放在不同子文件夹中。

## 文件夹结构

```
scripts/
├── batch/          # 批量处理脚本 (19个)
├── check/          # 检查脚本 (11个)
├── fetch/          # 获取数据脚本 (10个)
├── fix/            # 修复脚本 (7个)
├── update/         # 更新脚本 (21个)
├── verify/         # 验证脚本 (4个)
├── utils/          # 工具脚本 (26个)
├── archive/        # 归档的旧版本 (8个)
└── README.md       # 本说明文件
```

## 统计概览

总计：**106个Python脚本**

## 各文件夹详细内容

### 1. batch/ - 批量处理脚本 (19个)

用于批量处理药品数据的脚本。

- `batch_add_summary.py` - 批量添加摘要
- `batch_check_and_update.py` - 批量检查并更新
- `batch_check_detailed.py` - 批量详细检查
- `batch_check_drugs.py` - 批量检查药品
- `batch_fetch_and_update.py` - 批量获取并更新
- `batch_fetch_drug_manual.py` - 批量获取药品手册
- `batch_fetch_drug_manuals_v2.py` - 批量获取药品手册v2（最新版）
- `batch_fetch_missing_manuals.py` - 批量获取缺失手册
- `batch_fetch_tablet_v2.py` - 批量获取片剂v2（最新版）
- `batch_fill_manual.py` - 批量填充手册
- `batch_process_drugs.py` - 批量处理药品
- `batch_update_antibiotics.py` - 批量更新抗生素
- `batch_update_antibiotics2.py` - 批量更新抗生素2
- `batch_update_antibiotics3.py` - 批量更新抗生素3
- `batch_update_antibiotics4.py` - 批量更新抗生素4
- `batch_update_antibiotics5.py` - 批量更新抗生素5
- `batch_update_antibiotics6.py` - 批量更新抗生素6（最新版）
- `batch_update_drug_info.py` - 批量更新药品信息
- `batch_verify_and_update.py` - 批量验证并更新

### 2. check/ - 检查脚本 (11个)

用于检查药品数据质量和状态的脚本。

- `check_12_drugs.py` - 检查12个药品
- `check_antibiotic_drugs.py` - 检查抗生素药品
- `check_drug_data_quality.py` - 检查药品数据质量
- `check_drugs_status.py` - 检查药品状态
- `check_drugs_with_empty_manual.py` - 检查手册为空的药品
- `check_duplicate_drugs.py` - 检查重复药品
- `check_excel_sheets.py` - 检查Excel表格
- `check_infusion_drugs.py` - 检查输液药品
- `check_insulin_drugs.py` - 检查胰岛素药品
- `check_remaining.py` - 检查剩余药品
- `check_tablet_drugs_status.py` - 检查片剂药品状态

### 3. fetch/ - 获取数据脚本 (10个)

用于从网站获取药品数据的脚本。

- `fetch_antibiotic_drugs.py` - 获取抗生素药品
- `fetch_drug_details.py` - 获取药品详情
- `fetch_infusion_drugs.py` - 获取输液药品
- `fetch_insulin_drugs.py` - 获取胰岛素药品
- `fetch_phentolamine.py` - 获取酚妥拉明
- `fetch_phentolamine2.py` - 获取酚妥拉明2
- `fetch_phentolamine3.py` - 获取酚妥拉明3（最新版）
- `fetch_tigecycline.py` - 获取替加环素
- `fetch_two_drugs.py` - 获取两个药品
- `fetch_wrong_source_drugs.py` - 获取来源错误的药品

### 4. fix/ - 修复脚本 (7个)

用于修复药品数据问题的脚本。

- `fix_all_batch1.py` - 修复第一批所有
- `fix_antibiotic_urls.py` - 修复抗生素网址
- `fix_batch_1_drugs.py` - 修复批次1药品
- `fix_drug_manual_concise.py` - 修复药品手册精简版
- `fix_index_outpatient.py` - 修复索引门诊
- `fix_interactions_field.py` - 修复相互作用字段
- `fix_syntax_errors.py` - 修复语法错误

### 5. update/ - 更新脚本 (21个)

用于更新特定药品数据的脚本。

- `update_10_tcm_manual.py` - 更新10个中成药手册
- `update_11_drugs_manual.py` - 更新11个药品手册
- `update_aspirin.py` - 更新阿司匹林
- `update_benidipine.py` - 更新贝尼地平
- `update_cefoperazone_nacl.py` - 更新头孢哌酮钠
- `update_chinese_medicines.py` - 更新中成药
- `update_drug_manual.py` - 更新药品手册
- `update_drug_purchase_type.py` - 更新药品采购类型
- `update_edoxaban.py` - 更新艾多沙班
- `update_fluorouracil.py` - 更新氟尿嘧啶
- `update_index_locations.py` - 更新索引位置
- `update_index_outpatient.py` - 更新索引门诊
- `update_index_with_specs.py` - 更新索引规格
- `update_injection_drugs.py` - 更新注射药品
- `update_insulin_degludec.py` - 更新胰岛素德谷
- `update_interactions.py` - 更新相互作用
- `update_olmesartan_amlodipine.py` - 更新奥美沙坦氨氯地平
- `update_purchase_type.py` - 更新采购类型
- `update_summary.py` - 更新摘要
- `update_tigecycline_interactions.py` - 更新替加环素相互作用
- `update_urls.py` - 更新网址

### 6. verify/ - 验证脚本 (4个)

用于验证药品数据来源的脚本。

- `verify_antibiotic_info.py` - 验证抗生素信息
- `verify_antibiotic_sources.py` - 验证抗生素来源
- `verify_drug_sources.py` - 验证药品来源
- `verify_source_details.py` - 验证来源详情

### 7. utils/ - 工具脚本 (26个)

各类辅助工具脚本。

**添加数据类:**
- `add_anaprazole.py` - 添加安奈拉唑
- `add_location_codes.py` - 添加位置代码
- `add_location_to_specs.py` - 添加位置到规格
- `add_status_field.py` - 添加状态字段
- `add_summary_field.py` - 添加摘要字段

**分析类:**
- `analyze_drug_manuals.py` - 分析药品手册
- `analyze_drugs.py` - 分析药品数据

**清理类:**
- `clean_drug_names.py` - 清理药品名称

**压缩类:**
- `compress_cephalosporin_v2.py` - 压缩头孢菌素v2（最新版）

**转换类:**
- `convert_excel_to_json.py` - Excel转JSON
- `convert_to_separate_entries.py` - 转换为独立条目

**创建类:**
- `create_next_batches.py` - 创建下一批次

**去重类:**
- `deduplicate_drugs.py` - 药品去重

**提取类:**
- `extract_drugs_with_url.py` - 提取有网址的药品

**生成类:**
- `generate_missing_drugs_list.py` - 生成缺失药品列表
- `generate_summary_v2.py` - 生成摘要v2（最新版）

**导入类:**
- `import_outpatient_location.py` - 导入门诊位置

**整合类:**
- `integrate_and_update_drugs.py` - 整合并更新药品

**列表类:**
- `list_drugs_without_manual.py` - 列出无手册药品

**手动更新类:**
- `manual_update_11_drugs.py` - 手动更新11个药品
- `manual_update_drugs.py` - 手动更新药品

**处理类:**
- `process_tablet_drugs.py` - 处理片剂药品

**读取类:**
- `read_excel_temp_purchase.py` - 读取Excel临时采购
- `read_location_excel.py` - 读取位置Excel

**分割类:**
- `split_drugs_to_json.py` - 分割药品到JSON

**验证类:**
- `validate_drug_info.py` - 验证药品信息

### 8. archive/ - 归档的旧版本 (8个)

已归档的旧版本脚本，保留以备参考。

- `batch_fetch_drug_manuals.py` - 旧版批量获取药品手册
- `batch_fetch_tablet_drugs.py` - 旧版批量获取片剂药品
- `compress_cephalosporin.py` - 旧版压缩头孢菌素
- `fix_cephalosporin_blackbox.py` - 旧版修复头孢菌素黑框
- `fix_cephalosporin_data.py` - 旧版修复头孢菌素数据
- `generate_summary.py` - 旧版生成摘要
- `organize_data_folder.py` - 旧版整理数据文件夹
- `organize_root_folder.py` - 旧版整理根文件夹

## 使用建议

### 查找脚本

根据功能需求到对应文件夹查找：
- 需要批量处理 → `batch/`
- 需要检查数据 → `check/`
- 需要获取网站数据 → `fetch/`
- 需要修复问题 → `fix/`
- 需要更新特定药品 → `update/`
- 需要验证来源 → `verify/`
- 其他工具 → `utils/`

### 版本管理

- 最新版本直接存放在功能文件夹中
- 旧版本归档在 `archive/` 文件夹
- 带有 `v2`, `v3` 或数字后缀的是迭代版本

### 可合并的相似脚本

以下脚本功能相似，可考虑合并：

1. **fetch_phentolamine 系列** (fetch/)
   - `fetch_phentolamine.py`
   - `fetch_phentolamine2.py`
   - `fetch_phentolamine3.py`（最新版）

2. **batch_update_antibiotics 系列** (batch/)
   - `batch_update_antibiotics.py` 到 `batch_update_antibiotics6.py`
   - 建议保留 `batch_update_antibiotics6.py`（最新版）

## 命名规范

所有脚本遵循以下命名规范：
- 使用小写字母
- 使用下划线 `_` 分隔单词
- 以功能动词开头（add, check, fetch, fix, update, verify等）
- 描述清晰具体
- 版本号使用 `v2`, `v3` 或数字后缀

## 维护记录

- **2026-03-21**: 重新整理scripts文件夹，按功能分类存放
