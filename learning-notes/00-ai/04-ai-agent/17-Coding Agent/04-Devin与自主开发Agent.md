# Devin 与自主开发 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Devin 概述

Devin 是 Cognition 公司推出的"首个 AI 软件工程师"，能自主完成从需求理解到代码部署的完整开发流程。代表了从"辅助编程"到"自主开发"的范式转变。

```
┌──────────────────── Devin ────────────────────┐
│                                                │
│  输入：自然语言需求 / GitHub Issue / Slack 消息  │
│                                                │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐  │
│  │ 规划  │→│ 编码  │→│ 调试  │→│ 部署/PR   │  │
│  │ Plan  │  │ Code │  │Debug │  │ Deploy   │  │
│  └──────┘  └──────┘  └──────┘  └──────────┘  │
│       ↕         ↕         ↕          ↕         │
│  ┌────────────────────────────────────────┐   │
│  │  Shell / 浏览器 / 编辑器 / Git 环境     │   │
│  └────────────────────────────────────────┘   │
└───────────────────────────────────────────────┘
```

### 核心能力

```
自主开发流程：
├─ 需求理解：解析 Issue/需求文档
├─ 技术规划：选择技术方案，分解任务
├─ 代码编写：多文件编辑，遵循项目规范
├─ 自主调试：运行代码，分析错误，修复 Bug
├─ 测试验证：编写并运行测试
├─ 部署交付：创建 PR，部署到环境
└─ 学习适应：从反馈中改进
```

## 2. Manus AI

通用自主 Agent，不限于编程，能操作浏览器、执行代码、管理文件，完成复杂的多步骤任务。

```python
# Manus 的工作模式（概念示意）
# 用户只需描述目标，Manus 自主规划和执行

"""
用户: 帮我调研 2025 年 AI Agent 框架市场，
      生成一份对比报告，发送到我的邮箱。

Manus 执行流程:
1. 打开浏览器，搜索 AI Agent 框架
2. 访问多个网站，收集信息
3. 整理数据，生成对比表格
4. 用 Python 生成可视化图表
5. 撰写 Markdown 报告
6. 转换为 PDF
7. 通过邮件 API 发送
"""
```

## 3. OpenHands（原 OpenDevin）

开源的自主开发 Agent，复刻 Devin 的核心能力。提供沙箱环境，支持多种 LLM 后端。

```bash
# 安装和运行 OpenHands
pip install openhands

# Docker 方式运行（推荐）
docker run -it \
  -e LLM_API_KEY="sk-xxx" \
  -e LLM_MODEL="claude-sonnet-4-6-20260217" \
  -p 3000:3000 \
  ghcr.io/openhands/openhands:latest

# 访问 http://localhost:3000 使用 Web UI
```

```python
# OpenHands 编程接口
from openhands import Agent

agent = Agent(
    model="claude-sonnet-4-6-20260217",
    workspace="/workspace/my-project",
)

# 自主完成任务
result = agent.run(
    task="在 FastAPI 项目中添加用户认证模块，"
         "使用 JWT Token，包含注册、登录、刷新 Token 接口，"
         "并编写完整的测试。"
)

print(result.summary)
# → 创建了 5 个文件，修改了 2 个文件，所有测试通过
```

## 4. SWE-Agent

普林斯顿大学开发的软件工程 Agent，专注于 GitHub Issue 自动修复。

```bash
# 安装 SWE-Agent
# 修复于 2026-06-02: pip 包名是 sweagent（无连字符），swe-agent 在 PyPI 返回 404
pip install sweagent

# 修复 GitHub Issue
sweagent run \
  --model claude-sonnet-4-6-20260217 \
  --issue "https://github.com/user/repo/issues/42" \
  --repo "https://github.com/user/repo"

# SWE-Agent 会：
# 1. 克隆仓库，理解代码结构
# 2. 分析 Issue 描述
# 3. 定位相关代码
# 4. 编写修复代码
# 5. 运行测试验证
# 6. 生成 patch
```

