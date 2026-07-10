# Node.js 性能优化
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 内存泄漏排查

```javascript
// 使用 --inspect 启动
// node --inspect server.js
// Chrome DevTools → Memory → Heap Snapshot

// 常见内存泄漏原因
// 1. 全局变量累积
// 2. 闭包引用未释放
// 3. 事件监听器未移除
// 4. 定时器未清理
// 5. 大数组/对象缓存无上限

// 使用 LRU 缓存限制大小
import { LRUCache } from 'lru-cache';
const cache = new LRUCache({ max: 500, ttl: 1000 * 60 * 5 });
```

## 2. Worker Threads

```javascript
// CPU 密集型任务使用 Worker Threads
import { Worker } from 'node:worker_threads';

function runWorker(data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./heavy-task.js', { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
  });
}

// 使用 worker pool（piscina）
import Piscina from 'piscina';
const pool = new Piscina({ filename: './worker.js', maxThreads: 4 });
const result = await pool.run({ data: 'input' });
```

## 3. Stream 流式处理

```javascript
// 避免一次性加载大文件到内存
import { createReadStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';

// 流式响应
app.get('/api/export', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  const cursor = db.collection('users').find().stream();
  cursor.pipe(new CSVTransform()).pipe(res);
});
```

## 4. PM2 进程管理

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'api',
    script: 'dist/server.js',
    instances: 'max',     // 使用所有 CPU 核心
    exec_mode: 'cluster',
    max_memory_restart: '1G',
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000,
    },
  }],
};
```

```bash
pm2 start ecosystem.config.js --env production
pm2 monit     # 监控
pm2 logs      # 查看日志
pm2 reload all # 零停机重启
```

## 5. Node.js 24 LTS 性能改进

> 🔄 更新于 2026-07-10

<!-- version-check: Node.js 24.18.0 LTS (Krypton), Node.js 26.5.0 Current, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: 24.15.0 → 24.18.0；26.0.0 → 26.5.0 -->

Node.js 24 LTS（代号 Krypton）带来了显著的性能改进：

### 5.1 V8 13.6 引擎优化

```javascript
// Node.js 24 内置 V8 13.6，JS 执行速度提升
// 主要改进：
// - Maglev JIT 编译器优化，中间层编译更快
// - 正则表达式性能提升
// - JSON.parse 大对象性能改善

// npm 11 安装速度提升 65%
// 推荐使用 corepack 管理包管理器
```

### 5.2 诊断工具增强

```javascript
// Node.js 24 内置诊断报告（无需第三方工具）
// 生成诊断报告
// node --report-on-fatalerror server.js

// 使用 node:diagnostics_channel 追踪性能
import diagnostics_channel from 'node:diagnostics_channel';

const channel = diagnostics_channel.channel('http.server.request');
channel.subscribe((message) => {
  console.log(`请求: ${message.request.method} ${message.request.url}`);
  console.log(`耗时: ${message.duration}ms`);
});
```

### 5.3 2026 年 Node.js 性能优化清单

| 优化项 | 工具/方法 | 影响 |
|--------|----------|------|
| 升级到 Node.js 24 LTS | V8 13.6 + npm 11 | JS 执行更快，安装提速 65% |
| Worker Threads | piscina / workerpool | CPU 密集任务不阻塞事件循环 |
| Stream 处理 | node:stream/promises | 大文件处理内存恒定 |
| LRU 缓存 | lru-cache | 避免无限增长的内存缓存 |
| 集群模式 | PM2 cluster / node:cluster | 利用多核 CPU |
| 诊断通道 | node:diagnostics_channel | 零开销性能追踪 |

> 来源：[Node.js v22 to v24 Migration](https://nodejs.org/es/blog/migrations/v22-to-v24)
