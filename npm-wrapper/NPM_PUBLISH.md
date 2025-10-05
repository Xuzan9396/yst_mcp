# YST MCP 部署和发布指南

## 🎯 分发方案

YST MCP 采用 **NPM 包发布** 方案，让用户无需 Python 环境即可使用。

---

## 方案：NPM 包发布 ⭐（已实现）

### 用户使用（一行命令）

```bash
npx -y @xuzan/yst-mcp
```

### 工作原理

1. **用户执行** `npx -y @xuzan/yst-mcp`
2. **npm 下载** npm-wrapper 包（约 5KB，仅包含 JS 脚本）
3. **postinstall 脚本**：
   - 检测用户系统平台和架构
   - 从 GitHub Releases 下载对应平台的二进制文件
   - 自动设置执行权限
4. **启动** MCP 服务（所有依赖已打包，包括 Python + Playwright）

### 用户配置（只需一次）

**Claude Desktop**:
```bash
claude mcp add-json yst_mcp -s user '{"type":"stdio","command":"npx","args":["-y","@xuzan/yst-mcp"],"env":{}}'
```

### 数据存储位置

```
~/.yst_mcp/
├── data/
│   ├── cookies.json          # 登录凭证
│   └── browser_profile/      # 浏览器会话
└── output/
    └── new.md                # 默认输出文件
```

---

## ⚠️ 版本对应规则（重要！）

**npm 包版本必须与 GitHub Release tag 版本严格一致！**

| npm package.json | GitHub Tag | 状态 |
|-----------------|------------|------|
| 1.0.0           | v1.0.0     | ✅ 正确 |
| 1.0.1           | v1.0.1     | ✅ 正确 |
| 1.0.0           | v1.0.1     | ❌ 错误！用户安装会失败 |

**原因**：`postinstall.js` 脚本从 package.json 读取版本号，然后从 GitHub Releases 下载对应版本的二进制文件。版本不匹配会导致 404 错误。

---

## 📋 前置条件

### 1. npm 账号

```bash
# 注册账号（如果没有）
npm adduser

# 登录
npm login

# 验证登录
npm whoami
```

### 2. 确保 GitHub Release 已发布

**必须先完成 GitHub Release，再发布 npm 包！**

检查清单：
- [ ] GitHub Actions 已完成所有平台编译
- [ ] Release 已创建：https://github.com/Xuzan9396/yst_mcp/releases/tag/v1.0.0
- [ ] 所有二进制文件已上传（5个平台）：
  - `yst_mcp_darwin_arm64` (macOS Apple Silicon)
  - `yst_mcp_darwin_amd64` (macOS Intel)
  - `yst_mcp_linux_amd64` (Linux x64)
  - `yst_mcp_windows_amd64.exe` (Windows x64)
  - `yst_mcp_windows_arm64.exe` (Windows ARM64)

---

## 🚀 首次发布完整流程

### 步骤 1：创建 GitHub Release

```bash
cd /Users/admin/go/empty/python/yst_mcp

# 1. 确保版本号正确
cat npm-wrapper/package.json | grep version
# 应该显示: "version": "1.0.0"

# 2. 提交所有更改
git add .
git commit -m "feat: 准备发布 v1.0.0"
git push origin main

# 3. 创建对应版本的 tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 步骤 2：等待 GitHub Actions 完成（15-30分钟）

```bash
# 监控编译进度
open https://github.com/Xuzan9396/yst_mcp/actions

# 等待所有任务完成：
# - Build macOS ARM64 ✅
# - Build macOS AMD64 ✅
# - Build Linux ✅
# - Build Windows (amd64 + arm64) ✅
# - Create Release ✅
```

### 步骤 3：验证 GitHub Release

```bash
# 访问 Release 页面，确认所有二进制文件已上传
open https://github.com/Xuzan9396/yst_mcp/releases/tag/v1.0.0

# 或使用 curl 验证单个文件
curl -I https://github.com/Xuzan9396/yst_mcp/releases/download/v1.0.0/yst_mcp_darwin_arm64
# 应该返回 HTTP 302 (重定向到CDN，正常)
```

### 步骤 4：本地测试 npm 包

```bash
cd /Users/admin/go/empty/python/yst_mcp/npm-wrapper

# 测试 postinstall 脚本
npm install

# 验证二进制文件已下载
ls -lh bin/yst_mcp
file bin/yst_mcp

# 测试启动
node bin/yst-mcp.js
# 应该启动 MCP 服务
```

### 步骤 5：发布到 npm

```bash
cd /Users/admin/go/empty/python/yst_mcp/npm-wrapper

