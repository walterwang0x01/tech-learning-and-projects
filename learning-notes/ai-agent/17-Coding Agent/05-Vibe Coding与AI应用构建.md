# Vibe Coding 与 AI 应用构建
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

Vibe Coding 是 Andrej Karpathy（OpenAI 联合创始人）在 2025 年初提出的概念："你描述你想要什么，AI 来构建它"。与传统 Coding Agent（辅助开发者写代码）不同，Vibe Coding 面向非开发者或快速原型场景，用自然语言直接生成完整应用。

```
┌─────────────── Coding 工具光谱 ───────────────┐
│                                                 │
│  非开发者友好 ←──────────────────→ 开发者专业   │
│                                                 │
│  Vibe Coding        IDE Agent       终端 Agent  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │ Replit    │    │ Cursor   │    │Claude Code│ │
│  │ Bolt.new  │    │ Kiro     │    │ Codex    │ │
│  │ Lovable   │    │ Windsurf │    │ Aider    │ │
│  │ v0        │    │ Copilot  │    │          │ │
│  └──────────┘    └──────────┘    └──────────┘ │
│                                                 │
│  "说出来就行"     "一起写代码"     "命令行搞定"  │
│  零代码经验        需要代码能力     高级开发者    │
│  完整应用          现有项目增强     自动化/CI     │
└─────────────────────────────────────────────────┘
```

## 2. Replit Agent

浏览器端 AI 开发平台，从描述到部署全流程自动化。

```
核心特性：
├─ Agent v3/v4：自主多步骤开发，自动调试
├─ 全栈能力：Web 应用、API、数据库、定时任务
├─ 云 IDE：浏览器内完整开发环境
├─ 内置数据库：PostgreSQL / Key-Value Store
├─ 一键部署：自动部署到 Replit 托管
├─ 200+ 分钟：自主编码会话时长
├─ 多语言：Python, JavaScript, TypeScript, Go, Ruby 等
└─ 协作：实时多人协作编辑
```

### 使用流程

```
┌─────────── Replit Agent 工作流 ───────────┐
│                                            │
│  1. 用户描述需求（自然语言）                │
│     "帮我做一个待办事项 App，                │
│      支持分类、截止日期、优先级"             │
│     ↓                                      │
│  2. Agent 分析需求，生成开发计划             │
│     ├─ 技术栈选择（Next.js + PostgreSQL）  │
│     ├─ 数据库 Schema 设计                  │
│     ├─ API 路由规划                        │
│     └─ UI 组件规划                         │
│     ↓                                      │
│  3. Agent 自主编码（多步骤）                │
│     ├─ 创建项目结构                        │
│     ├─ 编写后端 API                        │
│     ├─ 编写前端页面                        │
│     ├─ 连接数据库                          │
│     └─ 自动调试错误                        │
│     ↓                                      │
│  4. 实时预览 + 用户反馈                     │
│     "加一个暗色模式" → Agent 继续修改       │
│     ↓                                      │
│  5. 一键部署上线                            │
│     https://my-todo-app.replit.app          │
└────────────────────────────────────────────┘
```

### Replit Agent 示例对话

```
用户: 帮我做一个个人博客网站，支持 Markdown 写文章，有标签分类和搜索功能

Replit Agent:
  ✅ 分析需求...
  📋 开发计划:
    1. 使用 Next.js 14 + TypeScript
    2. SQLite 数据库存储文章
    3. Markdown 渲染 (react-markdown)
    4. 标签系统 + 全文搜索
    5. 响应式设计 (Tailwind CSS)

  🔨 开始编码...
  ├─ 创建 Next.js 项目
  ├─ 设计数据库 Schema (posts, tags, post_tags)
  ├─ 编写 API: GET/POST/PUT/DELETE /api/posts
  ├─ 编写前端: 文章列表、编辑器、搜索
  ├─ 添加 Markdown 渲染和代码高亮
  ├─ 实现标签过滤
  └─ 修复 2 个 TypeScript 类型错误

  ✅ 完成！点击预览查看效果
  🚀 部署: https://my-blog.replit.app
```

## 3. v0 by Vercel

Vercel 推出的 UI 生成工具，专注 React/Next.js 前端组件生成。

