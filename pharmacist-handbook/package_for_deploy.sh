#!/bin/bash

# 药品手册 GitHub Pages 部署打包脚本
# 使用方法: ./package_for_deploy.sh

echo "=========================================="
echo "  药品手册 - GitHub Pages 部署打包"
echo "=========================================="

# 设置目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="${SCRIPT_DIR}/deploy"

echo ""
echo "📦 步骤 1: 清理旧文件..."
if [ -d "$DEPLOY_DIR" ]; then
    rm -rf "$DEPLOY_DIR"
    echo "✅ 已清理旧部署目录"
fi

# 创建部署目录
mkdir -p "$DEPLOY_DIR"
echo "✅ 创建部署目录: $DEPLOY_DIR"

echo ""
echo "📋 步骤 2: 复制必要文件..."

# 核心文件
cp "$SCRIPT_DIR/index.html" "$DEPLOY_DIR/"
cp "$SCRIPT_DIR/login.html" "$DEPLOY_DIR/"
cp "$SCRIPT_DIR/auth.js" "$DEPLOY_DIR/"

# 数据文件
mkdir -p "$DEPLOY_DIR/data/drugs"
cp "$SCRIPT_DIR/data/drugs/drugs.js" "$DEPLOY_DIR/data/drugs/"
cp "$SCRIPT_DIR/data/drugs/index.json" "$DEPLOY_DIR/data/drugs/"

# 文档
cp "$SCRIPT_DIR/DEPLOY.md" "$DEPLOY_DIR/"

echo "✅ 文件复制完成"

echo ""
echo "📊 步骤 3: 验证文件..."

# 检查文件是否存在
files=(
    "index.html"
    "login.html"
    "auth.js"
    "data/drugs/drugs.js"
    "data/drugs/index.json"
    "DEPLOY.md"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$DEPLOY_DIR/$file" ]; then
        size=$(du -h "$DEPLOY_DIR/$file" | cut -f1)
        echo "  ✅ $file ($size)"
    else
        echo "  ❌ $file (缺失)"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo ""
    echo "❌ 验证失败，部分文件缺失"
    exit 1
fi

echo ""
echo "📦 步骤 4: 创建压缩包..."

cd "$SCRIPT_DIR"
zip -r "deploy.zip" "deploy/" -q

echo "✅ 压缩包创建完成: deploy.zip"

echo ""
echo "📊 部署包统计:"
echo "  📁 目录: $DEPLOY_DIR"
echo "  📦 压缩包: $SCRIPT_DIR/deploy.zip"
echo "  📊 压缩包大小: $(du -h "$SCRIPT_DIR/deploy.zip" | cut -f1)"
echo "  💊 药品数量: $(grep -c '"id":' "$DEPLOY_DIR/data/drugs/index.json") 个"

echo ""
echo "=========================================="
echo "  打包完成！"
echo "=========================================="
echo ""
echo "🚀 下一步操作:"
echo ""
echo "1. 查看部署文件:"
echo "   ls -la $DEPLOY_DIR"
echo ""
echo "2. 本地测试:"
echo "   cd $DEPLOY_DIR"
echo "   python3 -m http.server 8080"
echo "   然后访问: http://localhost:8080/login.html"
echo ""
echo "3. GitHub Pages 部署:"
echo "   - 解压 deploy.zip"
echo "   - 将 deploy/ 目录内容上传到 GitHub 仓库"
echo "   - 按照 DEPLOY.md 中的步骤配置 GitHub Pages"
echo ""
echo "📖 详细说明请查看: DEPLOY.md"
echo ""