# 登录 npm
npm login

# 查看将要发布的文件
npm pack --dry-run

# 首次发布（公开包）
npm publish --access public
```

### 步骤 6：验证发布

```bash
# 查看包信息
npm view @xuzan/yst-mcp

# 查看版本
npm view @xuzan/yst-mcp version
# 应该显示: 1.0.0

# 测试安装（在新目录）
cd /tmp
npx -y @xuzan/yst-mcp
# 应该自动下载并启动
```

### 步骤 7：配置到 Claude Desktop 测试

```bash
claude mcp add-json yst_mcp -s user '{"type":"stdio","command":"npx","args":["-y","@xuzan/yst-mcp"],"env":{}}'

# 重启 Claude Desktop
# 测试工具：collect_reports, browser_login 等
```

---

## 🔄 后续版本发布流程

每次发布新版本时：

### 步骤 1：更新版本号

```bash
cd /Users/admin/go/empty/python/yst_mcp/npm-wrapper

# 方法 1: 使用 npm version（推荐）
npm version patch    # 1.0.0 -> 1.0.1 (bug fix)
npm version minor    # 1.0.0 -> 1.1.0 (new feature)
npm version major    # 1.0.0 -> 2.0.0 (breaking change)

# 方法 2: 手动编辑
vim package.json
# 修改 "version": "1.0.1"
```

### 步骤 2：创建 GitHub Release

```bash
cd /Users/admin/go/empty/python/yst_mcp

# 提交版本更新
git add npm-wrapper/package.json
git commit -m "chore: bump version to v1.0.1"
git push origin main

# 创建对应版本的 tag
git tag -a v1.0.1 -m "Release v1.0.1

新功能:
- xxx

修复:
- xxx"

# 推送 tag（触发 GitHub Actions）
git push origin v1.0.1
```

### 步骤 3：等待编译并发布 npm

```bash
# 等待 GitHub Actions 完成（15-30分钟）
# https://github.com/Xuzan9396/yst_mcp/actions

# 发布到 npm
cd npm-wrapper
npm publish

# 验证
npm view @xuzan/yst-mcp version
# 应该显示: 1.0.1
```

---

## 📦 目录结构

```
python/yst_mcp/
├── server.py                        # MCP 服务入口
├── cookie_manager.py                # Cookie 管理
├── browser_login.py                 # 浏览器登录
├── report_collector.py              # 日报采集
├── build.spec                       # PyInstaller 配置
├── build.sh / build.bat             # 构建脚本
├── .github/workflows/release.yml    # GitHub Actions
└── npm-wrapper/
    ├── package.json                 # npm 包配置
    ├── README.md                    # npm 包说明
    ├── NPM_PUBLISH.md               # 本文件
    ├── .npmignore                   # 忽略配置
    ├── bin/
    │   └── yst-mcp.js               # 启动脚本
    └── scripts/
        └── postinstall.js           # 自动下载脚本
```

---

## 🛠️ 技术细节

### PyInstaller 打包

```bash
# 将 Python 代码 + 依赖打包成单个可执行文件
pyinstaller build.spec

# 输出：
# - dist/yst_mcp (macOS/Linux)
# - dist/yst_mcp.exe (Windows)
```

### GitHub Actions 多平台编译

```yaml
# 使用不同 runner 编译不同平台
- macos-latest (ARM64)
- macos-13 (AMD64)
- ubuntu-latest (AMD64)
- windows-latest (AMD64 + ARM64)
```

### postinstall.js 特性

- ✅ 自动检测平台和架构
- ✅ 3次重试机制（网络容错）
- ✅ 超时保护（10秒获取版本，60秒下载）
- ✅ 备用方案（GitHub API 失败时使用 package.json 版本）
- ✅ 友好的错误提示和手动安装指南

---

## 🐛 故障排除

### 问题 1：npm 发布失败 - 权限错误

```bash
# 确保已登录
npm whoami

# 如果未登录
npm login

# 如果登录失败
npm logout
npm login
```

### 问题 2：用户安装失败 - 找不到 Release

```bash
# 错误: HTTP 404 Not Found

# 检查：
# 1. GitHub Release 是否存在
curl -I https://github.com/Xuzan9396/yst_mcp/releases/download/v1.0.0/yst_mcp_darwin_arm64

# 2. 版本号是否匹配
cat npm-wrapper/package.json | grep version
git describe --tags

