#!/usr/bin/env node

const https = require('https');
const fs = require('fs');
const path = require('path');

// 从 package.json 读取版本
function getPackageVersion() {
  try {
    const packageJson = require('../package.json');
    return 'v' + packageJson.version;
  } catch (e) {
    return 'v1.0.0'; // 默认版本
  }
}

// 获取平台和架构信息
function getPlatformInfo() {
  const platform = process.platform;
  const arch = process.arch;

  let platformName;
  let archName;

  // 平台映射
  switch (platform) {
    case 'darwin':
      platformName = 'darwin';
      break;
    case 'linux':
      platformName = 'linux';
      break;
    case 'win32':
      platformName = 'windows';
      break;
    default:
      throw new Error(`不支持的平台: ${platform}`);
  }

  // 架构映射
  switch (arch) {
    case 'x64':
      archName = 'amd64';
      break;
    case 'arm64':
      archName = 'arm64';
      break;
    default:
      throw new Error(`不支持的架构: ${arch}`);
  }

  return { platform: platformName, arch: archName };
}

// 获取最新 Release 版本（带重试）
function getLatestVersion(retries = 3) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      path: '/repos/Xuzan9396/yst_mcp/releases/latest',
      method: 'GET',
      timeout: 10000, // 10秒超时
      headers: {
        'User-Agent': 'yst-mcp-installer'
      }
    };

    const req = https.get(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const release = JSON.parse(data);
            resolve(release.tag_name);
          } catch (e) {
            reject(new Error(`解析版本信息失败: ${e.message}`));
          }
        } else {
          reject(new Error(`获取版本失败: HTTP ${res.statusCode}`));
        }
      });
    });

    req.on('error', (err) => {
      if (retries > 0) {
        console.log(`⚠️  网络错误，正在重试... (剩余 ${retries} 次)`);
        setTimeout(() => {
          getLatestVersion(retries - 1).then(resolve).catch(reject);
        }, 2000); // 等待2秒后重试
      } else {
        reject(err);
      }
    });

    req.on('timeout', () => {
      req.destroy();
      if (retries > 0) {
        console.log(`⚠️  请求超时，正在重试... (剩余 ${retries} 次)`);
        setTimeout(() => {
          getLatestVersion(retries - 1).then(resolve).catch(reject);
        }, 2000);
      } else {
        reject(new Error('请求超时'));
      }
    });
  });
}

