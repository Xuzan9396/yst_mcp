"""
YST KPI Report Collector MCP Service
使用 FastMCP 采集 KPI 系统日报数据
集成浏览器自动化登录功能
"""
import sys
import platform
import asyncio
import os

# Windows 兼容性：强制使用 UTF-8 编码
if platform.system() == 'Windows':
    # 设置环境变量强制使用 UTF-8
    os.environ['PYTHONUTF8'] = '1'

    # 设置 stdout 和 stderr 为 UTF-8
    import io
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        # Python 3.6 兼容
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    # 在 Windows 上，stdio 需要使用 SelectorEventLoop
    if sys.version_info >= (3, 8):
        # Python 3.8+ 默认使用 ProactorEventLoop，需要改为 SelectorEventLoop
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastmcp import FastMCP
from report_collector import ReportCollector, safe_text
from cookie_manager import CookieManager
from browser_login import BrowserLogin
from logger import logger

# 创建 MCP 服务
mcp = FastMCP("yst-mcp")

@mcp.tool()
async def collect_reports(start_month: str, end_month: str, output_file: str = None, auto_login: bool = False) -> str:
    """
    采集指定月份范围的日报数据

    ⚠️ 重要：使用前请先确保已登录！

    推荐流程：
    1. 先调用 check_login_status 检查登录状态
    2. 如果未登录，调用 browser_login 进行登录
    3. 登录成功后，再调用本工具采集数据

    这样可以避免采集过程被登录流程阻塞。

    Args:
        start_month: 起始月份，格式 YYYY-MM (例如: 2025-07)
        end_month: 结束月份，格式 YYYY-MM (例如: 2025-09)
        output_file: 输出文件路径（可选，默认为 ~/.yst_mcp/output/new.md 或项目目录下 data/new.md）
        auto_login: 未登录时是否自动启动浏览器登录（默认 False，不推荐设为 True）

    Returns:
        采集结果描述
    """
    collector = ReportCollector()
    cookie_manager = CookieManager()

    try:
        # 检查是否有保存的 Cookie
        if cookie_manager.has_cookies():
            collector.load_saved_cookies()

        # 检查登录状态
        if not collector.check_login_status():
            if auto_login:
                print(safe_text("❌ 未登录，正在启动浏览器..."))
                # 启动浏览器登录
                browser_login = BrowserLogin()
                if await browser_login.launch_persistent_browser():
                    # 重新加载 Cookie
                    collector.load_saved_cookies()
                else:
                    return safe_text("❌ 登录失败或超时，请重试")
            else:
                return safe_text(
                    "❌ 未登录或 Cookie 已过期\n\n"
                    "请使用以下方法之一：\n"
                    "1. 调用 browser_login 工具启动浏览器登录\n"
                    "2. 将 auto_login 参数设置为 true，自动打开浏览器"
                )

        # 执行采集
        result = await collector.collect(start_month, end_month, output_file)
        return result
    except Exception as e:
        return f"采集失败: {str(e)}"


@mcp.tool()
async def browser_login(use_persistent: bool = True, timeout: int = 300) -> str:
    """
    启动浏览器进行登录

    ✅ 推荐使用流程：
    1. 调用此工具启动浏览器
    2. 在浏览器中完成 Google 登录（约1分钟）
    3. 登录成功后，调用 collect_reports 采集数据

    工作流程：
    1. 打开浏览器窗口
    2. 等待您完成 Google OAuth 登录
    3. 自动提取并保存 Cookie
    4. 保存浏览器会话

    Args:
        use_persistent: 是否使用持久化浏览器上下文（推荐，默认 True）
        timeout: 登录超时时间（秒），默认 300 秒（5 分钟）

    Returns:
        登录结果
    """
    try:
        logger.info("=" * 60)
        logger.info("browser_login 工具被调用")
        logger.info(f"use_persistent: {use_persistent}, timeout: {timeout}")
        logger.info("=" * 60)

        print(safe_text("🌐 正在启动浏览器登录..."))

        login = BrowserLogin()

        if use_persistent:
            logger.info("使用持久化浏览器上下文")
            success = await login.launch_persistent_browser()
        else:
            logger.info("使用临时浏览器上下文")
            success = await login.launch_browser_for_login(headless=False, timeout=timeout)

        if success:
            logger.info("✓ 浏览器登录成功")
            return safe_text(
                "✅ 登录成功！\n\n"
                "Cookie 已保存，现在可以使用 collect_reports 采集数据了"
            )
        else:
            logger.error("✗ 浏览器登录失败")
            return safe_text(
                "❌ 登录失败或超时\n\n"
                "请检查：\n"
                "1. 浏览器是否正常弹出\n"
                "2. 是否完成了 Google 登录\n"
                "3. 查看日志文件获取详细信息"
            )
    except Exception as e:
        logger.exception("browser_login 执行出错:")
        return safe_text(f"❌ 启动失败: {str(e)}\n\n请查看日志文件获取详细错误信息")


