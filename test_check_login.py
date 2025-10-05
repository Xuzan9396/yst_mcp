import asyncio
from cookie_manager import CookieManager
from report_collector import ReportCollector

async def main():
    cookie_manager = CookieManager()
    collector = ReportCollector()
    
    print("检查登录状态...")
    
    if cookie_manager.has_cookies():
        print("✓ 发现 Cookie 文件")
        collector.load_saved_cookies()
        
        if collector.check_login_status():
            print("✓ 已登录，Cookie 有效")
            print("\n现在可以直接采集数据，不需要打开浏览器")
            return True
        else:
            print("❌ Cookie 已过期")
            return False
    else:
        print("❌ 未找到 Cookie")
        return False

asyncio.run(main())
