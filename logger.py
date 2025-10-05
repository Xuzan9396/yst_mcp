"""
详细日志模块
用于记录浏览器自动化的详细调试信息，特别针对 Windows 系统调试
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import platform


class DetailedLogger:
    """详细日志记录器"""

    _instance: Optional['DetailedLogger'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self.logger = None
        self._setup_logger()

    def _get_log_dir(self) -> Path:
        """
        获取日志目录

        Returns:
            日志目录路径
        """
        if getattr(sys, 'frozen', False):
            # 打包后：使用用户主目录
            log_dir = Path.home() / '.yst_mcp' / 'data' / 'logs'
        else:
            # 开发时：使用项目目录
            log_dir = Path(__file__).parent / 'data' / 'logs'

        # 确保目录存在
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def _setup_logger(self):
        """设置日志记录器"""
        # 创建 logger
        self.logger = logging.getLogger('yst_mcp')
        self.logger.setLevel(logging.DEBUG)

        # 清除已有的 handlers
        self.logger.handlers.clear()

        # 日志目录
        log_dir = self._get_log_dir()

        # 日志文件名：包含日期和平台信息
        log_filename = f"browser_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{platform.system().lower()}.log"
        log_file = log_dir / log_filename

        # 文件处理器 - 详细日志
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 控制台处理器 - 只显示 INFO 及以上
        # Windows 兼容：确保使用 UTF-8 编码
        import io
        if platform.system() == 'Windows' and hasattr(sys.stdout, 'buffer'):
            console_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        else:
            console_stream = sys.stdout
        console_handler = logging.StreamHandler(console_stream)
        console_handler.setLevel(logging.INFO)

        # 格式化器
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(message)s'
        )

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 记录系统信息
        self.logger.info("=" * 80)
        self.logger.info("YST MCP Browser Login - 详细调试日志")
        self.logger.info("=" * 80)
        self.logger.info(f"日志文件: {log_file}")
        self.logger.info(f"平台: {platform.system()} {platform.release()}")
        self.logger.info(f"Python 版本: {platform.python_version()}")
        self.logger.info(f"工作目录: {Path.cwd()}")
        self.logger.info("=" * 80)

    def debug(self, msg: str, *args, **kwargs):
        """调试级别日志"""
        if self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """信息级别日志"""
        if self.logger:
            self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """警告级别日志"""
        if self.logger:
            self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """错误级别日志"""
        if self.logger:
            self.logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        """异常级别日志（包含堆栈跟踪）"""
        if self.logger:
            self.logger.exception(msg, *args, **kwargs)

    def log_browser_config(self, config: dict):
        """记录浏览器配置"""
        self.info("浏览器配置:")
        for key, value in config.items():
            self.debug(f"  {key}: {value}")

    def log_playwright_version(self):
        """记录 Playwright 版本"""
        try:
            import playwright
            self.info(f"Playwright 版本: {playwright.__version__}")
        except Exception as e:
            self.error(f"无法获取 Playwright 版本: {e}")

    def log_system_chrome(self):
        """检测并记录系统 Chrome 信息"""
        system = platform.system()
        self.debug(f"检测系统 Chrome - 平台: {system}")

        chrome_paths = {
            'Windows': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            ],
            'Darwin': [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            ],
            'Linux': [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser',
            ]
        }

        paths = chrome_paths.get(system, [])
        for chrome_path in paths:
            if Path(chrome_path).exists():
                self.info(f"✓ 找到系统 Chrome: {chrome_path}")
                return

        self.warning(f"⚠ 未找到系统 Chrome，将使用 Playwright 内置 Chromium")


# 全局 logger 实例
logger = DetailedLogger()
