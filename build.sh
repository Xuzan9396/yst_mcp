#!/bin/bash
#
# yst_mcp 构建脚本 (macOS/Linux)
#
# 使用 PyInstaller 将 Python 项目打包成独立二进制文件
#

set -e  # 遇到错误立即退出

echo "========================================="
echo " YST MCP 构建脚本"
echo "========================================="

# 检查 Python 版本
echo ""
echo "🔍 检查 Python 版本..."
python3 --version

# 激活虚拟环境（如果存在）
if [ -d ".venv" ]; then
    echo ""
    echo "🔧 激活虚拟环境..."
    source .venv/bin/activate
else
    echo ""
    echo "⚠️  未找到虚拟环境，使用系统 Python"
fi

# 安装 PyInstaller
echo ""
echo "📦 安装/更新 PyInstaller..."
pip install --upgrade pyinstaller

# 清理旧的构建文件
echo ""
echo "🧹 清理旧的构建文件..."
rm -rf build/ dist/

# 运行 PyInstaller
echo ""
echo "🚀 开始打包..."
pyinstaller build.spec

# 检查构建结果
if [ -f "dist/yst_mcp" ]; then
    echo ""
    echo "✅ 构建成功！"
    echo ""
    echo "📍 二进制文件位置: dist/yst_mcp"
    ls -lh dist/yst_mcp
    echo ""
    echo "🧪 测试运行:"
    echo "   ./dist/yst_mcp"
else
    echo ""
    echo "❌ 构建失败：未找到输出文件"
    exit 1
fi

echo ""
echo "========================================="
echo " 构建完成"
echo "========================================="