// 下载二进制文件（带重试）
function downloadBinary(url, dest, retries = 3) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);

    const req = https.get(url, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        file.close();
        fs.unlink(dest, () => {});
        // 处理重定向
        return downloadBinary(response.headers.location, dest, retries).then(resolve).catch(reject);
      }

      if (response.statusCode !== 200) {
        file.close();
        fs.unlink(dest, () => {});
        reject(new Error(`下载失败: HTTP ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    });

    req.on('error', (err) => {
      file.close();
      fs.unlink(dest, () => {});

      if (retries > 0) {
        console.log(`⚠️  下载出错，正在重试... (剩余 ${retries} 次)`);
        setTimeout(() => {
          downloadBinary(url, dest, retries - 1).then(resolve).catch(reject);
        }, 2000);
      } else {
        reject(err);
      }
    });

    req.on('timeout', () => {
      req.destroy();
      file.close();
      fs.unlink(dest, () => {});

      if (retries > 0) {
        console.log(`⚠️  下载超时，正在重试... (剩余 ${retries} 次)`);
        setTimeout(() => {
          downloadBinary(url, dest, retries - 1).then(resolve).catch(reject);
        }, 2000);
      } else {
        reject(new Error('下载超时'));
      }
    });

    req.setTimeout(60000); // 60秒下载超时
  });
}

async function install() {
  try {
    console.log('🚀 正在安装 yst-mcp...');

    // 获取平台信息
    const { platform, arch } = getPlatformInfo();
    console.log(`📦 检测到平台: ${platform} ${arch}`);

    // 获取版本号（优先从 GitHub，失败则使用 package.json）
    let version;
    console.log('🔍 获取版本信息...');
    try {
      version = await getLatestVersion();
      console.log(`✅ 最新版本: ${version}`);
    } catch (err) {
      console.log(`⚠️  无法从 GitHub 获取最新版本: ${err.message}`);
      version = getPackageVersion();
      console.log(`📌 使用 package.json 版本: ${version}`);
    }

    // 构建下载 URL
    const binaryName = platform === 'windows' ? 'yst_mcp.exe' : 'yst_mcp';
    const archiveName = `yst_mcp_${platform}_${arch}${platform === 'windows' ? '.exe' : ''}`;
    const url = `https://github.com/Xuzan9396/yst_mcp/releases/download/${version}/${archiveName}`;

    // 下载路径
    const binDir = path.join(__dirname, '..', 'bin');
    if (!fs.existsSync(binDir)) {
      fs.mkdirSync(binDir, { recursive: true });
    }
    const destPath = path.join(binDir, binaryName);

    // 下载二进制文件
    console.log(`📥 下载中: ${url}`);
    console.log(`   目标路径: ${destPath}`);
    await downloadBinary(url, destPath);

    // 设置执行权限 (Unix 系统)
    if (platform !== 'windows') {
      fs.chmodSync(destPath, 0o755);
    }

    console.log('\n✅ yst-mcp 安装成功!');
    console.log(`\n📍 安装路径: ${destPath}`);

    // 验证文件大小
    const stats = fs.statSync(destPath);
    const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
    console.log(`📦 文件大小: ${sizeMB} MB`);

    console.log('\n✅ yst-mcp 二进制文件安装成功！');

    // Windows 额外提示
    if (platform === 'windows') {
      console.log('\n⚠️  Windows 用户重要提示:');
      console.log('   首次使用需要安装 Playwright 浏览器驱动！');
      console.log('   请在 PowerShell 中运行以下命令:');
      console.log('');
      console.log('   python -m pip install playwright');
      console.log('   python -m playwright install chromium');
      console.log('');
      console.log('   如果没有 Python，请先安装 Python 3.10+');
      console.log('   下载地址: https://www.python.org/downloads/');
    } else {
      console.log('\n💡 首次使用提示:');
      console.log('   如果浏览器无法弹出，请安装 Playwright 浏览器驱动:');
      console.log('   pip install playwright && playwright install chromium');
    }

    console.log('\n💡 使用方法:');
    console.log('  npx -y @xuzan/yst-mcp');
    console.log('\n🔧 Claude Desktop 配置:');
    console.log('  claude mcp add-json yst_mcp -s user \'{"type":"stdio","command":"npx","args":["-y","@xuzan/yst-mcp"],"env":{}}\'');
    console.log('\n💾 数据存储位置:');
    console.log('  ~/.yst_mcp/data/cookies.json          (登录凭证)');
    console.log('  ~/.yst_mcp/data/browser_profile/      (浏览器会话)');
    console.log('  ~/.yst_mcp/output/                    (日报输出)');

  } catch (error) {
    console.error('\n❌ 安装失败:', error.message);
    console.error('\n💡 可能的原因:');
    console.error('  1. 网络连接问题 - 检查是否能访问 GitHub');
    console.error('  2. Release 尚未发布 - 等待 GitHub Actions 完成编译');
    console.error('  3. 平台不支持 - 检查您的操作系统和架构');
    console.error('\n🔧 手动安装步骤:');
    console.error('  1. 访问 GitHub Releases:');
    console.error('     https://github.com/Xuzan9396/yst_mcp/releases/latest');
    console.error('  2. 下载对应平台的二进制文件');
    console.error(`  3. 重命名为 ${platform === 'windows' ? 'yst_mcp.exe' : 'yst_mcp'}`);
    console.error(`  4. 放置到目录: ${path.join(__dirname, '..', 'bin')}`);
    console.error('  5. 设置执行权限 (macOS/Linux): chmod +x yst_mcp');
    process.exit(1);
  }
}

// 执行安装
install();
