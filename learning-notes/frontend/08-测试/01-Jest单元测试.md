# Jest 单元测试
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础语法

```javascript
// sum.test.js
import { sum, multiply } from './math';

describe('Math utils', () => {
  // 基本测试
  it('should add two numbers', () => {
    expect(sum(1, 2)).toBe(3);
  });

  // 常用匹配器
  it('matchers', () => {
    expect(2 + 2).toBe(4);                    // 严格相等
    expect({ name: '张三' }).toEqual({ name: '张三' }); // 深度相等
    expect(null).toBeNull();
    expect(undefined).toBeUndefined();
    expect(1).toBeTruthy();
    expect(0).toBeFalsy();
    expect(10).toBeGreaterThan(5);
    expect('hello').toContain('ell');
    expect([1, 2, 3]).toContain(2);
    expect(() => { throw new Error('fail'); }).toThrow('fail');
  });
});
```

## 2. Mock 函数

```javascript
// Mock 函数
const mockFn = jest.fn();
mockFn.mockReturnValue(42);
mockFn.mockResolvedValue({ data: 'ok' });
mockFn.mockImplementation((x) => x * 2);

expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith('arg');
expect(mockFn).toHaveBeenCalledTimes(1);

// Mock 模块
jest.mock('./api', () => ({
  fetchUser: jest.fn().mockResolvedValue({ id: 1, name: '张三' }),
}));

// Spy
const spy = jest.spyOn(console, 'log');
doSomething();
expect(spy).toHaveBeenCalledWith('expected message');
spy.mockRestore();
```

## 3. 异步测试

```javascript
// async/await
it('fetches user data', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('张三');
});

// resolves/rejects
it('resolves with data', () => {
  return expect(fetchUser(1)).resolves.toEqual({ id: 1, name: '张三' });
});

it('rejects with error', () => {
  return expect(fetchUser(-1)).rejects.toThrow('Not found');
});
```

## 4. 生命周期

```javascript
describe('Database tests', () => {
  beforeAll(async () => { await db.connect(); });
  afterAll(async () => { await db.disconnect(); });
  beforeEach(async () => { await db.clear(); });
  afterEach(() => { jest.restoreAllMocks(); });

  it('should create user', async () => { /* ... */ });
});
```

## 5. Vitest（Vite 项目推荐）

<!-- version-check: Vitest 4.1, Jest 30, checked 2026-05-13 -->

> 🔄 更新于 2026-05-13：补充 Vitest 4.x 与 Jest 30 重大版本更新

```javascript
// vitest 与 jest API 基本兼容
import { describe, it, expect, vi } from 'vitest';

const mockFn = vi.fn();
vi.mock('./api');
vi.spyOn(console, 'log');

// 优势：
// - 与 Vite 共享配置，开箱即用
// - 原生 ESM 支持
// - 更快的执行速度
// - 兼容 Jest API
```

### 5.1 Vitest 4.x 新特性（2025-10 / 2026-01）

来源：[Vitest 4.0 Announcement](https://voidzero.dev/posts/announcing-vitest-4)、[Vitest 4.1](https://main.vitest.dev/blog/vitest-4-1)

```javascript
// 1. Browser Mode（稳定）— 在真实浏览器中运行测试
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: 'playwright',  // 或 'webdriverio'
      instances: [
        { browser: 'chromium' },
        { browser: 'firefox' },
      ],
    },
  },
});

// 2. Visual Regression Testing（视觉回归）
import { expect, test } from 'vitest';
import { page } from '@vitest/browser/context';

test('button looks correct', async () => {
  await expect(page.getByRole('button')).toMatchScreenshot();
});

// 3. Test Tags（4.1 新增）— 标签过滤与分组配置
test('login flow', { tag: ['e2e', 'critical'] }, async () => {
  // ...
});
// 命令行：vitest --tag e2e

// 4. AI Agent Reporter（4.1 新增）— 为 AI Coding Agent 优化的报告格式
// 命令行：vitest --reporter=agent

// 5. Playwright Trace 集成 — 失败时自动生成可回放的 trace
```

### 5.2 Jest 30 新特性（2025-06）

来源：[Jest 30 Release](https://jestjs.io/blog/2025/06/04/jest-30)

```javascript
// 主要变化：
// - 最低 Node.js 版本：18.x（移除 14/16/19/21 支持）
// - 最低 TypeScript 版本：5.4
// - 性能：内存占用降低、执行速度提升
// - ESM 支持改进（更接近原生 ESM）
// - expect API 重构

// 升级建议：
// - Vite 项目 → Vitest 4.x（更快、原生 ESM、Browser Mode）
// - 已有 Jest 项目 → Jest 30（迁移成本低）
// - 新项目 → 优先 Vitest
```
## 🎬 推荐视频资源

- [Traversy Media - Jest Crash Course](https://www.youtube.com/watch?v=7r4xVDI2vho) — Jest速成
- [freeCodeCamp - JavaScript Testing](https://www.youtube.com/watch?v=FgnxcUQ5vho) — JavaScript测试完整课程
