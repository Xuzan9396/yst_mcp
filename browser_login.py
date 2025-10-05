"""
浏览器自动化登录模块
使用 Playwright 打开浏览器，等待用户登录，然后提取 Cookie
"""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from cookie_manager import CookieManager
import asyncio
import sys
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

    async def launch_browser_for_login(self, headless: bool = False, timeout: int = 300) -> bool:
        """
        启动浏览器进行登录

        Args:
            headless: 是否无头模式（默认 False，显示浏览器窗口）
            timeout: 登录超时时间（秒），默认 5 分钟

        Returns:
            是否登录成功
        """
        print(f"正在启动浏览器...")
        print(f"请在浏览器中完成 Google 登录，超时时间：{timeout} 秒")

        async with async_playwright() as p:
            # 启动浏览器 - 优先使用系统 Chrome
            try:
                browser = await p.chromium.launch(
                    channel='chrome',  # 使用系统安装的 Chrome
                    headless=headless,
                    args=['--start-maximized']
                )
            except Exception:
                # 如果系统 Chrome 不可用，使用 Chromium
                browser = await p.chromium.launch(
                    headless=headless,
                    args=['--start-maximized']
                )

            try:
                # 创建浏览器上下文
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
                )

                # 打开新页面
                page = await context.new_page()

                # 导航到登录页面
                print(f"\n正在打开登录页面: {self.TARGET_URL}")
                try:
                    await page.goto(self.TARGET_URL, wait_until='domcontentloaded', timeout=30000)
                except Exception as e:
                    print(f"⚠ 首次访问出错（正常，可能需要登录）: {str(e)[:100]}")
                    print("继续等待登录...")

                # 等待用户完成登录
                print("\n⏳ 等待登录完成...")
                print("提示：登录成功后，页面会跳转到日报列表页面")
                print("     请在浏览器中完成 Google OAuth 登录")

                # 检测登录成功的标志
                success = await self._wait_for_login_success(page, timeout)

                if success:
                    print("\n✓ 检测到登录成功！")
                    print("正在提取 Cookie...")

                    # 提取 Cookie
                    cookies = await context.cookies()

                    # 转换为标准格式
                    cookie_list = []
                    for cookie in cookies:
                        cookie_list.append({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', ''),
                            'path': cookie.get('path', '/'),
                        })

                    # 保存 Cookie
                    if self.cookie_manager.save_cookies(cookie_list):
                        print("✓ Cookie 已保存到 data/cookies.json")
                        print("\n🎉 登录流程完成！现在可以使用 collect_reports 采集数据了")
                        return True
                    else:
                        print("❌ Cookie 保存失败")
                        return False
                else:
                    print(f"\n❌ 登录超时（{timeout} 秒）")
                    return False

            finally:
                await browser.close()

    async def launch_persistent_browser(self) -> bool:
        """
        启动持久化浏览器上下文（推荐）

        使用持久化用户数据目录，登录状态会自动保存

        Returns:
            是否登录成功
        """
        print(f"正在启动持久化浏览器...")
        print(f"用户数据将保存到: {self.USER_DATA_DIR}")

        async with async_playwright() as p:
            # 使用持久化上下文启动浏览器 - 优先使用系统 Chrome
            try:
                context = await p.chromium.launch_persistent_context(
                    self.USER_DATA_DIR,
                    channel='chrome',  # 使用系统 Chrome
                    headless=False,
                    args=['--start-maximized'],
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
                )
            except Exception:
                # 如果系统 Chrome 不可用，使用 Chromium
                context = await p.chromium.launch_persistent_context(
                    self.USER_DATA_DIR,
                    headless=False,
                    args=['--start-maximized'],
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
                )

            try:
                page = context.pages[0] if context.pages else await context.new_page()

                # 导航到目标页面
                print(f"\n正在打开页面: {self.TARGET_URL}")
                try:
                    await page.goto(self.TARGET_URL, wait_until='domcontentloaded', timeout=30000)
                except Exception as e:
                    print(f"⚠ 首次访问出错（正常，可能需要登录）: {str(e)[:100]}")
                    print("继续等待登录...")

                # 等待登录
                print("\n⏳ 等待登录完成...")
                print("提示：登录成功后，页面会显示日报列表")

                success = await self._wait_for_login_success(page, timeout=300)

                if success:
                    print("\n✓ 登录成功！")

                    # 提取 Cookie
                    cookies = await context.cookies()
                    cookie_list = []
                    for cookie in cookies:
                        cookie_list.append({
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', ''),
                            'path': cookie.get('path', '/'),
                        })

                    # 保存 Cookie
                    self.cookie_manager.save_cookies(cookie_list)
                    print("✓ Cookie 已保存")
                    print("\n🎉 登录完成！浏览器会话已保存，下次无需重复登录")

                    # 等待一会儿让用户看到结果
                    await asyncio.sleep(3)
                    return True
                else:
                    print("\n❌ 登录超时")
                    return False

            finally:
                # 关闭上下文
                await context.close()

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

        print(f"⏳ 等待登录中，每 {check_interval} 秒检查一次...")
        print(f"提示：如果已经看到日报列表页面，说明登录成功了")

        while time.time() - start_time < timeout:
            try:
                current_url = page.url
                elapsed = int(time.time() - start_time)

                print(f"\n[{elapsed}s] 检查中...")
                print(f"  当前URL: {current_url}")

                # 方法1: 检查是否已登录到系统（URL包含 kpi.drojian.dev 且不是 accounts.google.com）
                if 'kpi.drojian.dev' in current_url and 'accounts.google.com' not in current_url:
                    print(f"  ✓ 已登录到系统！")

                    # 如果不在目标页面，尝试跳转（仅尝试一次）
                    if 'my-list' not in current_url and 'report-daily' not in current_url:
                        print(f"  → 尝试跳转到日报页面...")
                        try:
                            await page.goto(self.TARGET_URL, wait_until='domcontentloaded', timeout=10000)
                            await asyncio.sleep(2)
                            current_url = page.url
                            print(f"  → 跳转后URL: {current_url}")
                        except Exception as e:
                            print(f"  ⚠ 跳转失败: {str(e)[:50]}")

                    # 只要在 kpi.drojian.dev 域名下，就认为登录成功
                    print(f"[{elapsed}s] ✓✓✓ 登录成功（已在系统内）！✓✓✓")

                    # 等待 Cookie 保存
                    await asyncio.sleep(2)
                    return True
                else:
                    print(f"  ⏳ 等待跳转到目标页面...")
                    print(f"  （需要URL包含: my-list 或 report-daily）")

                # 每7秒检查一次
                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"  ❌ 检查出错: {e}")
                await asyncio.sleep(check_interval)

        print(f"\n❌ 登录超时（{timeout}秒）")
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