# 3. GitHub Actions 是否完成
open https://github.com/Xuzan9396/yst_mcp/actions
```

### 问题 3：用户安装失败 - 网络超时

```bash
# postinstall.js 已内置重试机制
# 用户可以手动下载：

# 1. 访问 Release 页面
open https://github.com/Xuzan9396/yst_mcp/releases/latest

# 2. 下载对应平台文件
curl -L https://github.com/Xuzan9396/yst_mcp/releases/download/v1.0.0/yst_mcp_darwin_arm64 -o yst_mcp

# 3. 设置权限
chmod +x yst_mcp

# 4. 放置到 npm 包目录
mv yst_mcp ~/.npm/_npx/.../node_modules/@xuzan/yst-mcp/bin/
```

### 问题 4：版本不匹配

```bash
# 错误: 用户安装的版本和 Release 版本不一致

# 解决方法：
# 1. 回到项目目录
cd /Users/admin/go/empty/python/yst_mcp

# 2. 检查版本
cat npm-wrapper/package.json | grep version  # npm 版本
git describe --tags                          # Git tag

# 3. 如果不匹配，更新 package.json
cd npm-wrapper
npm version 1.0.0  # 修改为对应版本

# 4. 重新发布
npm publish
```

---

## 📊 发布检查清单

### 发布前
- [ ] 代码已提交到 main 分支
- [ ] `npm-wrapper/package.json` 版本号已更新
- [ ] Git tag 版本与 package.json 一致（去掉 `v`）
- [ ] GitHub Actions 已完成所有平台编译
- [ ] GitHub Release 已创建并包含所有二进制文件
- [ ] npm 账号已登录 (`npm whoami`)
- [ ] 本地测试 `npm install` 成功
- [ ] 本地测试 `node bin/yst-mcp.js` 能启动

### 发布时
- [ ] 执行 `npm publish --access public`（首次）或 `npm publish`
- [ ] 等待发布完成
- [ ] 记录发布的版本号

### 发布后
- [ ] `npm view @xuzan/yst-mcp` 显示正确信息
- [ ] `npm view @xuzan/yst-mcp version` 显示最新版本
- [ ] `npx -y @xuzan/yst-mcp` 能正常安装和运行
- [ ] Claude Desktop 配置正常工作
- [ ] 更新项目 README.md（如需要）

---

## 🎯 快速参考

### 首次发布

```bash
# 1. GitHub Release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 2. 等待编译（15-30分钟）
# https://github.com/Xuzan9396/yst_mcp/actions

# 3. 发布 npm
cd npm-wrapper
npm login
npm publish --access public

# 4. 验证
npx -y @xuzan/yst-mcp
```

### 更新版本

```bash
# 1. 更新版本号
cd npm-wrapper
npm version patch  # 或 minor/major

# 2. GitHub Release
cd ..
git add npm-wrapper/package.json
git commit -m "chore: bump version to vX.X.X"
git push origin main
git tag -a vX.X.X -m "Release vX.X.X"
git push origin vX.X.X

# 3. 等待编译

# 4. 发布 npm
cd npm-wrapper
npm publish
```

---

## 💡 优势总结

**对比传统 Python 分发**：

| 特性 | 传统方式 | YST MCP (npm) |
|-----|---------|--------------|
| 安装 Python | ✅ 必须 | ❌ 不需要 |
| 安装依赖 | `pip install` | ❌ 不需要 |
| 配置路径 | 绝对路径 | `npx` 自动管理 |
| 更新 | 手动重新安装 | `npx` 自动获取最新版 |
| 跨平台 | 需要各平台配置 | 自动检测下载 |
| 用户体验 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎉 用户使用方式（最终效果）

```bash
# 一行命令配置
claude mcp add-json yst_mcp -s user '{"type":"stdio","command":"npx","args":["-y","@xuzan/yst-mcp"],"env":{}}'

# 重启 Claude Desktop，立即可用
# 在 Claude 中对话：
# "使用 yst_mcp 采集 2025-07 到 2025-09 的日报"
```

**完全无需 Python 环境！** 🎊

---

## 📚 相关文档

- npm 官方文档：https://docs.npmjs.com/
- 语义化版本：https://semver.org/
- PyInstaller 文档：https://pyinstaller.org/
- GitHub Actions：https://docs.github.com/en/actions
- GitHub Releases：https://docs.github.com/en/repositories/releasing-projects-on-github

---

**总结**：通过 NPM 包 + PyInstaller 打包，用户体验达到零配置，只需一行命令即可使用！
