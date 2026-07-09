# OpenClaw 平台详解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

OpenClaw 是一个开源的 Agent 编排平台，核心理念是通过模块化 Skills 系统快速构建可部署到 20+ 消息渠道的 AI Agent。支持自托管，提供 ClawHub Skills 市场。

```
┌──────────────────── OpenClaw ────────────────────┐
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  Skills   │  │ Heartbeat│  │    Memory      │  │
│  │ 模块化技能 │  │ 心跳调度  │  │  记忆系统      │  │
│  │ Markdown  │  │ 定时任务  │  │  短期+长期     │  │
│  └──────────┘  └──────────┘  └────────────────┘  │
│  ┌──────────────────────────────────────────────┐ │
│  │              Channels（渠道层）                 │ │
│  │  WhatsApp│Telegram│Slack│Discord│Teams│iMessage│ │
│  │  Signal │Email  │SMS  │Web   │API  │20+     │ │
│  └──────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────┐ │
│  │         ClawHub Skills Marketplace            │ │
│  └──────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

## 2. 核心架构

### Skills 系统

Skills 是 OpenClaw 的核心扩展机制，使用 Markdown 文件定义 Agent 的能力和行为指令。

```markdown
# skill.md（Skill 定义文件示例）

## Identity
You are a scheduling assistant. Help users manage their calendar.

## Capabilities
- Create, update, and delete calendar events
- Check availability for meeting times
- Send meeting invitations

## Rules
- Always confirm before creating events
- Use the user's timezone
- Don't schedule meetings before 9am or after 6pm

## Tools
- google_calendar: Create and manage calendar events
- email: Send meeting invitations
```

```yaml
# skill.yaml（Skill 配置）
name: calendar-assistant
version: 1.0.0
description: Calendar management skill
author: community
tools:
  - google_calendar
  - email
env:
  - GOOGLE_CALENDAR_API_KEY
  - SMTP_HOST
```

### Heartbeat（心跳调度）

```yaml
# 定时任务配置
heartbeat:
  - name: daily-summary
    cron: "0 9 * * *"          # 每天早上 9 点
    action: "生成今日待办摘要并发送给用户"

  - name: weekly-report
    cron: "0 10 * * 1"         # 每周一上午 10 点
    action: "生成上周工作总结报告"

  - name: health-check
    interval: 300              # 每 5 分钟
    action: "检查监控指标，异常时告警"
```

### Memory 系统

```
Memory 层级：
├─ 短期记忆：当前对话上下文
├─ 长期记忆：跨会话的用户偏好和历史
├─ 共享记忆：多 Agent 间共享的知识
└─ 向量记忆：语义检索的知识库
```

## 3. 渠道集成

```python
# 多渠道配置示例
channels:
  whatsapp:
    enabled: true
    phone_number_id: "xxx"
    access_token: "xxx"

  telegram:
    enabled: true
    bot_token: "xxx"

  slack:
    enabled: true
    bot_token: "xoxb-xxx"
    app_token: "xapp-xxx"

  discord:
    enabled: true
    bot_token: "xxx"

  teams:
    enabled: true
    app_id: "xxx"
    app_password: "xxx"

  web:
    enabled: true
    port: 3000
    cors_origins: ["https://myapp.com"]
```

## 4. Sub-Agents 系统

```yaml
# 主 Agent 配置
agent:
  name: main-assistant
  model: gpt-5.2  # 修复于 2026-05-20: gpt-4o 已退役，统一升级为 gpt-5.2 系列
  skills:
    - general-chat
    - task-router

  sub_agents:
    - name: code-helper
      model: claude-sonnet-4-6-20260217
      skills: [code-review, code-generation]
      trigger: "当用户询问编程相关问题时"

    - name: data-analyst
      model: gpt-5.2
      skills: [sql-query, data-visualization]
      trigger: "当用户需要数据分析时"

    - name: scheduler
      model: gpt-5-mini
      skills: [calendar-assistant]
      trigger: "当用户需要日程管理时"
```

## 5. ClawHub Skills 市场

```bash
# 从 ClawHub 安装 Skill
openclaw skill install web-browsing
openclaw skill install email-manager
openclaw skill install code-executor
openclaw skill install file-manager

