"""
Playwright 浏览器自动安装 Hook
用于 PyInstaller 打包后首次运行时自动下载浏览器
"""
import os
import sys
import subprocess
from pathlib import Path

def ensure_playwright_browser():
    """确保 Playwright 浏览器已安装"""
    if getattr(sys, 'frozen', False):
        # 运行打包后的可执行文件
        # 使用用户目录存储浏览器
        if sys.platform == 'win32':
            browser_dir = Path.home() / '.yst_mcp' / 'playwright_browsers'
        elif sys.platform == 'darwin':
            browser_dir = Path.home() / 'Library' / 'Caches' / 'yst_mcp_playwright'
        else:
            browser_dir = Path.home() / '.cache' / 'yst_mcp_playwright'

        # 设置环境变量
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browser_dir)

        # 检查浏览器是否已安装
        chromium_installed = any(browser_dir.glob('chromium-*/chrome*'))

        if not chromium_installed:
            print("[Playwright] 首次运行，正在下载浏览器...")
            print(f"[Playwright] 浏览器将安装到: {browser_dir}")

            try:
                # 创建目录
                browser_dir.mkdir(parents=True, exist_ok=True)

                # 使用打包的 playwright 模块安装浏览器
                # 注意：这需要 playwright 的 driver 也被打包
                from playwright._impl._driver import compute_driver_executable

                driver_executable = compute_driver_executable()

                # 运行 playwright install chromium
                result = subprocess.run(
                    [str(driver_executable), 'install', 'chromium'],
                    env={**os.environ, 'PLAYWRIGHT_BROWSERS_PATH': str(browser_dir)},
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )

                if result.returncode == 0:
                    print("[Playwright] ✓ 浏览器安装成功")
                else:
                    print(f"[Playwright] ✗ 浏览器安装失败: {result.stderr}")
                    print("[Playwright] 请手动安装: playwright install chromium")

            except Exception as e:
                print(f"[Playwright] ✗ 安装浏览器时出错: {e}")
                print("[Playwright] 程序将使用系统默认位置")
        else:
            print(f"[Playwright] 使用已安装的浏览器: {browser_dir}")

    else:
        # 开发模式，使用系统安装的浏览器
        pass

# 在导入时自动执行
ensure_playwright_browser()
