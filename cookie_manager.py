"""
Cookie 持久化管理模块
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

class CookieManager:
    """管理浏览器 Cookie 的保存和加载"""

    @staticmethod
    def _get_base_dir() -> Path:
        """
        获取基础数据目录

        打包后使用用户主目录 ~/.yst_mcp/data/
        开发时使用项目目录 ./data/

        Returns:
            数据目录路径
        """
        if getattr(sys, 'frozen', False):
            # 打包后：使用用户主目录
            return Path.home() / '.yst_mcp' / 'data'
        else:
            # 开发时：使用项目目录
            return Path(__file__).parent / 'data'

    def __init__(self, cookie_file: str = None):
        """
        初始化 Cookie 管理器

        Args:
            cookie_file: Cookie 保存文件路径（可选，默认使用自动检测的路径）
        """
        if cookie_file is None:
            base_dir = self._get_base_dir()
            self.cookie_file = str(base_dir / 'cookies.json')
        else:
            self.cookie_file = cookie_file
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """确保 data 目录存在"""
        data_dir = os.path.dirname(self.cookie_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def save_cookies(self, cookies: List[Dict]) -> bool:
        """
        保存 Cookie 到文件

        Args:
            cookies: Cookie 列表

        Returns:
            是否保存成功
        """
        try:
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存 Cookie 失败: {e}")
            return False

    def load_cookies(self) -> Optional[List[Dict]]:
        """
        从文件加载 Cookie

        Returns:
            Cookie 列表，如果文件不存在或加载失败返回 None
        """
        if not os.path.exists(self.cookie_file):
            return None

        try:
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            return cookies
        except Exception as e:
            print(f"加载 Cookie 失败: {e}")
            return None

    def has_cookies(self) -> bool:
        """
        检查是否已有保存的 Cookie

        Returns:
            是否存在 Cookie 文件
        """
        return os.path.exists(self.cookie_file)

    def clear_cookies(self) -> bool:
        """
        清除保存的 Cookie

        Returns:
            是否清除成功
        """
        if os.path.exists(self.cookie_file):
            try:
                os.remove(self.cookie_file)
                return True
            except Exception as e:
                print(f"清除 Cookie 失败: {e}")
                return False
        return True
