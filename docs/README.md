# 上海市养志康复医院药品手册 - 网络端部署包

## 部署说明

### 文件结构

```
deploy-web/
├── index.html              # 药师登录页面（入口）
├── main.html               # 药师主页面
├── drugs.html              # 药品手册
├── workflow-guide.html     # 岗位手册导航
├── medication-damage-report.html  # 药品报损登记
├── css/                    # 样式文件目录（预留）
├── js/
│   └── auth.js             # 认证脚本
├── data/
│   └── drugs/
│       └── drugs.js        # 药品数据
├── workflow/               # 岗位流程文件
│   ├── clinical-consultation.html
│   ├── clinical-review.html
│   ├── inpatient-dispensing.html
│   ├── inpatient-scan.html
│   ├── outpatient-dispensing.html
│   ├── outpatient-review.html
│   ├── storage-inventory.html
│   └── storage-management.html
└── assets/                 # 资源文件目录（预留）
```

### 部署步骤

1. **上传文件**
   - 将 `deploy-web` 目录下的所有文件上传到 Web 服务器
   - 确保目录结构保持不变

2. **配置服务器**
   - 确保服务器支持静态 HTML 文件访问
   - 推荐配置默认首页为 `index.html`

3. **访问地址**
   - 登录页面：`http://您的域名/index.html`
   - 默认账号：
     - 用户名：`pharmacist`，密码：`123456`
     - 用户名：`admin`，密码：`admin123`

### 功能模块

1. **药品手册** - 查询药品详细信息、用法用量、禁忌症等
2. **岗位手册** - 包含以下子模块：
   - 门诊药房（发药、处方审核、调配、用药指导、退药处理）
   - 住院药房（口服药摆药/核对、针剂摆药、扫码发药、退药处理、药品拆零）
   - 药库管理（入库验收、库存管理）
   - 临床药学（医嘱点评、用药咨询）
   - 质量控制（药品报损登记、质量检查、差错处理、不良反应监测）
3. **药品报损登记** - 药品退药报损录入、查询与导出

### 注意事项

- 本系统为纯前端实现，数据存储在浏览器 LocalStorage 中
- 药品报损记录仅保存在当前浏览器，换设备需重新录入
- 建议定期导出报损记录备份

### 技术支持

医院药学部
数据更新于：2026年1月1日
