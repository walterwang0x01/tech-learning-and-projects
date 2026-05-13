# Node.js 基础与模块系统
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 事件循环

<!-- version-check: Node.js 24.15.0 LTS, checked 2026-05-13 -->
<!-- 修复于 2026-05-13: 24.14.1 → 24.15.0（2026-04-15 发布）；补充 Node.js 26 Current -->

> 🔄 更新于 2026-05-13：Node.js 24（Krypton）是当前 Active LTS 版本（2025-10-28 进入 LTS，支持至 2028-04），搭载 V8 13.6、npm 11（安装速度提升 65%）、Undici 7。Node.js 26.0.0（Current）已于 2026-05-05 发布，搭载 V8 14.6、Undici 8、Temporal API 默认启用。

来源：[Node.js 24.15.0 LTS](https://nodejs.org/en/blog/release/v24.15.0)、[Node.js 26.0.0 Current](https://nodejs.org/en/blog/release/v26.0.0)

```
   ┌───────────────────────────┐
┌─>│           timers          │  ← setTimeout, setInterval
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │  ← I/O 回调
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           poll            │  ← 获取新的 I/O 事件
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           check           │  ← setImmediate
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
└──┤      close callbacks      │  ← socket.on('close')
   └───────────────────────────┘

微任务（process.nextTick > Promise.then）在每个阶段之间执行
```

## 2. 模块系统

```javascript
// CommonJS（Node.js 传统方式）
const fs = require('fs');
module.exports = { add, subtract };
module.exports = function main() {};

// ESM（推荐，package.json 中设置 "type": "module"）
import fs from 'node:fs';
import { readFile } from 'node:fs/promises';
export function add(a, b) { return a + b; }
export default class Calculator {}
```

## 3. 核心模块

```javascript
// fs 文件系统
import { readFile, writeFile, mkdir, readdir, stat } from 'node:fs/promises';

const content = await readFile('file.txt', 'utf-8');
await writeFile('output.txt', 'hello');
await mkdir('new-dir', { recursive: true });
const files = await readdir('./src');

// path 路径
import path from 'node:path';
path.join('/user', 'docs', 'file.txt');  // /user/docs/file.txt
path.resolve('src', 'index.js');          // 绝对路径
path.extname('file.txt');                 // .txt
path.basename('/path/file.txt');          // file.txt
path.dirname('/path/file.txt');           // /path

// Stream 流
import { createReadStream, createWriteStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
import { createGzip } from 'node:zlib';

await pipeline(
  createReadStream('input.txt'),
  createGzip(),
  createWriteStream('input.txt.gz'),
);

// Buffer
const buf = Buffer.from('Hello', 'utf-8');
buf.toString('base64');  // SGVsbG8=
Buffer.alloc(1024);      // 分配 1KB

// child_process
import { exec, spawn } from 'node:child_process';
import { execSync } from 'node:child_process';

const output = execSync('ls -la', { encoding: 'utf-8' });

// Worker Threads
import { Worker, isMainThread, parentPort } from 'node:worker_threads';

if (isMainThread) {
  const worker = new Worker(new URL('./worker.js', import.meta.url));
  worker.postMessage({ data: 'hello' });
  worker.on('message', (result) => console.log(result));
} else {
  parentPort.on('message', (msg) => {
    parentPort.postMessage({ result: msg.data.toUpperCase() });
  });
}
```

## 4. 环境变量与配置

```javascript
// 使用 dotenv
import 'dotenv/config';
const port = process.env.PORT || 3000;
const dbUrl = process.env.DATABASE_URL;

// process 对象
process.argv;     // 命令行参数
process.cwd();    // 当前工作目录
process.env;      // 环境变量
process.exit(0);  // 退出进程
process.pid;      // 进程ID
process.memoryUsage(); // 内存使用
```
## 🎬 推荐视频资源

- [freeCodeCamp - Node.js Full Course](https://www.youtube.com/watch?v=Oe421EPjeBE) — Node.js完整课程
- [Traversy Media - Node.js Crash Course](https://www.youtube.com/watch?v=fBNz5xF-Kx4) — Node.js速成
- [Fireship - Node.js in 100 Seconds](https://www.youtube.com/watch?v=ENrzD9HAZK4) — Node.js快速了解
### 📺 B站（Bilibili）
- [黑马程序员 - Node.js教程](https://www.bilibili.com/video/BV1a34y167AZ) — Node.js完整中文教程
- [尚硅谷 - Node.js教程](https://www.bilibili.com/video/BV1gM411W7ex) — Node.js深入讲解
