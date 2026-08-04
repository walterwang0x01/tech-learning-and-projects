# Electron 桌面应用
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 架构

```
Electron 应用
├── 主进程（Main Process）    — Node.js 环境，管理窗口和系统交互
├── 渲染进程（Renderer）      — Chromium，运行 Web 页面
└── 预加载脚本（Preload）     — 桥接主进程和渲染进程
```

## 2. 基本结构

```javascript
// main.js（主进程）
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,  // 安全：隔离上下文
      nodeIntegration: false,  // 安全：禁用 Node
    },
  });
  win.loadFile('index.html');
  // 或 win.loadURL('http://localhost:3000'); // 开发模式
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
```

## 3. IPC 通信

```javascript
// preload.js（预加载脚本）
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  onUpdate: (callback) => ipcRenderer.on('update', (_, data) => callback(data)),
});

// main.js（主进程处理）
ipcMain.handle('read-file', async (event, filePath) => {
  return fs.readFileSync(filePath, 'utf-8');
});

// renderer.js（渲染进程调用）
const content = await window.electronAPI.readFile('/path/to/file');
```

## 4. 打包发布

```javascript
// electron-builder 配置
// package.json
{
  "build": {
    "appId": "com.example.myapp",
    "mac": { "target": "dmg" },
    "win": { "target": "nsis" },
    "linux": { "target": "AppImage" }
  }
}
```

```bash
npx electron-builder --mac --win --linux
```

## 5. Electron 42.x 与 2026 版本演进

<!-- version-check: Electron 42.0.1, checked 2026-05-15 -->

> 🔄 更新于 2026-05-15

<!-- 修复于 2026-05-15: Electron 42.0.0 已于 2026-05-05 稳定发布，更新版本演进表 -->

### 版本演进

| 版本 | Chromium | Node.js | 关键变化 |
|------|----------|---------|---------|
| 36 | 136 | 22 | macOS Writing Tools/Autofill/Services 菜单集成 |
| 40 | 144 | 24.11 | `app.isHardwareAccelerationEnabled()`、RGBAF16 HDR 输出 |
| 41 | 146 | 24.15 | `allowExtensions` 自定义协议扩展、窗口 min/max 约束强制 |
| 42（稳定） | 148 | 24.15 | 2026-05-05 发布，最新稳定版 |
| 43 alpha | 149+ | 24.15 | 开发中 |

### Electron 41 新特性

```javascript
// 自定义协议支持 Chrome 扩展（41 新增）
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'myapp',
    privileges: {
      standard: true,
      secure: true,
      allowExtensions: true, // 新增：启用 Chrome 扩展
    },
  },
]);
```

### Tauri 2.0 替代方案

2026 年 Tauri 2.0 已成为 Electron 的主要竞争者，适合对包体积和内存敏感的场景：

| 对比项 | Electron 42 | Tauri 2.x |
|--------|------------|-----------|
| 安装包大小 | ~244 MB | ~8.6 MB |
| 内存占用 | 较高（Chromium） | 较低（系统 WebView） |
| 后端语言 | Node.js | Rust |
| 移动端支持 | ❌ | ✅（iOS/Android） |
| 生态成熟度 | 极高（VS Code、Slack） | 快速增长 |
| 学习曲线 | 低（纯 Web 技术） | 中（需了解 Rust） |

**选型建议**：
- 需要最大生态兼容性和 Node.js 原生模块 → Electron
- 追求小包体积、低内存、跨移动端 → Tauri 2.x
- 已有 Electron 项目 → 继续 Electron，无需迁移

来源：[Electron 42 Release](https://electronjs.org/blog/electron-42-0) | [Tauri vs Electron 2026](https://tech-insider.org/tauri-vs-electron-2026/)
