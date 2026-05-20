# 浏览器自动化 Agent 详解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

浏览器自动化 Agent 从传统 DOM 脚本演进到视觉驱动的自主 Agent。

```
演进路径：Selenium 脚本 → MCP 工具集成 → 独立 Agent 框架（视觉+自主决策）
```

## 2. Browser-Use — 最推荐，基准最高

> 🔄 更新于 2026-04-21

开源浏览器自动化框架，83K+ Stars，SDK 3.0 + CLI 2.0 重大更新。API V3 在 Online-Mind2Web 基准测试达到 SOTA。来源：[Browser-Use Changelog](https://browser-use.com/changelog)

<!-- version-check: Browser-Use SDK 3.0, CLI 2.0, checked 2026-04-21 -->

**SDK 3.0 重大变化**（2026-02-25）：
- 全新 `client.run()` API（Breaking Change）
- BU Agent API：类似 Claude Code 的浏览器 Agent，支持多步骤工作流
- Code Mode：Agent 生成可复用 Python 脚本，可用于 cron 任务
- BYOK：使用自己的 LLM API Key
- Sensitive Data：安全传递密钥，不进入日志和录制

**CLI 2.0**（2026-03-22）：
- 终端直接运行：`pip install browser-use-cli`
- 与 Claude Code、Cursor 等 AI 编码工具集成
- 同步真实浏览器配置（cookies、sessions）
- Stealth 升级：Chromium 146、hCaptcha 求解器、reCAPTCHA 准确率提升
- 开源 stealth 基准测试（80 个反机器人网站）

**Cloud 免费层**（2026-04-03）：
- 免费浏览器会话，无需信用卡
- Agent 可通过 CLI 自助注册 Cloud 账户
- 代理数据成本 $10/GB → $5/GB

> 🔄 更新于 2026-05-20: Browser Use Cloud Python SDK 已独立为 `browser-use-sdk` 包（PyPI 2026-04-04），使用 `client.run()` 新 API。下面的代码示例为开源 `browser-use` 包（仍活跃维护）的本地用法，两者并存。
>
> Cloud SDK 用法：
> ```python
> from browser_use_sdk import AsyncBrowserUse
> client = AsyncBrowserUse()
> result = await client.run("Find the top 3 trending repos on GitHub today")
> ```

<!-- 修复于 2026-05-20: gpt-4o 已退役（ChatGPT 2026-02-13 退役，API 仍可用但不推荐），改为 gpt-5.2 -->

```python
from browser_use import Agent, Controller
from langchain_openai import ChatOpenAI

# 基本用法
agent = Agent(
    task="去 GitHub Trending，筛选 Python，提取前 5 个项目名称和 Star 数",
    llm=ChatOpenAI(model="gpt-5.2"),
    max_actions_per_step=5,
)
result = await agent.run()

# 自定义 Action + Claude 后端
controller = Controller()

@controller.action("保存结果到文件")
def save_to_file(content: str, filename: str):
    with open(filename, "w") as f:
        f.write(content)

agent = Agent(
    task="搜索 AI Agent 框架，对比特点，保存到 report.md",
    llm=ChatAnthropic(model="claude-sonnet-4-6-20260217"),
    controller=controller,
)
```

## 3. Skyvern — 视觉驱动，适合复杂网站

使用计算机视觉而非 DOM 解析，不怕 UI 变化，能处理 CAPTCHA。

```
工作原理：浏览器截图 → 视觉模型理解页面 → 生成操作指令 → 执行并验证
```

```python
client = skyvern.Skyvern(api_key="your-api-key")
task = client.tasks.create(
    url="https://example.com/apply",
    goal="填写申请表单，姓名 John Doe，邮箱 john@example.com",
)
```

## 4. Agent-Browser — Vercel 出品，轻量 CLI

TypeScript 编写，极简 API，适合轻量级 Agent 场景。

```typescript
import { createBrowser } from "@anthropic-ai/agent-browser";
const browser = await createBrowser();
const page = await browser.newPage();
await page.act("导航到 Hacker News");
const title = await page.extract("提取文章标题");
```

## 5. Agent-S — GUI Agent，超越人类表现

通用计算机使用 Agent，OSWorld 基准测试超越人类，不仅限于浏览器。

```
架构：经验学习 + 自主探索 → 多模态推理 → OS 级控制（鼠标/键盘/窗口）
```

## 6. Page-Agent — 阿里巴巴，网站 AI 原生化

将任何网站变成 AI 原生应用，Agent 直接与网页交互而非通过 API。

## 7. 综合对比表

| 工具 | 方式 | 语言 | 最佳场景 | Stars | 自托管 | 云端 |
|------|------|------|----------|-------|--------|------|
| Browser-Use | DOM+视觉混合 | Python | 通用浏览器自动化 | 83k+ | ✅ | ✅ |
| Skyvern | 纯视觉驱动 | Python | 复杂动态网站 | 20k+ | ✅ | ✅ |
| Agent-Browser | DOM 操作 | TypeScript | 轻量级 Agent | 3k+ | ✅ | ❌ |
| Agent-S | GUI/截图 | Python | 通用计算机操作 | 5k+ | ✅ | ❌ |
| Page-Agent | 网页 AI 化 | TypeScript | 网站 AI 原生化 | 2k+ | ✅ | ❌ |

与已有工具对比（详见 → [Computer Use与浏览器Agent](./02-Computer%20Use与浏览器Agent.md)）：

| 工具 | 类型 | 适用场景 |
|------|------|----------|
| Claude Computer Use | 通用 GUI | 任何桌面应用 |
| Nova Act SDK | 浏览器专用 | 语义化浏览器工作流 |
| Playwright/Puppeteer MCP | MCP 工具 | Agent 调用浏览器 |
| Browserbase / Steel | 云基础设施 | 云端浏览器实例 |

## 8. 选型决策树

```
需要浏览器自动化？
├─ 已有 MCP 环境？ → Playwright MCP（最简集成）
├─ 需要通用计算机操作？ → Claude Computer Use / Agent-S
├─ 目标网站复杂（CAPTCHA/动态）？ → Skyvern
├─ TypeScript 项目？ → Agent-Browser
├─ 需要云端大规模运行？ → Browser-Use + Browserbase
└─ 通用推荐 → Browser-Use（基准最高，生态最好）
```

## 9. 安全注意事项

```
├─ 沙箱隔离：始终在容器中运行浏览器
├─ URL 白名单：限制可访问域名
├─ 凭证管理：使用 Vault，不硬编码
├─ 超时控制：设置最大执行时间
└─ 人工兜底：关键操作（支付/删除）需确认
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [Browser-Use - Getting Started](https://www.youtube.com/watch?v=dcgRMOG605w) — Browser-Use入门
- [Skyvern - AI Browser Automation](https://www.youtube.com/watch?v=YtiYrmAdJ5g) — Skyvern演示

### 📖 官方文档
- [Browser-Use](https://browser-use.com/) — Browser-Use官网
- [Skyvern](https://github.com/Skyvern-AI/skyvern) — Skyvern GitHub
