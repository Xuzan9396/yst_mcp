#!/usr/bin/env node

const https = require('https');
const fs = require('fs');
const path = require('path');

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

// 获取最新 Release 版本
function getLatestVersion() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      path: '/repos/Xuzan9396/yst_mcp/releases/latest',
      method: 'GET',
      headers: {
        'User-Agent': 'yst-mcp-installer'
      }
    };

    https.get(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          const release = JSON.parse(data);
          resolve(release.tag_name);
        } else {
          reject(new Error(`获取版本失败: ${res.statusCode}`));
        }
      });
    }).on('error', reject);
  });
}

// 下载二进制文件
function downloadBinary(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);

    https.get(url, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        // 处理重定向
        return downloadBinary(response.headers.location, dest).then(resolve).catch(reject);
      }

      if (response.statusCode !== 200) {
        reject(new Error(`下载失败: ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => {});
      reject(err);
    });
  });
}

async function install() {
  try {
    console.log('🚀 正在安装 yst-mcp...');

    // 获取平台信息
    const { platform, arch } = getPlatformInfo();
    console.log(`📦 检测到平台: ${platform} ${arch}`);

    // 获取最新版本
    console.log('🔍 获取最新版本...');
    const version = await getLatestVersion();
    console.log(`✅ 最新版本: ${version}`);

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
    await downloadBinary(url, destPath);

    // 设置执行权限 (Unix 系统)
    if (platform !== 'windows') {
      fs.chmodSync(destPath, 0o755);
    }

    console.log('✅ yst-mcp 安装成功!');
    console.log(`\n📍 安装路径: ${destPath}`);
    console.log('\n使用方法:');
    console.log('  npx -y @xuzan/yst-mcp');
    console.log('\nClaude Desktop 配置:');
    console.log('  claude mcp add-json yst_mcp -s user \'{"type":"stdio","command":"npx","args":["-y","@xuzan/yst-mcp"],"env":{}}\'');
    console.log('\n数据存储位置:');
    console.log('  ~/.yst_mcp/data/cookies.json          (登录凭证)');
    console.log('  ~/.yst_mcp/data/browser_profile/      (浏览器会话)');
    console.log('  ~/.yst_mcp/output/                    (日报输出)');

  } catch (error) {
    console.error('❌ 安装失败:', error.message);
    console.error('\n请尝试以下方案:');
    console.error('1. 检查网络连接是否正常');
    console.error('2. 检查是否能访问 GitHub');
    console.error('3. 手动从 GitHub Releases 下载二进制文件');
    console.error('   https://github.com/Xuzan9396/yst_mcp/releases/latest');
    process.exit(1);
  }
}

// 执行安装
install();
