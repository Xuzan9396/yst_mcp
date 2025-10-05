"""
浏览器自动化登录模块
使用 Playwright 打开浏览器，等待用户登录，然后提取 Cookie
"""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from cookie_manager import CookieManager
from logger import logger
import asyncio
import sys
import platform
from pathlib import Path
from typing import Optional, Dict, List

class BrowserLogin:
    """浏览器自动化登录"""

    LOGIN_URL = "https://kpi.drojian.dev/site/login"
    TARGET_URL = "https://kpi.drojian.dev/report/report-daily/my-list"

    @staticmethod
    def _get_user_data_dir() -> str:
        """
        获取浏览器持久化数据目录

        打包后使用用户主目录 ~/.yst_mcp/data/browser_profile/
        开发时使用项目目录 ./data/browser_profile/

        Returns:
            浏览器数据目录路径
        """
        if getattr(sys, 'frozen', False):
            # 打包后：使用用户主目录
            return str(Path.home() / '.yst_mcp' / 'data' / 'browser_profile')
        else:
            # 开发时：使用项目目录
            return str(Path(__file__).parent / 'data' / 'browser_profile')

    def __init__(self):
        """初始化浏览器登录管理器"""
        self.cookie_manager = CookieManager()
        self.USER_DATA_DIR = self._get_user_data_dir()
        logger.info(f"初始化 BrowserLogin - 用户数据目录: {self.USER_DATA_DIR}")
        logger.log_playwright_version()
        logger.log_system_chrome()

    @staticmethod
    def _get_browser_args() -> List[str]:
        """
        获取浏览器启动参数，针对不同平台进行优化

        Returns:
            浏览器启动参数列表
        """
        args = ['--start-maximized']

        system = platform.system()
        logger.debug(f"检测到系统平台: {system}")

        if system == 'Windows':
            # Windows 特定参数
            args.extend([
                '--disable-blink-features=AutomationControlled',  # 禁用自动化检测
                '--no-sandbox',  # Windows 上可能需要
                '--disable-dev-shm-usage',  # 避免共享内存问题
                '--disable-gpu',  # 某些 Windows 系统需要
            ])
            logger.debug("添加 Windows 特定浏览器参数")
        elif system == 'Linux':
            # Linux 特定参数
            args.extend([
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ])
            logger.debug("添加 Linux 特定浏览器参数")

        logger.debug(f"浏览器启动参数: {args}")
        return args

    async def launch_browser_for_login(self, headless: bool = False, timeout: int = 300) -> bool:
        """
        启动浏览器进行登录

        Args:
            headless: 是否无头模式（默认 False，显示浏览器窗口）
            timeout: 登录超时时间（秒），默认 5 分钟

        Returns:
            是否登录成功
        """
        logger.info("=" * 60)
        logger.info("开始浏览器登录流程")
        logger.info(f"无头模式: {headless}")
        logger.info(f"超时时间: {timeout} 秒")
        logger.info("=" * 60)

        print(f"正在启动浏览器...")
        print(f"请在浏览器中完成 Google 登录，超时时间：{timeout} 秒")

        browser_args = self._get_browser_args()

        async with async_playwright() as p:
            # 启动浏览器 - 优先使用系统 Chrome
            browser = None
            try:
                logger.info("尝试启动系统 Chrome 浏览器...")
                browser = await p.chromium.launch(
                    channel='chrome',  # 使用系统安装的 Chrome
                    headless=headless,
                    args=browser_args
                )
                logger.info("✓ 成功启动系统 Chrome")
            except Exception as e:
                # 如果系统 Chrome 不可用，使用 Chromium
                logger.warning(f"系统 Chrome 不可用: {e}")
                logger.info("尝试启动 Playwright Chromium...")
                try:
                    browser = await p.chromium.launch(
                        headless=headless,
                        args=browser_args
                    )
                    logger.info("✓ 成功启动 Playwright Chromium")
                except Exception as e2:
                    logger.error(f"启动浏览器失败: {e2}")
                    logger.exception("详细错误信息:")
                    print(f"❌ 启动浏览器失败: {e2}")
                    return False

            try:
                # 创建浏览器上下文
                logger.info("创建浏览器上下文...")
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
                )
                logger.debug("浏览器上下文创建成功")

                # 打开新页面
                logger.info("创建新页面...")
                page = await context.new_page()
                logger.debug("页面创建成功")

                # 导航到登录页面
                print(f"\n正在打开登录页面: {self.TARGET_URL}")
                logger.info(f"导航到目标 URL: {self.TARGET_URL}")
                try:
                    await page.goto(self.TARGET_URL, wait_until='domcontentloaded', timeout=30000)
                    logger.info(f"成功加载页面，当前 URL: {page.url}")
                except Exception as e:
                    logger.warning(f"首次访问出错（可能需要登录）: {e}")
                    print(f"⚠ 首次访问出错（正常，可能需要登录）: {str(e)[:100]}")
                    print("继续等待登录...")

                # 等待用户完成登录
                print("\n⏳ 等待登录完成...")
                print("提示：登录成功后，页面会跳转到日报列表页面")
                print("     请在浏览器中完成 Google OAuth 登录")
                logger.info("开始等待用户登录...")

                # 检测登录成功的标志
                success = await self._wait_for_login_success(page, timeout)

                if success:
                    print("\n✓ 检测到登录成功！")
                    print("正在提取 Cookie...")
                    logger.info("登录成功！开始提取 Cookie...")

                    # 提取 Cookie
                    cookies = await context.cookies()
                    logger.debug(f"获取到 {len(cookies)} 个 Cookie")

                    # 转换为标准格式
                    cookie_list = []
                    for cookie in cookies:
                        cookie_list.append({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', ''),
                            'path': cookie.get('path', '/'),
                        })
                        logger.debug(f"Cookie: {cookie['name']} (domain: {cookie.get('domain', '')})")

                    # 保存 Cookie
                    logger.info("保存 Cookie 到文件...")
                    if self.cookie_manager.save_cookies(cookie_list):
                        print("✓ Cookie 已保存到 data/cookies.json")
                        print("\n🎉 登录流程完成！现在可以使用 collect_reports 采集数据了")
                        logger.info("✓ Cookie 保存成功")
                        logger.info("登录流程完成")

                        # 延迟关闭，让用户看到成功信息
                        logger.info("等待 3 秒后关闭浏览器...")
                        await asyncio.sleep(3)
                        return True
                    else:
                        print("❌ Cookie 保存失败")
                        logger.error("Cookie 保存失败")
                        return False
                else:
                    print(f"\n❌ 登录超时（{timeout} 秒）")
                    logger.error(f"登录超时（{timeout} 秒）")
                    return False

            except Exception as e:
                logger.exception("浏览器操作过程中发生异常:")
                print(f"❌ 发生错误: {e}")
                return False
            finally:
                logger.info("关闭浏览器...")
                await browser.close()
                logger.info("浏览器已关闭")

    async def launch_persistent_browser(self) -> bool:
        """
        启动持久化浏览器上下文（推荐）

        使用持久化用户数据目录，登录状态会自动保存

        Returns:
            是否登录成功
        """
        logger.info("=" * 60)
        logger.info("开始持久化浏览器登录流程")
        logger.info(f"用户数据目录: {self.USER_DATA_DIR}")
        logger.info("=" * 60)

        print(f"正在启动持久化浏览器...")
        print(f"用户数据将保存到: {self.USER_DATA_DIR}")

        browser_args = self._get_browser_args()

        async with async_playwright() as p:
            # 使用持久化上下文启动浏览器 - 优先使用系统 Chrome
            context = None
            try:
                logger.info("尝试启动持久化系统 Chrome...")
                context = await p.chromium.launch_persistent_context(
                    self.USER_DATA_DIR,
                    channel='chrome',  # 使用系统 Chrome
                    headless=False,
                    args=browser_args,
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
                )
                logger.info("✓ 成功启动持久化系统 Chrome")
            except Exception as e:
                # 如果系统 Chrome 不可用，使用 Chromium
                logger.warning(f"系统 Chrome 不可用: {e}")
                logger.info("尝试启动持久化 Playwright Chromium...")
                try:
                    context = await p.chromium.launch_persistent_context(
                        self.USER_DATA_DIR,
                        headless=False,
                        args=browser_args,
                        viewport={'width': 1920, 'height': 1080},
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
                    )
                    logger.info("✓ 成功启动持久化 Playwright Chromium")
                except Exception as e2:
                    logger.error(f"启动持久化浏览器失败: {e2}")
                    logger.exception("详细错误信息:")
                    print(f"❌ 启动浏览器失败: {e2}")
                    return False

            try:
                logger.info("获取或创建页面...")
                page = context.pages[0] if context.pages else await context.new_page()
                logger.debug(f"当前页面数量: {len(context.pages)}")

                # 导航到目标页面
                print(f"\n正在打开页面: {self.TARGET_URL}")
                logger.info(f"导航到目标 URL: {self.TARGET_URL}")
                try:
                    await page.goto(self.TARGET_URL, wait_until='domcontentloaded', timeout=30000)
                    logger.info(f"成功加载页面，当前 URL: {page.url}")
                except Exception as e:
                    logger.warning(f"首次访问出错（可能需要登录）: {e}")
                    print(f"⚠ 首次访问出错（正常，可能需要登录）: {str(e)[:100]}")
                    print("继续等待登录...")

                # 等待登录
                print("\n⏳ 等待登录完成...")
                print("提示：登录成功后，页面会显示日报列表")
                logger.info("开始等待用户登录...")

                success = await self._wait_for_login_success(page, timeout=300)

                if success:
                    print("\n✓ 登录成功！")
                    logger.info("登录成功！开始提取 Cookie...")

                    # 提取 Cookie
                    cookies = await context.cookies()
                    logger.debug(f"获取到 {len(cookies)} 个 Cookie")

                    cookie_list = []
                    for cookie in cookies:
                        cookie_list.append({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', ''),
                            'path': cookie.get('path', '/'),
                        })
                        logger.debug(f"Cookie: {cookie['name']} (domain: {cookie.get('domain', '')})")

                    # 保存 Cookie
                    logger.info("保存 Cookie 到文件...")
                    self.cookie_manager.save_cookies(cookie_list)
                    print("✓ Cookie 已保存")
                    print("\n🎉 登录完成！浏览器会话已保存，下次无需重复登录")
                    logger.info("✓ Cookie 保存成功")
                    logger.info("持久化登录流程完成")

                    # 等待一会儿让用户看到结果
                    logger.info("等待 3 秒后关闭浏览器...")
                    await asyncio.sleep(3)
                    return True
                else:
                    print("\n❌ 登录超时")
                    logger.error("登录超时")
                    return False

            except Exception as e:
                logger.exception("持久化浏览器操作过程中发生异常:")
                print(f"❌ 发生错误: {e}")
                return False
            finally:
                # 关闭上下文
                logger.info("关闭持久化浏览器上下文...")
                await context.close()
                logger.info("持久化浏览器上下文已关闭")

    async def _wait_for_login_success(self, page: Page, timeout: int = 300) -> bool:
        """
        等待登录成功

        检测方法（满足任一即可）：
        1. URL 包含 my-list 或 report-daily
        2. 页面包含 #report_list 元素
        3. 页面包含 .list-group-item 元素（日报列表项）
        4. 页面标题包含"日报"

        Args:
            page: Playwright 页面对象
            timeout: 超时时间（秒）

        Returns:
            是否登录成功
        """
        import time
        start_time = time.time()
        check_interval = 7  # 每7秒检查一次

        logger.info(f"等待登录成功，超时时间: {timeout} 秒，检查间隔: {check_interval} 秒")
        print(f"⏳ 等待登录中，每 {check_interval} 秒检查一次...")
        print(f"提示：如果已经看到日报列表页面，说明登录成功了")

        while time.time() - start_time < timeout:
            try:
                current_url = page.url
                elapsed = int(time.time() - start_time)

                print(f"\n[{elapsed}s] 检查中...")
                print(f"  当前URL: {current_url}")
                logger.debug(f"[{elapsed}s] 检查登录状态 - URL: {current_url}")

                # 方法1: 检查是否已登录到系统（URL包含 kpi.drojian.dev 且不是 accounts.google.com）
                if 'kpi.drojian.dev' in current_url and 'accounts.google.com' not in current_url:
                    print(f"  ✓ 已登录到系统！")
                    logger.info(f"检测到已登录系统 - URL: {current_url}")

                    # 如果不在目标页面，尝试跳转（仅尝试一次）
                    if 'my-list' not in current_url and 'report-daily' not in current_url:
                        print(f"  → 尝试跳转到日报页面...")
                        logger.info(f"不在目标页面，尝试跳转到: {self.TARGET_URL}")
                        try:
                            await page.goto(self.TARGET_URL, wait_until='domcontentloaded', timeout=10000)
                            await asyncio.sleep(2)
                            current_url = page.url
                            print(f"  → 跳转后URL: {current_url}")
                            logger.info(f"跳转成功，当前 URL: {current_url}")
                        except Exception as e:
                            print(f"  ⚠ 跳转失败: {str(e)[:50]}")
                            logger.warning(f"跳转失败: {e}")

                    # 只要在 kpi.drojian.dev 域名下，就认为登录成功
                    print(f"[{elapsed}s] ✓✓✓ 登录成功（已在系统内）！✓✓✓")
                    logger.info(f"✓ 登录成功！耗时: {elapsed} 秒")

                    # 等待 Cookie 保存
                    logger.debug("等待 2 秒确保 Cookie 完全保存...")
                    await asyncio.sleep(2)
                    return True
                else:
                    print(f"  ⏳ 等待跳转到目标页面...")
                    print(f"  （需要URL包含: my-list 或 report-daily）")
                    logger.debug(f"等待跳转 - 当前 URL: {current_url}")

                # 每7秒检查一次
                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"  ❌ 检查出错: {e}")
                logger.error(f"检查登录状态时出错: {e}")
                logger.exception("详细错误信息:")
                await asyncio.sleep(check_interval)

        print(f"\n❌ 登录超时（{timeout}秒）")
        logger.error(f"登录超时 - 超时时间: {timeout} 秒")
        return False

    async def extract_cookies_from_browser(self) -> Optional[List[Dict]]:
        """
        从持久化浏览器上下文中提取 Cookie

        Returns:
            Cookie 列表
        """
        try:
            async with async_playwright() as p:
                try:
                    context = await p.chromium.launch_persistent_context(
                        self.USER_DATA_DIR,
                        channel='chrome',  # 使用系统 Chrome
                        headless=True
                    )
                except Exception:
                    context = await p.chromium.launch_persistent_context(
                        self.USER_DATA_DIR,
                        headless=True
                    )

                cookies = await context.cookies()
                await context.close()

                cookie_list = []
                for cookie in cookies:
                    cookie_list.append({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', ''),
                        'path': cookie.get('path', '/'),
                    })

                return cookie_list

        except Exception as e:
            print(f"提取 Cookie 失败: {e}")
            return None
