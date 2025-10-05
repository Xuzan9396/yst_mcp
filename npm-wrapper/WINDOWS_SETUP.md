# Windows 系统安装指南

## 问题说明

由于 Playwright 浏览器驱动无法打包进二进制文件，Windows 用户需要额外安装 Playwright 浏览器。

## 安装步骤

### 1. 安装 Python（如果还没有）

下载并安装 Python 3.10 或更高版本：
- 官方下载：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

### 2. 安装 Playwright 和浏览器驱动

打开 PowerShell 或命令提示符，运行：

```powershell
# 安装 Playwright
python -m pip install playwright

# 安装 Chromium 浏览器
python -m playwright install chromium
```

### 3. 验证安装

运行以下命令检查安装状态：

```powershell
npx @xuzan/yst-mcp
```

然后在 Claude Code 中使用：

```
使用 check_playwright_installation 检查安装状态
```

## 常见问题

### Q: 为什么需要单独安装？

A: Playwright 的浏览器（约 300MB）存储在系统目录中，无法打包进可执行文件。这是 Playwright 的设计限制。

### Q: 提示找不到 Python？

A: 确保：
1. Python 已安装并添加到 PATH
2. 重启命令行窗口
3. 使用 `python --version` 验证

### Q: 浏览器仍然无法弹出？

A: 检查：
1. 运行 `python -m playwright install chromium`
2. 检查防火墙/杀毒软件是否阻止
3. 查看日志文件：`%USERPROFILE%\.yst_mcp\data\logs\`

## 日志位置

Windows 系统日志保存在：
```
C:\Users\<你的用户名>\.yst_mcp\data\logs\
```

查看最新日志文件获取详细错误信息。

## 技术支持

如有问题，请提供：
1. Python 版本：`python --version`
2. Playwright 版本：`python -m playwright --version`
3. 最新的日志文件内容

GitHub Issues: https://github.com/Xuzan9396/yst_mcp/issues