```
核心特性：
├─ UI 专精：从描述/截图生成 React 组件
├─ 技术栈：React + Next.js + shadcn/ui + Tailwind CSS
├─ 实时预览：生成即可预览效果
├─ 代码导出：一键导出到本地项目
├─ 迭代修改：对话式修改 UI
├─ Vercel 部署：无缝部署到 Vercel
└─ 截图转代码：上传设计稿自动生成代码
```

### v0 生成示例

```
用户: 做一个现代风格的定价页面，3 个套餐：免费版、专业版、企业版

v0 生成 →

// components/pricing.tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Check } from "lucide-react"

const plans = [
  {
    name: "免费版",
    price: "¥0",
    period: "/月",
    description: "适合个人项目",
    features: ["1 个项目", "基础分析", "社区支持", "1GB 存储"],
    cta: "免费开始",
    popular: false,
  },
  {
    name: "专业版",
    price: "¥99",
    period: "/月",
    description: "适合成长团队",
    features: ["无限项目", "高级分析", "优先支持", "100GB 存储", "自定义域名", "API 访问"],
    cta: "开始试用",
    popular: true,
  },
  {
    name: "企业版",
    price: "联系我们",
    period: "",
    description: "适合大型组织",
    features: ["一切专业版功能", "SSO 单点登录", "SLA 保障", "专属客户经理", "私有部署", "审计日志"],
    cta: "联系销售",
    popular: false,
  },
]

export function PricingPage() {
  return (
    <section className="py-20 px-4">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold mb-4">选择适合你的方案</h2>
        <p className="text-muted-foreground">所有方案均可免费试用 14 天</p>
      </div>
      <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {plans.map((plan) => (
          <Card key={plan.name} className={plan.popular ? "border-primary shadow-lg scale-105" : ""}>
            <CardHeader>
              {plan.popular && (
                <span className="text-xs bg-primary text-primary-foreground px-3 py-1 rounded-full w-fit">
                  最受欢迎
                </span>
              )}
              <CardTitle>{plan.name}</CardTitle>
              <div className="text-3xl font-bold">{plan.price}<span className="text-sm font-normal">{plan.period}</span></div>
              <p className="text-sm text-muted-foreground">{plan.description}</p>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" /> {f}
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
                {plan.cta}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </section>
  )
}
```

## 4. Bolt.new by StackBlitz

浏览器内全栈应用生成，基于 WebContainer 技术（浏览器中运行 Node.js）。

```
核心特性：
├─ WebContainer：浏览器内运行完整 Node.js 环境
├─ 全栈生成：前端 + 后端 + 数据库
├─ 多框架：React, Vue, Svelte, Next.js, Nuxt, Astro
├─ 实时预览：代码修改即时反映
├─ 一键部署：Netlify 一键部署
├─ 无需安装：纯浏览器，无需本地环境
└─ 开源版本：bolt.diy 社区开源版
```

```
┌─────────── Bolt.new 架构 ───────────┐
│                                      │
│  浏览器                              │
│  ┌──────────────────────────────┐   │
│  │  Bolt.new UI                  │   │
│  │  ┌────────┐  ┌────────────┐  │   │
│  │  │ AI Chat │  │ 代码编辑器  │  │   │
│  │  │ (提示)  │  │ (Monaco)   │  │   │
│  │  └────────┘  └────────────┘  │   │
│  │  ┌────────────────────────┐  │   │
│  │  │  WebContainer          │  │   │
│  │  │  (浏览器内 Node.js)    │  │   │
│  │  │  ├─ npm install        │  │   │
│  │  │  ├─ dev server         │  │   │
│  │  │  └─ 实时预览           │  │   │
│  │  └────────────────────────┘  │   │
│  └──────────────────────────────┘   │
│                                      │
│  一切在浏览器中运行，无需后端服务器    │
└──────────────────────────────────────┘
```

## 5. Lovable（原 GPT Engineer）

全栈应用构建器，GitHub 集成 + Supabase 后端。

```
核心特性：
├─ 全栈生成：React 前端 + Supabase 后端
├─ GitHub 同步：代码自动同步到 GitHub 仓库
├─ Supabase 集成：数据库、认证、存储一键配置
├─ Agent Mode：自主调试，发现并修复错误
├─ 可视化编辑：拖拽 + 代码双模式
├─ 版本历史：每次修改可回滚
└─ 自定义域名：支持绑定自有域名
```

### Lovable 开发流程

