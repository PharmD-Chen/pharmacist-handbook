# GitHub Pages 部署指南

## 部署步骤

### 1. 推送代码到 GitHub

```bash
# 确保您在项目根目录
cd /Users/chenheng/Projects_AI/Project_Pharmacist

# 添加 docs 目录到 git
git add docs/
git commit -m "部署药品手册到 GitHub Pages"
git push origin main
```

### 2. 启用 GitHub Pages

1. 打开您的 GitHub 仓库页面
2. 点击 **Settings**（设置）
3. 在左侧菜单找到 **Pages**
4. **Source** 选择 **Deploy from a branch**
5. **Branch** 选择 **main**，文件夹选择 **/docs**
6. 点击 **Save**

### 3. 访问网站

等待几分钟（通常 1-5 分钟），然后访问：

```
https://您的用户名.github.io/仓库名/
```

例如：`https://chenheng.github.io/Project_Pharmacist/`

## 文件结构

```
docs/                       # GitHub Pages 源目录
├── index.html              # 登录页面（入口）
├── main.html               # 药师主页面
├── drugs.html              # 药品手册
├── workflow-guide.html     # 岗位手册导航
├── medication-damage-report.html  # 药品报损登记
├── js/
│   └── auth.js             # 认证脚本
├── data/drugs/
│   └── drugs.js            # 药品数据
├── workflow/               # 岗位流程文件
└── README.md               # 说明文档
```

## 默认登录账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| pharmacist | 123456 | 药师 |
| admin | admin123 | 管理员 |

## 注意事项

1. **数据存储**：药品报损记录保存在浏览器 LocalStorage 中，不同设备数据不互通
2. **更新部署**：修改代码后重新推送，`docs` 目录会自动更新
3. **访问地址**：如果仓库是私有的，GitHub Pages 也是私有的（需要登录才能访问）

## 自定义域名（可选）

如需使用自定义域名：
1. 在 `docs` 目录下创建 `CNAME` 文件
2. 文件内容为您的域名，例如：`yaodian.example.com`
3. 在域名 DNS 设置中添加 CNAME 记录指向 `用户名.github.io`
