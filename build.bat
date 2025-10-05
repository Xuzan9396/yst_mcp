@echo off
REM
REM yst_mcp 构建脚本 (Windows)
REM
REM 使用 PyInstaller 将 Python 项目打包成独立二进制文件
REM

echo =========================================
echo  YST MCP 构建脚本
echo =========================================

REM 检查 Python 版本
echo.
echo 检查 Python 版本...
python --version

REM 激活虚拟环境（如果存在）
if exist ".venv\Scripts\activate.bat" (
    echo.
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
) else (
    echo.
    echo 未找到虚拟环境，使用系统 Python
)

REM 安装 PyInstaller
echo.
echo 安装/更新 PyInstaller...
pip install --upgrade pyinstaller

REM 清理旧的构建文件
echo.
echo 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 运行 PyInstaller
echo.
echo 开始打包...
pyinstaller build.spec

REM 检查构建结果
if exist "dist\yst_mcp.exe" (
    echo.
    echo ✅ 构建成功！
    echo.
    echo 📍 二进制文件位置: dist\yst_mcp.exe
    dir dist\yst_mcp.exe
    echo.
    echo 🧪 测试运行:
    echo    dist\yst_mcp.exe
) else (
    echo.
    echo ❌ 构建失败：未找到输出文件
    exit /b 1
)

echo.
echo =========================================
echo  构建完成
echo =========================================
pause