```
用户: 做一个 SaaS 项目管理工具，支持看板视图、
      团队成员管理、任务分配和截止日期提醒

Lovable:
  📋 需求分析:
    ├─ 看板视图 (Kanban Board)
    ├─ 用户认证 (Supabase Auth)
    ├─ 团队管理 (邀请/角色)
    ├─ 任务 CRUD + 拖拽排序
    └─ 截止日期提醒 (Email)

  🔨 生成中...
    ├─ React + TypeScript + Tailwind
    ├─ Supabase: users, teams, projects, tasks 表
    ├─ 认证: 邮箱登录 + Google OAuth
    ├─ 看板: react-beautiful-dnd 拖拽
    └─ 部署: Lovable 托管

  ✅ 完成！
    预览: https://my-pm-tool.lovable.app
    GitHub: github.com/user/my-pm-tool (已同步)
    Supabase: 数据库已配置
```

## 6. 综合对比表

| 特性 | Replit | v0 (Vercel) | Bolt.new | Lovable | Cursor | Kiro |
|------|--------|-------------|----------|---------|--------|------|
| 定位 | 全栈 App 构建 | UI 组件生成 | 全栈 App 构建 | 全栈 App 构建 | IDE Agent | IDE Agent |
| 目标用户 | 非开发者/初学者 | 前端开发者 | 非开发者/原型 | 非开发者/创业者 | 专业开发者 | 专业开发者 |
| 技术栈 | 多语言多框架 | React/Next.js | React/Vue/Svelte | React+Supabase | 任意 | 任意 |
| 数据库 | ✅ PostgreSQL | ❌ 仅前端 | ❌ 需外接 | ✅ Supabase | 用户自选 | 用户自选 |
| 部署 | ✅ 内置 | ✅ Vercel | ✅ Netlify | ✅ 内置 | 用户自行 | 用户自行 |
| GitHub 同步 | ✅ | ✅ 导出 | ❌ | ✅ 自动同步 | ✅ 原生 | ✅ 原生 |
| 现有项目 | ❌ 新项目为主 | ❌ 组件级 | ❌ 新项目为主 | ❌ 新项目为主 | ✅ 核心能力 | ✅ 核心能力 |
| 自主调试 | ✅ Agent v4 | ❌ | 有限 | ✅ Agent Mode | ✅ | ✅ |
| 免费额度 | 有限 | 有限 | 有限 | 有限 | 有限 | ✅ 免费 |
| 月费 | $25+ | $20+ | $20+ | $20+ | $20 | 免费(Preview) |
| 最佳场景 | MVP/原型/学习 | UI 组件 | 快速原型 | SaaS MVP | 日常开发 | 规范化开发 |

## 7. 选型决策指南

```
你是谁？你要做什么？
│
├─ 非开发者，想做一个完整应用
│   ├─ 需要数据库和后端     → Replit 或 Lovable
│   ├─ 只需要前端页面       → v0 或 Bolt.new
│   └─ 想学编程             → Replit（最佳学习环境）
│
├─ 开发者，快速原型验证
│   ├─ UI 原型              → v0（最快出 UI）
│   ├─ 全栈 MVP             → Bolt.new 或 Lovable
│   └─ 需要后续维护         → Lovable（GitHub 同步）
│
├─ 专业开发者，日常工作
│   ├─ 现有项目增强         → Cursor / Kiro（IDE Agent）
│   ├─ 需要规范化流程       → Kiro（Specs 驱动）
│   └─ 终端自动化           → Claude Code
│
├─ 团队/企业
│   ├─ 内部工具快速搭建     → Replit Teams
│   ├─ 设计稿转代码         → v0
│   └─ 生产级项目           → Cursor / Kiro + CI/CD
│
└─ 黑客松/比赛
    └─ Bolt.new 或 Replit（最快出成品）
```

## 8. Vibe Coding 的局限性

```
Vibe Coding 适合：                    Vibe Coding 不适合：
├─ ✅ MVP / 原型验证                  ├─ ❌ 大型复杂系统
├─ ✅ 内部工具                        ├─ ❌ 高性能要求
├─ ✅ 学习和实验                      ├─ ❌ 安全敏感应用
├─ ✅ 黑客松/比赛                     ├─ ❌ 需要深度定制
├─ ✅ 个人项目                        ├─ ❌ 遗留系统维护
└─ ✅ 非技术人员的自动化              └─ ❌ 团队协作开发

关键问题：
├─ 代码质量：生成的代码可能不符合最佳实践
├─ 可维护性：非开发者难以后续维护
├─ 安全性：可能存在安全漏洞
├─ 扩展性：简单架构难以应对增长
└─ 调试：出错时非开发者难以定位问题

建议：
├─ 原型阶段用 Vibe Coding 快速验证
├─ 验证成功后用 IDE Agent 重构为生产级代码
└─ 或者直接用 Kiro Specs 从需求开始规范化开发
```

