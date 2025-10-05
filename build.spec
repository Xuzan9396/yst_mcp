# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for yst_mcp
# 用于将 Python MCP 服务打包成独立可执行文件
#

from PyInstaller.utils.hooks import copy_metadata
import os
import sys
from pathlib import Path

# 收集包元数据（解决 importlib.metadata.PackageNotFoundError）
datas = []
datas += copy_metadata('fastmcp')
datas += copy_metadata('playwright')
datas += copy_metadata('requests')
datas += copy_metadata('beautifulsoup4')
datas += copy_metadata('python-dateutil')

# 打包 Playwright Driver（用于首次运行时下载浏览器）
def get_playwright_driver():
    """获取 Playwright driver 文件"""
    try:
        from playwright._impl._driver import compute_driver_executable

        driver_executable = compute_driver_executable()
        driver_path = Path(driver_executable)

        if driver_path.exists():
            print(f"找到 Playwright Driver: {driver_path}")
            # 打包整个 driver 目录
            driver_dir = driver_path.parent
            return [(str(driver_dir), 'playwright/driver')]
        else:
            print(f"⚠️  警告: 未找到 Playwright Driver")
            return []
    except Exception as e:
        print(f"⚠️  警告: 无法获取 Playwright Driver: {e}")
        return []

# 添加 Playwright Driver
playwright_driver = get_playwright_driver()
for src, dst in playwright_driver:
    datas.append((src, dst))

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Playwright 浏览器 hook
        'playwright_hook',
        # FastMCP 相关
        'fastmcp',
        'fastmcp.server',
        'fastmcp.tools',
        # Playwright 相关
        'playwright',
        'playwright.async_api',
        'playwright._impl',
        'playwright._impl._api_types',
        'playwright._impl._connection',
        # HTTP 和解析
        'requests',
        'bs4',
        'beautifulsoup4',
        'lxml',
        'html.parser',
        # 日期处理
        'dateutil',
        'dateutil.relativedelta',
        # 标准库
        'json',
        'asyncio',
        'pathlib',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='yst_mcp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
