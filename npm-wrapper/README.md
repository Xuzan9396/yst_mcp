# @xuzan/yst-mcp

YST KPI 日报采集 MCP 服务 - 自动化采集 KPI 系统日报数据

## 快速开始

### 使用 npx（推荐）

无需安装，直接使用：

```bash
npx -y @xuzan/yst-mcp
```

### 配置到 Claude Desktop

一条命令完成配置：

```bash
claude mcp add-json yst_mcp -s user '{"type":"stdio","command":"npx","args":["-y","@xuzan/yst-mcp"],"env":{}}'
```

或手动编辑配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "yst_mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@xuzan/yst-mcp"],
      "env": {}
    }
  }
}
```

重启 Claude Desktop 即可使用。

## 功能特性

- ✅ **自动登录**: 使用 Playwright 自动化浏览器登录
- ✅ **持久化会话**: 登录一次长期有效
- ✅ **批量采集**: 支持采集多个月份日报
- ✅ **格式化输出**: 自动生成 Markdown 报告
- ✅ **跨平台支持**: macOS / Linux / Windows

## 使用方法

在 Claude Desktop 中直接对话：

```
使用 yst_mcp 采集 2025-07 到 2025-09 的日报
```

首次使用会自动打开浏览器进行 Google 登录，登录成功后自动采集数据。

## MCP 工具列表

| 工具名称 | 功能说明 |
|---------|---------|
| `collect_reports` | 采集指定月份日报 |
| `browser_login` | 手动打开浏览器登录 |
| `check_login_status` | 检查登录状态 |
| `clear_saved_cookies` | 清除登录信息 |

## 数据存储位置

```
~/.yst_mcp/
├── data/
│   ├── cookies.json          # 登录凭证 (8KB)
│   └── browser_profile/      # 浏览器会话 (~20MB)
└── output/
    └── new.md                # 默认输出文件
```

## 支持的平台

- macOS (Intel & Apple Silicon)
- Linux (x64)
- Windows (x64 & ARM64)

## 技术栈

- **打包工具**: PyInstaller
- **浏览器自动化**: Playwright
- **MCP 框架**: FastMCP
- **HTTP 请求**: requests + BeautifulSoup4

## 项目仓库

- GitHub: https://github.com/Xuzan9396/yst_mcp
- NPM: https://www.npmjs.com/package/@xuzan/yst-mcp

## 许可证

MIT License

## 作者

Xuzan