## 9. 从 Vibe Coding 到 Spec 驱动开发：ACAI 方法论

> 🔄 更新于 2026-05-04

2026 年 5 月，开发者社区出现了对 Vibe Coding 的深度反思。两篇文章同日在 HN 爆火：

- **Specsmaxxing**（HN 262 分）：提出 ACAI（Acceptance Criteria for AI）方法论
- **Agentic Coding Is a Trap**（HN 234 分）：分析 Agentic Coding 的陷阱

### ACAI 方法论核心

作者认为我们已经过了"Peak Slop"（AI 生成垃圾代码的高峰），正在进入"后 Slop 时代"。上下文窗口是真正的瓶颈，而非模型能力。

ACAI 的核心做法：用结构化 YAML 编写验收标准，Agent 在代码中直接引用需求编号：

```yaml
# requirements.yaml
AUTH-1: 接受 Authorization: Bearer <token> 头
AUTH-2: Token 是用户级别的，提供对用户所有资源的访问
AUTH-3: 无效 Token 返回 401 Unauthorized
```

```python
# 代码中引用需求编号
# AUTH-1
auth_header = req.headers["authorization"]
# AUTH-2
is_authorized = verify_bearer_token(auth_header)
# AUTH-3
if not is_authorized:
    raise HTTPException(status_code=401)
```

### Agentic Coding 的陷阱

"Agentic 疲劳"现象：AI 工具消除了代码生产的摩擦，但人类吸收、验证和维护代码的判断力跟不上生产速度。速度 ≠ 生产力，AI 生成的代码在 6 个月后可能变成维护噩梦。

### 解决路径

```
Vibe Coding（快速原型）
  ↓ 验证成功
Spec 驱动开发（ACAI / Kiro Specs）
  ↓ 结构化需求 + 验收标准
Harness Engineering（约束 + 反馈循环）
  ↓ CI 强制执行
生产级代码
```

- **来源**：[Specsmaxxing](https://acai.sh/blog/specsmaxxing) / [Agentic Coding Is a Trap](https://larsfaye.com/articles/agentic-coding-is-a-trap)

## 10. 趋势展望

```
2024：Vibe Coding 概念提出，早期工具涌现
2025：工具成熟，Replit/Bolt/Lovable 用户量爆发
2026：
  ├─ "Peak Slop" 已过，行业从狂热走向理性反思
  ├─ Spec 驱动开发成为共识（ACAI / Kiro Specs / Open Agent Spec）
  ├─ Vibe Coding 与 IDE Agent 融合
  │   （非开发者入门 → 逐步过渡到专业工具）
  ├─ AI 生成代码质量持续提升
  ├─ 更多垂直领域工具（AI 做电商/AI 做 SaaS）
  └─ "人人都是开发者" 时代加速到来
```

## 10. 相关文档

- IDE Agent → `Cursor-Kiro-Windsurf IDE Agent.md`（本目录）
- 终端 Agent → `Claude Code与终端Agent.md`（本目录）
- 自主开发 → `Devin与自主开发Agent.md`（本目录）
- Harness Engineering → `16-Harness Engineering/Harness Engineering完整指南.md`
- Agent 设计模式 → `01-Agentic设计模式/Agentic设计模式大全.md`
## 🎬 推荐视频资源

### 🌐 YouTube
- [Fireship - Vibe Coding Explained](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Vibe Coding概念讲解
- [freeCodeCamp - Build Apps with AI](https://www.youtube.com/watch?v=dcgRMOG605w) — AI应用构建教程

### 📺 B站
- [Vibe Coding实战](https://www.bilibili.com/video/BV1Bm421N7BH) — AI辅助编程中文教程

### 🌐 平台
- [Replit](https://replit.com/) — AI驱动的在线IDE
- [v0.dev](https://v0.dev/) — Vercel AI UI生成器
- [bolt.new](https://bolt.new/) — StackBlitz AI应用构建
