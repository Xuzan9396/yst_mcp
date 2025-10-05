"""
日报数据采集模块
使用 requests 和 BeautifulSoup 采集 KPI 系统日报
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cookie_manager import CookieManager
from typing import List, Dict
import re
import sys
import os
import platform
from pathlib import Path

# Windows 兼容：emoji 字符映射
def safe_text(text: str) -> str:
    """
    Windows 兼容的安全输出
    在 Windows 下，将 emoji 替换为文本符号
    """
    if platform.system() == 'Windows':
        # 替换常用 emoji 为文本符号
        replacements = {
            '✓': '[OK]',
            '✅': '[OK]',
            '❌': '[X]',
            '⚠': '[!]',
            '⏳': '[...]',
            '🌐': '[*]',
            '📍': '[*]',
            '💡': '[*]',
            '⏱': '[*]',
            '🔒': '[*]',
        }
        for emoji, replacement in replacements.items():
            text = text.replace(emoji, replacement)
    return text

class ReportCollector:
    """日报采集器"""

    BASE_URL = "https://kpi.drojian.dev"
    LOGIN_URL = f"{BASE_URL}/site/login"
    REPORT_LIST_URL = f"{BASE_URL}/report/report-daily/my-list"

    @staticmethod
    def _get_default_output_dir() -> Path:
        """
        获取默认输出目录

        打包后使用用户主目录 ~/.yst_mcp/output/
        开发时使用项目目录 ./data/

        Returns:
            输出目录路径
        """
        if getattr(sys, 'frozen', False):
            # 打包后：使用用户主目录
            return Path.home() / '.yst_mcp' / 'output'
        else:
            # 开发时：使用项目目录
            return Path(__file__).parent / 'data'

    def __init__(self):
        """初始化采集器"""
        self.cookie_manager = CookieManager()
        self.session = requests.Session()
        self._setup_headers()
        self.default_output_dir = self._get_default_output_dir()

    def _setup_headers(self):
        """设置请求头"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',  # 明确指定接受的编码
            'DNT': '1',
        })

    def load_cookies_from_dict(self, cookie_dict: Dict[str, str]) -> bool:
        """
        从字典加载 Cookie

        Args:
            cookie_dict: Cookie 字典，例如 {'PHPSESSID': 'xxx', '_csrf-backend': 'yyy'}

        Returns:
            是否加载成功
        """
        try:
            for name, value in cookie_dict.items():
                self.session.cookies.set(name, value, domain='kpi.drojian.dev')
            return True
        except Exception as e:
            print(f"加载 Cookie 失败: {e}")
            return False

    def load_cookies_from_string(self, cookie_string: str) -> bool:
        """
        从 Cookie 字符串加载（浏览器复制的格式）

        Args:
            cookie_string: Cookie 字符串，格式如 "name1=value1; name2=value2"

        Returns:
            是否加载成功
        """
        try:
            cookie_dict = {}
            for item in cookie_string.split('; '):
                if '=' in item:
                    name, value = item.split('=', 1)
                    cookie_dict[name] = value
            return self.load_cookies_from_dict(cookie_dict)
        except Exception as e:
            print(f"解析 Cookie 字符串失败: {e}")
            return False

    def save_current_cookies(self) -> bool:
        """保存当前 session 的 Cookie"""
        cookies = []
        for cookie in self.session.cookies:
            cookies.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
            })
        return self.cookie_manager.save_cookies(cookies)

    def load_saved_cookies(self) -> bool:
        """加载已保存的 Cookie"""
        cookies = self.cookie_manager.load_cookies()
        if not cookies:
            return False

        try:
            for cookie in cookies:
                self.session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain', 'kpi.drojian.dev'),
                    path=cookie.get('path', '/')
                )
            return True
        except Exception as e:
            print(f"加载保存的 Cookie 失败: {e}")
            return False

    def check_login_status(self) -> bool:
        """
        检查是否已登录

        Returns:
            是否已登录
        """
        try:
            response = self.session.get(self.REPORT_LIST_URL, allow_redirects=False)
            # 如果返回 200 且不是重定向到登录页，说明已登录
            return response.status_code == 200 and 'login' not in response.url.lower()
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            return False

    def fetch_month_reports(self, month: str) -> List[Dict]:
        """
        获取指定月份的日报列表

        Args:
            month: 月份，格式 YYYY-MM

        Returns:
            日报列表
        """
        url = f"{self.REPORT_LIST_URL}?month={month}"
        reports = []

        try:
            # 禁用自动解压缩，手动处理编码
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            # 手动处理响应内容
            response.raw.decode_content = True
            content = response.content.decode('utf-8', errors='ignore')

            soup = BeautifulSoup(content, 'html.parser')
            report_list = soup.select('#report_list li')

            for li in report_list:
                report = self._parse_report_item(li)
                if report:
                    reports.append(report)

            return reports
        except Exception as e:
            print(f"获取 {month} 月份日报失败: {e}")
            return []

    def _parse_report_item(self, li_element) -> Dict:
        """
        解析单个日报条目

        Args:
            li_element: li 元素

        Returns:
            日报信息字典
        """
        try:
            # 根据实际页面结构调整解析逻辑
            # 这里需要等登录后查看实际结构
            text = li_element.get_text(strip=True)
            link = li_element.find('a')

            return {
                'text': text,
                'link': link['href'] if link and link.get('href') else '',
                'raw_html': str(li_element)
            }
        except Exception as e:
            print(f"解析日报条目失败: {e}")
            return {}

    def generate_month_range(self, start_month: str, end_month: str) -> List[str]:
        """
        生成月份范围列表

        Args:
            start_month: 起始月份 YYYY-MM
            end_month: 结束月份 YYYY-MM

        Returns:
            月份列表
        """
        start_date = datetime.strptime(start_month, '%Y-%m')
        end_date = datetime.strptime(end_month, '%Y-%m')

        months = []
        current = start_date
        while current <= end_date:
            months.append(current.strftime('%Y-%m'))
            current += relativedelta(months=1)

        return months

    async def collect(self, start_month: str, end_month: str, output_file: str = None) -> str:
        """
        采集指定月份范围的日报并保存

        Args:
            start_month: 起始月份
            end_month: 结束月份
            output_file: 输出文件路径（可选，默认使用自动检测的路径）

        Returns:
            采集结果描述
        """
        # 处理输出文件路径
        if output_file is None:
            # 使用默认路径
            output_file = str(self.default_output_dir / 'new.md')
        elif not os.path.isabs(output_file):
            # 如果是相对路径，转换为绝对路径（相对于默认输出目录）
            output_file = str(self.default_output_dir / output_file)

        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 加载已保存的 Cookie
        if self.cookie_manager.has_cookies():
            self.load_saved_cookies()

        # 检查登录状态
        if not self.check_login_status():
            return safe_text(
                "❌ 未登录或登录已过期\n\n"
                "请先使用以下步骤登录：\n"
                "1. 使用 chrome_devtools_mcp 打开登录页面\n"
                f"2. 访问 {self.LOGIN_URL}\n"
                "3. 手动登录\n"
                "4. 登录成功后，使用 save_cookies 工具保存 Cookie\n"
                "5. 重新调用 collect_reports 工具"
            )

        # 生成月份范围
        months = self.generate_month_range(start_month, end_month)

        # 采集所有月份的数据
        all_reports = {}
        for month in months:
            print(f"正在采集 {month} 月份日报...")
            reports = self.fetch_month_reports(month)
            all_reports[month] = reports
            print(safe_text(f"  ✓ 采集到 {len(reports)} 条日报"))

        # 生成 Markdown 文件
        self._generate_markdown(all_reports, output_file)

        total_count = sum(len(reports) for reports in all_reports.values())
        return safe_text(f"✓ 采集完成！共采集 {len(months)} 个月份，{total_count} 条日报，已保存到 {output_file}")

    def _generate_markdown(self, all_reports: Dict[str, List[Dict]], output_file: str):
        """
        生成 Markdown 文件

        Args:
            all_reports: 所有日报数据
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# YST 日报整理\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for month in sorted(all_reports.keys()):
                reports = all_reports[month]
                f.write(f"## {month} 月份日报 ({len(reports)} 条)\n\n")

                if not reports:
                    f.write("*暂无数据*\n\n")
                    continue

                for i, report in enumerate(reports, 1):
                    f.write(f"### {i}. {report.get('text', '无标题')}\n\n")
                    if report.get('link'):
                        f.write(f"链接：{report['link']}\n\n")
                    f.write("---\n\n")
