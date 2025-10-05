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
    启动浏览器进行登录（后台执行，不阻塞）

    ✅ 新版本改进：
    - 立即返回，不再阻塞等待
    - 在后台线程中启动浏览器
    - 用户可以使用 check_login_status 检查登录是否完成

    ✅ 推荐使用流程：
    1. 调用此工具启动浏览器（立即返回）
    2. 在浏览器中完成 Google 登录（约1分钟）
    3. 调用 check_login_status 检查登录状态
    4. 登录成功后，调用 collect_reports 采集数据

    工作流程：
    1. 立即返回"浏览器启动中..."
    2. 后台打开浏览器窗口
    3. 等待您完成 Google OAuth 登录
    4. 自动提取并保存 Cookie
    5. 保存浏览器会话

    Args:
        use_persistent: 是否使用持久化浏览器上下文（推荐，默认 True）
        timeout: 登录超时时间（秒），默认 300 秒（5 分钟）

    Returns:
        启动状态（立即返回，不等待登录完成）
    """
    import asyncio

    async def background_login():
        """后台执行登录"""
        try:
            login = BrowserLogin()
            if use_persistent:
                await login.launch_persistent_browser()
            else:
                await login.launch_browser_for_login(headless=False, timeout=timeout)
        except Exception as e:
            print(f"后台登录失败: {e}")

    # 在后台任务中启动登录（不等待完成）
    asyncio.create_task(background_login())

    return safe_text(
        "🌐 浏览器自动登录已启动\n\n"
        "📍 当前状态：\n"
        "  ✓ 后台任务已创建\n"
        "  ✓ Playwright 浏览器正在启动中...\n"
        "  ⏳ 预计 3-5 秒后浏览器窗口会打开\n\n"
        "💡 您需要做的：\n"
        "  1. 注意浏览器窗口弹出（可能在后台）\n"
        "  2. 在浏览器中完成 Google 登录\n"
        "  3. 登录成功后，告诉我「登录完成」或「好了」\n\n"
        "⏱️  预计总时间：1-2 分钟\n"
        "🔒 登录信息会安全保存，下次使用无需重复登录"
    )


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
