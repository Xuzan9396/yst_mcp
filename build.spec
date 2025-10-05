# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for yst_mcp
# 用于将 Python MCP 服务打包成独立可执行文件
#

from PyInstaller.utils.hooks import copy_metadata

# 收集包元数据（解决 importlib.metadata.PackageNotFoundError）
datas = []
datas += copy_metadata('fastmcp')
datas += copy_metadata('playwright')
datas += copy_metadata('requests')
datas += copy_metadata('beautifulsoup4')
datas += copy_metadata('python-dateutil')

a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
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