## 5. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Devin 2.2, SWE-1.6, OpenHands 1.7.0（框架）/ openhands CLI 1.16.0, checked 2026-06-02 -->

### Devin 2.2（2026-02-24）

```
Devin 2.2 核心更新：
├─ Desktop Computer Use：操作 GUI 桌面应用
│  ├─ 浏览器、Figma、Photoshop 等原生应用
│  ├─ 从终端工作流扩展到视觉设计和测试
│  └─ 跨应用自动化
├─ Devin Review：自审查 PR
│  ├─ 每个 PR 自动运行质量检查
│  ├─ 识别逻辑错误、遗漏边界、风格违规
│  └─ 比人工审查多发现 30% 问题
├─ 3x 启动加速：~45s → ~15s
├─ Linear 集成：项目管理工作流
├─ 定时任务：Devin 可自行调度循环会话
│  └─ 跨会话保持状态，每次从上次中断处继续
└─ $10 免费月度额度
```

### SWE-1.6 模型（2026-03-20）

Cognition 发布 SWE-1.6，专为智能和模型 UX 优化。

### Cognition 收购 Windsurf（2025-07）

<!-- 修复于 2026-05-21: 收购时间从 2025-12 修正为 2025-07 -->
2025 年 7 月，在 Google 以 $24 亿"反向收购"挖走 Windsurf 创始人后，Cognition 收购了 Windsurf 剩余资产。Cognition 随后以 $10.2B 估值融资 $400M+（Founders Fund 领投）。截至 2026-05 两个产品仍独立运营。

### OpenHands v1.7.0（框架，2026-05）

<!-- 修复于 2026-05-21: v1.6.0 → v1.14.x（PyPI 确认），Stars 70K+ → 65K（GitHub 确认） -->
<!-- 修复于 2026-06-02: Stars 65K → 75K+（GitHub API 实测 OpenHands/OpenHands 75.4K） -->
<!-- version-check: 已核实并统一口径（2026-06-02）— OpenHands 有双版本号体系：核心框架 = GitHub release tag 1.7.0 = PyPI 包 openhands-ai 1.7.0（summary "Code Less, Make More"，homepage OpenHands/OpenHands）；终端 CLI = PyPI 包 openhands 1.16.0（"Terminal User Interface"）。旧文写的 v1.14.x 来源不明，已更正为框架版 1.7.0。 -->
开源自主编码 Agent 持续增长：75K+ GitHub Stars、490+ 贡献者、MIT 许可。

```
OpenHands 生态数据：
├─ 75K+ GitHub Stars
├─ 490+ 贡献者，3500+ commits
├─ 100+ 版本发布（核心框架 v1.7.0；终端 CLI 包 openhands 独立编号至 1.16.0）
├─ 支持任意 LLM 后端（Claude/GPT/Gemini/本地模型）
├─ OpenHands LM 32B：基于 Qwen Coder 2.5 的开源编码模型
└─ OpenHands Index：跨模型编码能力基准评测
```

### Codex CLI v0.116.0（2026-03-19）

OpenAI 终端编码 Agent：87K+ Stars、12K+ Forks、400 贡献者。新增 ChatGPT 设备码登录、用户 Prompt Hook、插件简化配置。<!-- 修复于 2026-06-02: 67K → 87K+ Stars、9K → 12K+ Forks，GitHub API 实测 openai/codex -->

<!-- version-check: 已核实 — openai/codex 实际 tag 为 rust-v0.116.0，发布日期 2026-03-19，与正文一致（GitHub Releases API 2026-06-02 实测）。注意官方 tag 前缀是 rust-v，正文简写为 v0.116.0。截至 2026-05 已迭代到 rust-v0.135.0。 -->

### 自主 Agent 市场格局（2026-04）

```
PR 合并率数据（截至 2026-03）：
├─ Devin：PR 合并率从 34% 提升至 67%（同比翻倍）
├─ 已合并数十万 PR，覆盖数千家公司
├─ Cognition Japan：首个亚洲扩展，服务日本企业
└─ COBOL 现代化：Fortune 500 企业的遗留系统迁移
```

