# Node.js 日志最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 日志库对比

<!-- version-check: pino 10.3.1（最新稳定版）, winston 3.x, pino-http 10.x, checked 2026-07-10 -->

| 特性 | pino | winston | Bunyan | console |
|------|------|---------|--------|---------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| JSON 原生 | ✅ | 需配置 | ✅ | ❌ |
| Transport | Worker Thread | 同步/异步 | Stream | 无 |
| 推荐场景 | 高性能服务 | 通用项目 | 已停更 | 仅开发 |

## 2. pino（推荐）

```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV !== 'production'
    ? { target: 'pino-pretty', options: { colorize: true } }
    : undefined,
  base: { service: 'user-api', env: process.env.NODE_ENV },
  redact: ['req.headers.authorization', 'password', 'token'],
});

logger.info({ userId: 10086, action: 'login' }, '用户登录成功');
logger.error({ err, orderId: 'ORD-001' }, '订单处理失败');

// 子 logger：自动继承父级字段
const childLog = logger.child({ module: 'payment' });
childLog.info({ amount: 99.9 }, '支付发起');
```

## 3. winston 配置

```typescript
import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json(),
  ),
  defaultMeta: { service: 'user-api' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(winston.format.colorize(), winston.format.simple()),
    }),
    new DailyRotateFile({
      filename: 'logs/app-%DATE%.log', datePattern: 'YYYY-MM-DD',
      maxSize: '100m', maxFiles: '14d',
    }),
    new DailyRotateFile({
      filename: 'logs/error-%DATE%.log', level: 'error', maxFiles: '30d',
    }),
  ],
});
```

## 4. 请求日志中间件

```typescript
// Express + pino-http
import pinoHttp from 'pino-http';

app.use(pinoHttp({
  logger,
  customLogLevel: (req, res, err) => {
    if (res.statusCode >= 500 || err) return 'error';
    if (res.statusCode >= 400) return 'warn';
    return 'info';
  },
  redact: ['req.headers.authorization', 'req.headers.cookie'],
}));

// Fastify 内置 pino
const app = Fastify({ logger: { level: 'info' } });
// request.log 自带 reqId，自动关联请求上下文
```

## 5. 日志级别规范

| 级别 | 场景 | 示例 |
|------|------|------|
| fatal | 进程即将崩溃 | 数据库连接池耗尽 |
| error | 操作失败 | 第三方 API 调用失败 |
| warn | 异常但可恢复 | 缓存未命中、重试成功 |
| info | 关键业务事件 | 用户注册、订单创建 |
| debug | 开发调试 | SQL 查询、缓存命中 |

## 6. AsyncLocalStorage 请求上下文

```typescript
// 类似 Java MDC，在异步调用链中传递上下文
import { AsyncLocalStorage } from 'node:async_hooks';

interface RequestContext { requestId: string; userId?: string }
export const als = new AsyncLocalStorage<RequestContext>();

// Express 中间件
app.use((req, res, next) => {
  const ctx = { requestId: req.headers['x-request-id'] as string || crypto.randomUUID() };
  als.run(ctx, () => next());
});

// 任意深层调用中获取上下文
function getLogger() {
  const ctx = als.getStore();
  return logger.child({ requestId: ctx?.requestId, userId: ctx?.userId });
}
```

## 7. 前端日志与错误上报

```typescript
class BrowserLogger {
  private buffer: Array<{ level: string; msg: string; ts: number }> = [];

  error(msg: string, error?: Error) {
    console.error(`[ERROR] ${msg}`, error);
    this.buffer.push({ level: 'error', msg, ts: Date.now() });
    this.flush(); // 错误立即上报
  }

  flush() {
    if (!this.buffer.length) return;
    navigator.sendBeacon('/api/logs', JSON.stringify(this.buffer));
    this.buffer = [];
  }
}

// Sentry 错误追踪
import * as Sentry from '@sentry/react';
Sentry.init({
  dsn: 'https://xxx@sentry.io/123',
  tracesSampleRate: 0.1,
  beforeSend(event) {
    if (event.request?.headers) delete event.request.headers['Authorization'];
    return event;
  },
});
```

## 8. 日志轮转

```typescript
// pino-roll
const logger = pino({
  transport: {
    target: 'pino-roll',
    options: { file: 'logs/app', frequency: 'daily', size: '100m', limit: { count: 14 } },
  },
});
```

## 9. 生产环境配置

```typescript
const isProd = process.env.NODE_ENV === 'production';

export const logger = pino({
  level: isProd ? 'info' : 'debug',
  ...(isProd ? {} : { transport: { target: 'pino-pretty' } }),
  formatters: { level: (label) => ({ level: label }) },
  base: { service: process.env.SERVICE_NAME, version: process.env.APP_VERSION },
});
// Docker/K8s：输出到 stdout，由日志收集器（Fluentd/Loki）采集，不要在容器内写文件
```
