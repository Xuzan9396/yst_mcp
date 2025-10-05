#!/usr/bin/env python3
"""
测试两步走工作流程
模拟 MCP 调用：采集 2025-03 月数据
"""
import asyncio
from cookie_manager import CookieManager
from browser_login import BrowserLogin
from report_collector import ReportCollector

async def main():
    print("=" * 60)
    print("测试工作流程：采集 2025-03 月数据")
    print("=" * 60)

    # 第一步：检查登录状态
    print("\n📋 第一步：检查登录状态")
    print("-" * 60)
    
    cookie_manager = CookieManager()
    collector = ReportCollector()
    
    is_logged_in = False
    
    if cookie_manager.has_cookies():
        print("✓ 发现已保存的 Cookie")
        collector.load_saved_cookies()
        
        if collector.check_login_status():
            print("✓ Cookie 有效，已登录")
            is_logged_in = True
        else:
            print("❌ Cookie 已过期")
    else:
        print("❌ 未找到保存的 Cookie")
    
    # 第二步：如果未登录，启动浏览器登录
    if not is_logged_in:
        print("\n🌐 第二步：启动浏览器登录")
        print("-" * 60)
        
        login = BrowserLogin()
        print("提示：将打开浏览器，请完成登录...")
        
        result = await login.launch_persistent_browser()
        
        if result:
            print("\n✓✓✓ 登录成功！")
            # 重新加载 Cookie
            collector.load_saved_cookies()
        else:
            print("\n❌ 登录失败")
            return
    else:
        print("\n⏭️  跳过第二步：已登录")
    
    # 第三步：采集数据
    print("\n📊 第三步：采集数据")
    print("-" * 60)
    
    start_month = "2025-03"
    end_month = "2025-03"
    output_file = "/Users/admin/Downloads/new3.md"
    
    print(f"采集月份：{start_month} 到 {end_month}")
    print(f"输出文件：{output_file}")
    print()
    
    result = await collector.collect(start_month, end_month, output_file)
    
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
