# NPM 发布指南

本文档说明如何将 yst_mcp 发布到 npm registry。

## 📋 前置条件

1. **npm 账号**
   ```bash
   # 如果没有账号，先注册
   npm adduser

   # 如果已有账号，登录
   npm login
   ```

2. **验证登录**
   ```bash
   npm whoami
   # 应该显示你的 npm 用户名
   ```

3. **确保 GitHub Releases 已就绪**
   - yst_mcp 必须已经发布到 GitHub Releases
   - postinstall 脚本会从 GitHub Releases 下载二进制文件

## 🚀 发布步骤

### 1. 进入 npm-wrapper 目录

```bash
cd /Users/admin/go/empty/python/yst_mcp/npm-wrapper
```

### 2. 测试本地安装（可选但推荐）

```bash
# 在本地测试 postinstall 脚本
npm install

# 测试启动
node bin/yst-mcp.js
```

### 3. 检查包内容

```bash
# 查看将要发布的文件
npm pack --dry-run
```

应该看到：
- `package.json`
- `README.md`
- `bin/yst-mcp.js`
- `scripts/postinstall.js`

### 4. 发布到 npm

```bash
# 首次发布（公开包）
npm publish --access public

# 后续更新
npm publish
```

### 5. 验证发布

```bash
# 查看包信息
npm view @xuzan/yst-mcp

# 测试安装
npx -y @xuzan/yst-mcp
```

## 🔄 更新版本

每次更新时：

1. **更新版本号**
   ```bash
   # 方法1: 手动编辑 package.json 中的 version
   # 方法2: 使用 npm version 命令

   # 补丁版本 (1.0.0 -> 1.0.1)
   npm version patch

   # 次要版本 (1.0.0 -> 1.1.0)
   npm version minor

   # 主要版本 (1.0.0 -> 2.0.0)
   npm version major
   ```

2. **重新发布**
   ```bash
   npm publish
   ```

## 📦 版本管理建议

建议 npm 包版本与 yst_mcp 的 GitHub Release 版本保持一致：

- yst_mcp 发布 `v1.0.0` 到 GitHub
- npm 包同步发布 `1.0.0` 版本

## 🔧 目录结构

```
npm-wrapper/
├── package.json          # npm 包配置
├── README.md            # 包说明文档
├── .npmignore           # 忽略文件配置
├── bin/
│   └── yst-mcp.js       # 启动脚本
└── scripts/
    └── postinstall.js  # 安装后自动下载二进制
```

## 🎯 工作原理

1. **用户执行**: `npx -y @xuzan/yst-mcp`
2. **npm 下载**: npm-wrapper 包（仅包含 JS 脚本，约 5KB）
3. **postinstall**: 自动从 GitHub Releases 下载对应平台的二进制文件
4. **启动**: `bin/yst-mcp.js` 启动下载的二进制文件

## ⚠️ 注意事项

1. **包名规则**
   - 作用域包必须使用 `--access public` 发布
   - 包名：`@xuzan/yst-mcp`（需要你的 npm 用户名为 xuzan）

2. **版本号**
   - 遵循语义化版本 (Semver)
   - 主版本.次版本.补丁版本 (major.minor.patch)

3. **二进制文件**
   - npm 包本身不包含二进制文件
   - 通过 postinstall 从 GitHub Releases 下载
   - 确保 GitHub Release 已发布对应版本

4. **测试**
   - 发布前务必在本地测试 `npm install`
   - 确认 postinstall 脚本能正确下载二进制文件

## 🐛 故障排除

### 发布失败：权限错误

```bash
# 确保已登录
npm login

# 检查登录状态
npm whoami
```

### 发布失败：包名已存在

如果 `@xuzan/yst-mcp` 已被占用，需要修改 package.json 中的包名。

### 用户安装失败

检查：
1. GitHub Release 是否存在对应版本
2. postinstall.js 中的下载 URL 是否正确
3. 网络是否能访问 GitHub

## 📊 发布检查清单

- [ ] npm 账号已登录 (`npm whoami`)
- [ ] GitHub Release 已发布对应版本（所有平台二进制）
- [ ] package.json 版本号已更新
- [ ] 本地测试 `npm install` 成功
- [ ] 本地测试启动成功
- [ ] 执行 `npm publish --access public`
- [ ] 验证 `npm view @xuzan/yst-mcp`
- [ ] 测试 `npx -y @xuzan/yst-mcp`

## 🎉 首次发布完整流程

```bash
# 1. 确保 yst_mcp 已发布到 GitHub
cd /Users/admin/go/empty/python/yst_mcp
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 2. 等待 GitHub Actions 完成编译和发布

# 3. 进入 npm-wrapper 目录
cd npm-wrapper

# 4. 登录 npm
npm login

# 5. 本地测试
npm install
node bin/yst-mcp.js

# 6. 查看将要发布的文件
npm pack --dry-run

# 7. 发布到 npm
npm publish --access public

# 8. 验证
npx -y @xuzan/yst-mcp

# 9. 查看版本
npm view @xuzan/yst-mcp version

# 10. 查看包信息
npm view @xuzan/yst-mcp
```

## 📝 后续更新流程

```bash
# 1. 更新 GitHub Release（新版本）
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1

# 2. 等待 GitHub Actions 编译

# 3. 更新 npm 包版本
cd npm-wrapper
npm version patch  # 或 minor/major

# 4. 发布
npm publish

# 5. 验证
npm view @xuzan/yst-mcp version
```

完成！用户现在可以通过 `npx -y @xuzan/yst-mcp` 直接使用你的 MCP 服务器了！