@mcp.tool()
async def save_cookies_from_browser(cookie_string: str) -> str:
    """
    保存浏览器 Cookie（用于首次登录）

    使用方法：
    1. 使用 chrome_devtools_mcp 登录 https://kpi.drojian.dev
    2. 登录成功后，从浏览器复制 Cookie 字符串
    3. 调用此工具保存 Cookie

    Args:
        cookie_string: Cookie 字符串，格式如 "name1=value1; name2=value2"
        或者完整的 curl 命令中的 -b 参数内容

    Returns:
        保存结果
    """
    collector = ReportCollector()

    try:
        # 加载 Cookie
        if collector.load_cookies_from_string(cookie_string):
            # 保存到文件
            if collector.save_current_cookies():
                return safe_text("✓ Cookie 保存成功！现在可以使用 collect_reports 工具采集数据了")
            else:
                return safe_text("❌ Cookie 保存失败")
        else:
            return safe_text("❌ Cookie 格式错误")
    except Exception as e:
        return safe_text(f"保存失败: {str(e)}")


@mcp.tool()
async def check_login_status() -> str:
    """
    检查当前登录状态（建议第一步调用）

    ✅ 推荐工作流程：
    1. 首先调用此工具检查登录状态
    2. 如果返回"未登录"，则调用 browser_login 进行登录
    3. 登录成功后，调用 collect_reports 采集数据

    Returns:
        登录状态信息：
        - "✓ 已登录，Cookie 有效" -> 可以直接采集数据
        - "❌ Cookie 已过期" -> 需要调用 browser_login 重新登录
        - "❌ 未找到保存的 Cookie" -> 需要调用 browser_login 首次登录
    """
    collector = ReportCollector()

    try:
        # 尝试加载已保存的 Cookie
        if collector.cookie_manager.has_cookies():
            collector.load_saved_cookies()

            # 检查登录状态
            if collector.check_login_status():
                return safe_text("✓ 已登录，Cookie 有效")
            else:
                return safe_text("❌ Cookie 已过期，请重新登录并保存 Cookie")
        else:
            return safe_text("❌ 未找到保存的 Cookie，请先使用 save_cookies_from_browser 工具保存登录信息")
    except Exception as e:
        return safe_text(f"检查失败: {str(e)}")


@mcp.tool()
async def check_playwright_installation() -> str:
    """
    检查 Playwright 浏览器驱动安装状态

    Returns:
        安装状态信息
    """
    import subprocess
    import sys

    try:
        logger.info("检查 Playwright 安装状态")

        # 检查 Playwright 模块
        try:
            import playwright
            playwright_version = playwright.__version__
            logger.info(f"Playwright 模块已安装，版本: {playwright_version}")
        except ImportError:
            return safe_text(
                "❌ Playwright 模块未安装\n\n"
                "请运行以下命令安装：\n"
                "pip install playwright\n"
                "playwright install chromium"
            )

        # 检查浏览器驱动
        result_text = safe_text(f"✓ Playwright 模块已安装 (v{playwright_version})\n\n")

        # 尝试检查浏览器安装
        try:
            # 运行 playwright install --dry-run 检查浏览器状态
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
                capture_output=True,
                text=True,
                timeout=10
            )

            logger.debug(f"playwright install --dry-run 输出: {result.stdout}")

            if "is already installed" in result.stdout or "Skipping" in result.stdout:
                result_text += safe_text("✓ Chromium 浏览器驱动已安装\n\n")
                result_text += "系统状态：正常\n"
                result_text += "\n如果浏览器仍无法弹出，请检查：\n"
                result_text += "1. 防火墙/杀毒软件是否阻止\n"
                result_text += "2. 查看详细日志文件"
            else:
                result_text += safe_text("⚠ Chromium 浏览器驱动可能未安装\n\n")
                result_text += "请运行以下命令安装：\n"
                result_text += "playwright install chromium\n\n"
                result_text += "或在 Windows PowerShell 中：\n"
                result_text += "python -m playwright install chromium"

        except subprocess.TimeoutExpired:
            logger.warning("playwright install 命令超时")
            result_text += safe_text("⚠ 无法检查浏览器驱动状态（命令超时）\n\n")
            result_text += "建议手动运行：playwright install chromium"
        except Exception as e:
            logger.error(f"检查浏览器驱动失败: {e}")
            result_text += safe_text(f"⚠ 无法检查浏览器驱动: {str(e)}\n\n")
            result_text += "建议手动运行：playwright install chromium"

        return result_text

    except Exception as e:
        logger.exception("检查 Playwright 安装状态出错:")
        return safe_text(f"❌ 检查失败: {str(e)}")


@mcp.tool()
async def clear_saved_cookies() -> str:
    """
    清除已保存的 Cookie

    Returns:
        清除结果
    """
    manager = CookieManager()

    try:
        if manager.clear_cookies():
            return safe_text("✓ Cookie 已清除")
        else:
            return safe_text("❌ 清除失败")
    except Exception as e:
        return safe_text(f"清除失败: {str(e)}")


if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("YST MCP Server 启动")
        logger.info(f"平台: {platform.system()} {platform.release()}")
        logger.info(f"Python: {sys.version}")

        if platform.system() == 'Windows':
            logger.info("检测到 Windows 系统，已设置 SelectorEventLoop 策略")
            # 记录当前事件循环策略
            policy = asyncio.get_event_loop_policy()
            logger.info(f"当前事件循环策略: {type(policy).__name__}")

        logger.info("=" * 60)

        mcp.run()
    except Exception as e:
        logger.exception("MCP 服务器启动失败:")
        raise
