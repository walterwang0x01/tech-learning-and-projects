# E2E 测试 Cypress / Playwright
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Playwright（推荐）

```javascript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

```javascript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Login', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('用户名').fill('admin');
    await page.getByLabel('密码').fill('123456');
    await page.getByRole('button', { name: '登录' }).click();

    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('用户名').fill('wrong');
    await page.getByLabel('密码').fill('wrong');
    await page.getByRole('button', { name: '登录' }).click();

    await expect(page.getByText('用户名或密码错误')).toBeVisible();
  });
});

// API 拦截（handler 应为 async 并 await route.fulfill，避免响应未完全处理）
test('mock API response', async ({ page }) => {
  await page.route('/api/users', async (route) => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify([{ id: 1, name: '张三' }]),
    });
  });
  await page.goto('/users');
  await expect(page.getByText('张三')).toBeVisible();
});
```

## 2. Cypress

<!-- version-check: Cypress 15.10+ (v16 尚未发布，env() 废弃状态不变), checked 2026-07-10 -->

> 🔄 更新于 2026-05-13：补充 Cypress 15.10+ 环境变量 API 迁移

```javascript
// cypress/e2e/login.cy.js
describe('Login', () => {
  beforeEach(() => { cy.visit('/login'); });

  it('should login successfully', () => {
    cy.get('[data-testid="username"]').type('admin');
    cy.get('[data-testid="password"]').type('123456');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
    cy.contains('欢迎回来').should('be.visible');
  });

  // 网络拦截
  it('should handle API error', () => {
    cy.intercept('POST', '/api/login', { statusCode: 401, body: { message: '认证失败' } });
    cy.get('[data-testid="username"]').type('wrong');
    cy.get('[data-testid="password"]').type('wrong');
    cy.get('button[type="submit"]').click();
    cy.contains('认证失败').should('be.visible');
  });
});
```

### 2.1 Cypress 15.10+ 环境变量 API 迁移

`Cypress.env()` 在 v15.10.0 已标记废弃，将在 v16 移除。原因：旧 API 会把所有环境变量序列化到浏览器上下文，可能意外暴露敏感数据。

来源：[Cypress 15.10.0 Migration Guide](https://docs.cypress.io/guides/references/migration-guide)

```javascript
// ❌ 旧用法（已废弃）
const apiKey = Cypress.env('API_KEY');

// ✅ 新用法 1：cy.env() — 用于敏感数据（按需获取，不进浏览器上下文）
cy.env('API_KEY').then((apiKey) => {
  cy.request({
    url: '/api/data',
    headers: { Authorization: `Bearer ${apiKey}` },
  });
});

// ✅ 新用法 2：Cypress.expose() — 用于公开/非敏感配置（同步访问）
// cypress.config.js 中预先暴露
// e.g. Cypress.expose({ FEATURE_FLAG: true })
const flag = Cypress.expose('FEATURE_FLAG');
```

迁移建议：敏感值（密钥/Token/密码）用 `cy.env()`，配置/特性开关用 `Cypress.expose()`。

## 3. Playwright Screencast API（1.59 引入，1.61 增强）

> 🔄 更新于 2026-07-10

<!-- version-check: Playwright 1.61.1（当前最新稳定版）, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: Playwright 已从 1.59.x 更新到 1.61.1，补充 1.61 新增的 showActions cursor 选项与 onFrame timestamp -->

### 3.1 Screencast API — Agentic 视频回执

Playwright 1.59 新增 `page.screencast` API，为 AI Agent 工作流提供视频录制和注解能力，1.61 进一步增强（`showActions` 新增 `cursor` 光标动画选项，`onFrame` 回调新增帧时间戳）。Agent 完成任务后可以录制验证视频作为"回执"，比文本日志更直观。来源：[Playwright Release Notes](https://playwright.dev/docs/release-notes)

```javascript
// 基础录制
await page.screencast.start({ path: 'video.webm' });
// ... 执行操作 ...
await page.screencast.stop();

// 动作注解 — 高亮交互元素并显示操作标题
await page.screencast.showActions({ position: 'top-right' });

// 章节标题 — 为视频添加上下文说明
await page.screencast.showChapter('验证结账流程', {
  description: '根据工单 #1234 添加优惠券支持',
  duration: 1000,
});

// Agentic 视频回执 — Agent 录制验证视频供人工审查
await page.screencast.start({ path: 'receipt.webm' });
await page.screencast.showActions({ position: 'top-right' });
await page.screencast.showChapter('验证优惠券功能');
await page.locator('#coupon').fill('SAVE20');
await page.locator('#apply-coupon').click();
await expect(page.locator('.discount')).toContainText('20%');
await page.screencast.showChapter('完成', {
  description: '优惠券已应用，折扣已反映在总价中',
});
await page.screencast.stop();

// 实时帧捕获 — 流式 JPEG 帧用于 AI 视觉分析
await page.screencast.start({
  onFrame: (frame) => sendToVisionModel(frame.data),
});
```

### 3.2 交互式定位器选择

```javascript
// page.pickLocator() — 悬停高亮元素，点击获取 Locator
const locator = await page.pickLocator();
// 取消选择
await page.cancelPickLocator();

// locator.normalize() — 将定位器转换为最佳实践格式（test id、aria role）
const normalized = locator.normalize();
```

### 3.3 其他改进

- `browserContext.setStorageState()` — 清除并设置新的存储状态，无需创建新上下文
- `browserContext.debugger` — 编程式控制 Playwright 调试器
- `tracing.start({ live: true })` — 实时 trace 更新
- `response.httpVersion()` — 获取响应使用的 HTTP 版本

## 4. 对比

| 特性 | Playwright | Cypress |
|------|-----------|---------|
| 多浏览器 | Chromium/Firefox/WebKit | Chromium/Firefox/WebKit |
| 多标签页 | 支持 | 不支持 |
| 自动等待 | 内置 | 内置 |
| 并行执行 | 原生支持 | 需要付费 |
| API 测试 | 支持 | 支持 |
| 语言 | JS/TS/Python/Java/C# | JS/TS |
| Screencast API | ✅（1.59+，1.61 增强） | ❌ |
| Agent 集成 | ✅（视频回执） | ❌ |