# 常用 Skills
# ├─ web-browsing     — 网页浏览和信息提取
# ├─ email-manager    — 邮件收发和管理
# ├─ calendar         — 日历和日程管理
# ├─ file-manager     — 文件操作
# ├─ code-executor    — 代码执行沙箱
# ├─ image-gen        — 图片生成
# ├─ voice            — 语音交互
# └─ knowledge-base   — 知识库问答
```

## 6. 自托管部署

```bash
# Docker 部署
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 配置环境变量
cp .env.example .env
# 编辑 .env 设置 API Key、数据库等

# 启动
docker-compose up -d

# 服务组成
# ├─ openclaw-core    — 核心引擎
# ├─ openclaw-web     — Web UI
# ├─ redis            — 缓存和消息队列
# └─ postgres         — 持久化存储
```

## 7. 安全模型

```
安全层级：
├─ 工具权限：每个 Skill 声明所需权限
├─ 用户认证：渠道级别的用户身份验证
├─ 数据隔离：用户数据严格隔离
├─ 沙箱执行：代码执行在隔离沙箱中
├─ 审计日志：所有操作记录可追溯
└─ 速率限制：防止滥用的请求限制
```

## 8. 与其他平台对比

| 特性 | OpenClaw | Dify | Coze | n8n |
|------|----------|------|------|-----|
| 类型 | Agent 编排 | LLM 应用平台 | Bot 构建 | 工作流自动化 |
| 开源 | ✅ | ✅ | ❌ | ✅ |
| Skills 市场 | ClawHub | 模板市场 | 插件商店 | 社区节点 |
| 消息渠道 | 20+ | API/Web | 多平台 | Webhook |
| 自托管 | ✅ | ✅ | ❌ | ✅ |
| 多 Agent | Sub-Agents | 工作流 | Bot 嵌套 | AI Agent 节点 |
| 定时任务 | Heartbeat | ❌ | 定时触发 | Cron 触发 |
| 适用场景 | 个人/团队助手 | 企业 AI 应用 | 快速 Bot | 自动化流程 |

> 更新于 2026-07-09

### 2026 年 6 月 OpenClaw 浏览器与生产实践

**OpenClaw 2026.6.x** 将浏览器自动化作为一等公民能力，通过 Gateway 内嵌 CDP 控制服务实现：

| 模式 | Profile | 适用场景 |
| ---- | ------- | -------- |
| **Managed** | `openclaw`（默认） | 隔离用户数据目录，干净会话，适合大多数自动化 |
| **Attached** | `user` | 附着已登录 Chrome（Gmail/GitHub/内网仪表盘） |
| **Remote CDP** | 自定义 profile | Docker/Browserless/远程节点，Gateway 代理到 node host |

**新增 `browser-automation` Skill**（随 2026.6 捆绑）：

- 操作循环：check status/tabs → 标注任务 tab → snapshot → act → resnapshot
- stale ref 恢复一次；登录/2FA/captcha 上报为 manual action 而非盲猜
- CLI：`openclaw browser start`、`openclaw browser --browser-profile user tabs`

**生产部署要点**（Context Studios 2026 实践）：

- 多 Agent 分工：一个 Agent 写内容，另一个通过 `user` profile 操作 LinkedIn 企业页
- 浏览器状态跨交互持久化，适合多步 dashboard 提取 → Slack 摘要工作流
- 与 134+ MCP 工具组合：浏览器取证 + 文件系统 + 定时 Heartbeat

```yaml
# ~/.openclaw/openclaw.json 浏览器块示例
browser:
  defaultProfile: openclaw
  profiles:
    openclaw:
      headless: true
    user:
      cdpUrl: "http://127.0.0.1:9222"  # 已开启 remote debugging 的 Chrome
```

> 来源：[OpenClaw Browser 文档](https://docs.openclaw.ai/cli/browser)、[unpkg openclaw@2026.6.9 browser.md](https://unpkg.com/openclaw@2026.6.9/docs/tools/browser.md)、[OpenClaw 生产指南](https://www.contextstudios.ai/blog/the-complete-openclaw-guide-how-we-run-an-ai-agent-in-production-2026)

## 🎬 推荐视频资源

### 📖 官方文档
- [OpenClaw GitHub](https://github.com/openclaw/openclaw) — OpenClaw开源项目
- [OpenFang GitHub](https://github.com/RightNow-AI/openfang) — OpenFang Agent运行时
