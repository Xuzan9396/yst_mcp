#!/usr/bin/env python3
"""
测试登录检测逻辑
"""
import asyncio
from browser_login import BrowserLogin

async def main():
    print("=" * 60)
    print("测试 YST MCP 登录检测功能")
    print("=" * 60)

    login = BrowserLogin()

    print("\n1. 测试启动持久化浏览器并检测登录")
    print("-" * 60)

    result = await login.launch_persistent_browser()

    if result:
        print("\n✓✓✓ 测试成功！登录检测正常工作")
    else:
        print("\n❌ 测试失败！登录检测未能成功")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
