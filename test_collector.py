"""
测试脚本 - 验证日报采集功能
"""
import asyncio
from report_collector import ReportCollector

async def test_save_cookie():
    """测试保存 Cookie"""
    print("=== 测试 1: 保存 Cookie ===")

    # 使用用户提供的 Cookie 字符串
    cookie_string = "_identity-backend=2fe950a44abdcb3463bfcad84999689cf3bf0646c46ff21158f03c895a3357aaa%3A2%3A%7Bi%3A0%3Bs%3A17%3A%22_identity-backend%22%3Bi%3A1%3Bs%3A20%3A%22%5B416%2C%2241610%22%2C604800%5D%22%3B%7D; _csrf-backend=b94bbbf8e9cf88f90fe9b163183d0a56f2e29b87fe83ab0886ae248e3a299029a%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22_csrf-backend%22%3Bi%3A1%3Bs%3A32%3A%22YB5WuuDS6zLQUl_N9qIWFK29SLw90X9h%22%3B%7D; PHPSESSID=0b224ebbjkdir5sq1lp2vr8948"

    collector = ReportCollector()

    if collector.load_cookies_from_string(cookie_string):
        print("✓ Cookie 解析成功")
        if collector.save_current_cookies():
            print("✓ Cookie 保存成功")
            return True
        else:
            print("❌ Cookie 保存失败")
            return False
    else:
        print("❌ Cookie 解析失败")
        return False

async def test_login_status():
    """测试登录状态"""
    print("\n=== 测试 2: 检查登录状态 ===")

    collector = ReportCollector()
    collector.load_saved_cookies()

    if collector.check_login_status():
        print("✓ 登录状态有效")
        return True
    else:
        print("❌ 登录状态无效（可能 Cookie 已过期）")
        return False

async def test_fetch_one_month():
    """测试采集单个月份"""
    print("\n=== 测试 3: 采集单个月份数据 ===")

    collector = ReportCollector()
    collector.load_saved_cookies()

    # 测试采集 2025-09 月份
    reports = collector.fetch_month_reports("2025-09")

    print(f"采集到 {len(reports)} 条日报")

    if reports:
        print("\n前 3 条日报预览：")
        for i, report in enumerate(reports[:3], 1):
            print(f"\n{i}. {report.get('text', '无标题')[:100]}")
            if report.get('link'):
                print(f"   链接: {report['link']}")
        return True
    else:
        print("未采集到数据（可能是该月份没有日报，或页面结构需要调整）")
        return False

async def test_full_collection():
    """测试完整采集流程"""
    print("\n=== 测试 4: 完整采集流程（7-9月） ===")

    collector = ReportCollector()
    result = await collector.collect("2025-07", "2025-09", "data/new.md")

    print(f"\n结果: {result}")

    # 检查文件是否生成
    import os
    if os.path.exists("data/new.md"):
        print("\n✓ 输出文件已生成: data/new.md")
        # 显示文件前几行
        with open("data/new.md", "r", encoding="utf-8") as f:
            lines = f.readlines()[:20]
            print("\n文件内容预览（前 20 行）：")
            print("=" * 60)
            print("".join(lines))
            print("=" * 60)
        return True
    else:
        print("❌ 输出文件未生成")
        return False

async def main():
    """主测试流程"""
    print("开始测试 YST 日报采集器\n")

    # 测试 1: 保存 Cookie
    if not await test_save_cookie():
        print("\n❌ Cookie 保存失败，停止测试")
        return

    # 测试 2: 检查登录状态
    if not await test_login_status():
        print("\n❌ 登录状态无效，停止测试")
        return

    # 测试 3: 采集单个月份
    await test_fetch_one_month()

    # 测试 4: 完整采集流程
    await test_full_collection()

    print("\n\n✅ 所有测试完成！")

if __name__ == "__main__":
    asyncio.run(main())