来源：[Cognition Blog: Devin 2.2](https://cognition.ai/blog/introducing-devin-2-2)（Content was rephrased for compliance with licensing restrictions）
来源：[Cognition Blog: SWE-1.6](https://cognition.ai/blog/1)（Content was rephrased for compliance with licensing restrictions）
来源：[OpenHands Review](https://vibecoding.app/blog/openhands-review)（Content was rephrased for compliance with licensing restrictions）

## 6. 自主 Agent 基准测试（SWE-bench）

```
SWE-bench：标准化软件工程 Agent 评测基准
├─ SWE-bench Lite：300 个精选 Issue
├─ SWE-bench Full：2294 个真实 GitHub Issue
└─ SWE-bench Verified：人工验证的高质量子集

2025 年主要成绩（SWE-bench Verified）：
┌──────────────────┬────────────┐
│ Agent            │ 解决率      │
├──────────────────┼────────────┤
│ Devin            │ ~50%       │
│ OpenHands        │ ~45%       │
│ SWE-Agent        │ ~35%       │
│ Claude Code      │ ~55%       │
│ Cursor Agent     │ ~40%       │
└──────────────────┴────────────┘

注：成绩持续更新，仅供参考趋势
```

## 7. 自主 vs 辅助：何时使用

| 维度 | 自主 Agent（Devin 类） | 辅助 Agent（Cursor 类） |
|------|----------------------|----------------------|
| 交互模式 | 给任务，等结果 | 实时协作，人主导 |
| 适合任务 | 明确的 Issue 修复 | 探索性开发、设计 |
| 代码质量 | 需要审查 | 实时可控 |
| 上下文理解 | 自主探索 | 人提供上下文 |
| 复杂重构 | 有限 | 人引导更好 |
| 成本 | 高（多轮推理） | 中（交互式） |
| 适用团队 | 有 Code Review 流程 | 所有团队 |

## 8. 局限性

```
当前自主开发 Agent 的局限：
├─ 复杂架构决策：缺乏全局设计能力
├─ 跨系统集成：难以理解分布式系统交互
├─ 性能优化：缺乏性能直觉和基准测试经验
├─ 安全审计：可能引入安全漏洞
├─ 需求歧义：对模糊需求的理解不如人类
├─ 成本控制：复杂任务可能消耗大量 Token
└─ 幻觉风险：可能生成看似正确但有隐患的代码
```

## 9. 未来展望

> 🔄 更新于 2026-04-21

```
短期（2025-2026）：
├─ 自主 Agent 在简单 Issue 修复上达到人类水平
├─ IDE Agent 成为开发者标配
├─ Code Review Agent 普及
└─ 厂商战略聚焦 Agent：OpenAI 关停 Sora（4/26），
   清理"副业"集中资源到 Codex Agent 和企业产品

中期（2026-2028）：
├─ 自主 Agent 能处理中等复杂度的功能开发
├─ 多 Agent 协作开发成为现实
├─ AI 参与架构设计和技术选型
└─ 本地 Coding Agent 崛起（OpenCode、Junco 等隐私优先方案）

长期趋势：
├─ 人类角色转向需求定义、架构决策、质量把关
├─ AI 负责大部分编码实现工作
└─ 软件开发效率提升 5-10 倍
```

### OpenAI 战略转型信号（2026-04）

OpenAI 于 4 月 17 日经历三位高管同日离职（前 CPO Kevin Weil、Sora 负责人 Bill Peebles、企业 CTO Srinivas Narayanan），同时 Sora 视频平台将于 4/26 关闭 App、9/24 关闭 API。官方定性为"清理副业"（shedding side quests），将资源集中到 Agent 平台和企业产品。Sora 日均计算成本数百万美元但总收入仅约 210 万美元，经济模型不可持续。

这意味着 OpenAI 的 Agents SDK、Codex Desktop、ChatGPT Agent 将获得更多资源投入，自主开发 Agent 赛道的竞争将进一步加剧。

来源：[TechCrunch](https://techcrunch.com/2026/04/17/kevin-weil-and-bill-peebles-exit-openai-as-company-continues-to-shed-side-quests/) / [The Next Web](https://thenextweb.com/news/openai-departures-kevin-weil-sora-peebles-enterprise-pivot)

### OpenAI Symphony 编排框架（2026-04-28）

> 🔄 更新于 2026-05-03

<!-- version-check: OpenAI Symphony, GPT-5.5, Codex orchestration, Codex app May 2026 upgrades, checked 2026-05-20 -->

OpenAI 开源了 **Symphony**，一个将项目管理看板（当前支持 Linear）转化为 Coding Agent 控制平面的编排规范。每个 Issue 自动分配一个 Agent，Agent 在隔离工作区中持续运行，直到提交 PR。来源：[OpenAI Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)

**核心架构：**
- 基于 Elixir/OTP 构建，天然支持并发和容错
- 每个 Issue → 独立 Agent 工作区 → 自主执行 → PR
- 支持多模型运行时（不限于 Codex）
- 内部使用后 landed PRs 增加 500%

```
Symphony 工作流：
Linear Issue Board
  ├─ Issue #1 → Agent A（隔离沙箱）→ PR #1
  ├─ Issue #2 → Agent B（隔离沙箱）→ PR #2
  ├─ Issue #3 → Agent C（隔离沙箱）→ PR #3
  └─ ...（并行执行，人工审查 PR）
```

**与 GPT-5.5 的关系**：GPT-5.5（2026-04-23）定位为 Agent 运行时而非传统聊天模型，Symphony 是其在软件工程领域的编排层。两者共同标志着 OpenAI 从"模型提供商"向"Agent 平台"的战略转型。

来源：[OpenAI Symphony GitHub](https://github.com/openai/symphony)、[TechCrunch GPT-5.5](https://techcrunch.com/2026/04/23/openai-chatgpt-gpt-5-5-ai-model-superapp/)（Content was rephrased for compliance with licensing restrictions）

### OpenAI Codex App 重大升级（2026-05 月）

> 🔄 更新于 2026-05-20

OpenAI 在 5 月密集发布了 Codex 平台级升级，从 CLI 工具演进为全平台 Agent 开发环境：

**Codex "for (almost) everything"（2026-05-14）：**
- PR 审查：直接在 Codex 中审查 Pull Request
- 多文件 & 终端视图：同时查看多个文件和终端输出
- SSH 远程开发：连接到远程 devbox
- 内置浏览器：前端设计/应用/游戏的快速迭代
- 记忆预览：跨会话的个性化上下文记忆

**Codex 移动端（2026-05-14）：**
- iOS 和 Android ChatGPT 应用内可用
- 所有 ChatGPT 计划（含免费版）均可使用
- 支持在手机上启动和监控 Agent 任务

**Codex Security（研究预览）：**
- 深度项目上下文分析，识别复杂漏洞
- 高置信度发现 + 自动修复建议
- 区别于传统 SAST 工具的 Agent 式安全扫描

**安全架构（"Running Codex Safely"）：**
- 隔离沙箱执行环境
- 细粒度权限控制
- Agent 行为审计追踪

来源：[Codex for (almost) everything](https://openai.com/index/codex-for-almost-everything/)、[Codex Mobile](https://www.buildfastwithai.com/blogs/openai-codex-mobile-chatgpt-app-2026)、[Codex Security](https://openai.com/index/codex-security-now-in-research-preview/)、[Running Codex Safely](https://openai.com/index/running-codex-safely/)（Content was rephrased for compliance with licensing restrictions）
## 🎬 推荐视频资源

### 🌐 YouTube
- [Cognition AI - Devin Demo](https://www.youtube.com/watch?v=fjHtjT7GO1c) — Devin官方演示
- [Fireship - Devin AI Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Devin评测
- [OpenHands - Open Source Devin](https://www.youtube.com/watch?v=dcgRMOG605w) — OpenHands开源替代

### 📖 官方文档
- [OpenHands GitHub](https://github.com/OpenHands/OpenHands) — OpenHands开源项目
