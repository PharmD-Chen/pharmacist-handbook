# 药品手册 - GitHub Pages 部署指南

## 📋 部署前准备

### 1. 文件清单
确保以下文件已准备就绪：

```
pharmacist-handbook/
├── index.html          # 主页面（已集成权限控制）
├── login.html          # 登录页面
├── auth.js             # 认证和权限控制模块
├── data/
│   └── drugs/
│       ├── drugs.js    # 药品数据（已生成）
│       └── index.json  # 药品索引
└── DEPLOY.md           # 本部署指南
```

### 2. 用户账号配置

默认用户账号（**部署后请立即修改密码**）：

| 用户类型 | 用户名 | 密码 | 权限 |
|---------|--------|------|------|
| 访客 | visitor | visitor2024 | 仅查看基础信息 |
| 护士 | nurse | nurse2024 | 药品信息 + 用法用量 |
| 医生 | doctor | doctor2024 | 完整药品手册 |
| 药师 | pharmacist | pharma2024 | 全部内容 + 岗位手册 |
| 管理员 | admin | admin2024 | 所有功能 |

**⚠️ 安全提示**：
- 部署后请立即修改默认密码
- 建议定期更换密码
- 不要将密码存储在代码仓库中

---

## 🚀 GitHub Pages 部署步骤

### 步骤 1：创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名称：`pharmacist-handbook`（或其他名称）
4. 设置为 **Public** 或 **Private**
5. 点击 "Create repository"

### 步骤 2：上传文件

**方式 A：通过 Git 命令行**

```bash
# 进入项目目录
cd pharmacist-handbook

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Pharmacist Handbook with auth"

# 关联远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/pharmacist-handbook.git

# 推送
git push -u origin main
```

**方式 B：通过 GitHub 网页上传**

1. 在仓库页面点击 "uploading an existing file"
2. 拖拽或选择以下文件上传：
   - `index.html`
   - `login.html`
   - `auth.js`
   - `data/drugs/drugs.js`
   - `data/drugs/index.json`
3. 点击 "Commit changes"

### 步骤 3：启用 GitHub Pages

1. 进入仓库的 **Settings** 页面
2. 左侧菜单选择 **Pages**
3. **Source** 部分选择：
   - Branch: `main` 或 `master`
   - Folder: `/ (root)`
4. 点击 **Save**
5. 等待几分钟，页面会显示访问地址：`https://YOUR_USERNAME.github.io/pharmacist-handbook/`

### 步骤 4：验证部署

1. 访问 `https://YOUR_USERNAME.github.io/pharmacist-handbook/login.html`
2. 使用测试账号登录
3. 验证不同用户类型的权限是否正确

---

## 🔐 修改默认密码

### 方法 1：直接修改 auth.js（推荐）

编辑 `auth.js` 文件中的 `USER_CONFIG` 对象：

```javascript
const USER_CONFIG = {
    visitor: {
        password: '你的新密码',  // 修改这里
        permissions: ['basic_info'],
        menuItems: ['drug_search']
    },
    nurse: {
        password: '你的新密码',  // 修改这里
        // ...
    },
    // ...
};
```

修改后重新提交到 GitHub。

### 方法 2：使用环境变量（高级）

如果需要更安全的方案，可以考虑使用：
- GitHub Secrets + GitHub Actions
- 外部认证服务（如 Auth0）
- 后端服务器验证

---

## 👥 用户权限说明

### 访客（Visitor）
- **可见内容**：药品名称、规格、厂家、价格
- **隐藏内容**：用法用量、禁忌症、不良反应、相互作用等
- **适用场景**：公众查询、患者自查

### 护士（Nurse）
- **可见内容**：基础信息 + 用法用量、溶媒选择、注意事项
- **隐藏内容**：药物相互作用、药代动力学、岗位手册
- **适用场景**：临床给药、药品核对

### 医生（Doctor）
- **可见内容**：完整药品手册（除岗位手册外）
- **隐藏内容**：岗位手册
- **适用场景**：处方开具、用药决策

### 药师（Pharmacist）
- **可见内容**：所有内容，包括岗位手册
- **适用场景**：药学服务、用药指导、处方审核

### 管理员（Admin）
- **可见内容**：所有功能
- **适用场景**：系统管理、用户管理

---

## 🛠️ 自定义配置

### 添加新用户

在 `auth.js` 的 `USER_CONFIG` 中添加：

```javascript
const USER_CONFIG = {
    // ... 现有用户
    
    newuser: {
        password: 'password123',
        permissions: ['basic_info', 'dosage_info'],
        menuItems: ['drug_search', 'dosage_guide']
    }
};
```

然后在 `PERMISSIONS` 中定义权限：

```javascript
const PERMISSIONS = {
    // ... 现有权限
    
    newuser: {
        name: '新用户',
        level: 3,
        canView: ['basic_info', 'dosage_info'],
        canAccess: ['home', 'drug_search'],
        hiddenSections: ['interactions', 'pharmacokinetics']
    }
};
```

### 修改权限范围

编辑 `PERMISSIONS` 对象中的对应用户类型：

```javascript
pharmacist: {
    name: '药师',
    level: 4,
    canView: ['all'],  // 可以查看所有
    canAccess: ['home', 'drug_search', 'favorites', 'history', 'workflow'],
    hiddenSections: []  // 没有隐藏内容
}
```

---

## 📱 移动端优化

本项目已针对移动端进行优化：
- 响应式设计，适配各种屏幕尺寸
- 触摸友好的交互
- 快速搜索和导航
- 离线缓存支持（PWA）

---

## 🔧 故障排除

### 问题 1：页面显示 404

**原因**：GitHub Pages 未正确配置或文件路径错误

**解决**：
1. 检查 Settings → Pages 中的分支设置
2. 确保文件已上传到正确的分支
3. 等待 2-5 分钟后刷新

### 问题 2：无法登录

**原因**：auth.js 未正确加载或密码错误

**解决**：
1. 检查浏览器控制台是否有 JavaScript 错误
2. 确认 auth.js 文件已上传
3. 检查密码是否正确（区分大小写）

### 问题 3：数据不显示

**原因**：drugs.js 文件过大或加载失败

**解决**：
1. 检查 drugs.js 是否已上传
2. 检查文件大小（约 8MB）
3. 考虑使用 CDN 或分片加载

### 问题 4：权限控制不生效

**原因**：JavaScript 未正确执行

**解决**：
1. 清除浏览器缓存
2. 检查控制台错误信息
3. 确保 auth.js 在 index.html 中正确引入

---

## 📝 更新数据

当药品数据更新时：

1. 运行数据生成脚本：
   ```bash
   python3 generate_drugs_js.py
   ```

2. 提交更新到 GitHub：
   ```bash
   git add data/drugs/drugs.js
   git commit -m "Update drug data"
   git push
   ```

3. 等待 GitHub Pages 自动部署（约 1-2 分钟）

---

## 🔒 安全建议

1. **定期更换密码**：建议每 3 个月更换一次
2. **使用强密码**：包含大小写字母、数字、特殊字符
3. **限制访问**：如数据敏感，建议将仓库设为 Private
4. **启用 HTTPS**：GitHub Pages 默认启用 HTTPS
5. **备份数据**：定期备份药品数据和用户配置

---

## 📞 技术支持

如有问题，请：
1. 检查浏览器控制台错误信息
2. 查看 GitHub Pages 文档：https://docs.github.com/en/pages
3. 联系系统管理员

---

**部署日期**：2026-03-23  
**版本**：v1.0.0  
**作者**：药品手册开发团队
