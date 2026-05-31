# 本地 Coding Agent：隐私优先的去中心化方案

> Author: Walter Wang

> 🔄 创建于 2026-04-21

## 1. 背景与动机

在 OpenAI Codex 和 Claude Code 争夺云端 Coding Agent 市场的同时，开源社区正在走一条不同的路线：**完全本地运行的 Coding Agent**。核心理念是代码不应该离开开发者的机器。

```
云端 Coding Agent vs 本地 Coding Agent：

┌─────────────────────────────────────────────────────┐
│  云端路线                    本地路线                 │
│  ┌──────────┐              ┌──────────┐             │
│  │ 开发者   │              │ 开发者   │             │
│  └────┬─────┘              └────┬─────┘             │
│       │ 代码上传                 │ 代码留在本地       │
│       ↓                         ↓                    │
│  ┌──────────┐              ┌──────────┐             │
│  │ 云端 API │              │ 本地模型  │             │
│  │ GPT/Claude│              │ GGUF/MLX │             │
│  └──────────┘              └──────────┘             │
│                                                      │
│  优势：模型能力强           优势：隐私、零成本、离线  │
│  劣势：隐私、成本、依赖网络  劣势：模型能力受限       │
└─────────────────────────────────────────────────────┘
```

**适用场景**：
- 企业有严格的数据隐私/合规要求（金融、医疗、政府）
- 个人开发者希望零 API 成本
- 离线开发环境（飞机、受限网络）
- 处理敏感代码库（未公开的商业代码）

## 2. 代表项目

### OpenCode

<!-- version-check: OpenCode, checked 2026-04-21 -->

完全本地运行的开源 AI Coding Agent，支持 GGUF 格式的大模型。

```
OpenCode 架构：

┌──────────────────────────────────────┐
│  OpenCode CLI                        │
│  ├─ 代码编辑（多文件）               │
│  ├─ 调试与错误修复                   │
│  ├─ Shell 命令执行                   │
│  └─ Git 集成                         │
│                                      │
│  模型后端（可切换）                   │
│  ├─ 本地 GGUF：Qwen3-Coder 等       │
│  ├─ 本地 Ollama                      │
│  └─ 可选：云端 API（GPT/Claude）     │
└──────────────────────────────────────┘
```

- **语言**：Go（已归档版本）
- **特点**：终端原生 AI coding agent，支持多语言，可切换本地/云端模型后端
- **模型**：Qwen3-Coder、DeepSeek-Coder 等
- **来源**：[官网](https://opencode.ai/) / [GitHub（活跃版 anomalyco/opencode）](https://github.com/anomalyco/opencode)

> 🔄 更新于 2026-06-02：经核对，名为 "OpenCode" 的项目有两个，**本节已更正指向活跃的主流版本**：
> - `opencode-ai/opencode`（Go，约 1.3 万 stars）—— **已于 2025-09 归档停止维护**，是早期终端 agent。原文引用的「主打本地 GGUF」定位与该项目实际描述（"terminal AI coding agent"）并不吻合，疑似引用的二手分析文章解读有误。
> - `anomalyco/opencode`（原 `sst/opencode`，TypeScript，约 16.7 万 stars，官网 opencode.ai）—— **活跃维护中**（2026-05 仍在更新），是业界主流的开源 coding agent，支持本地与云端模型。
>
> ⚠️ 待确认：若作者本意确实是介绍那个「纯本地 GGUF」的小众项目，请改回 `opencode-ai/opencode` 并注明其已归档；否则保留指向活跃主流版本。

### Junco

<!-- version-check: Junco, checked 2026-04-21 -->

基于 Apple Intelligence 的完全本地 Swift Coding Agent。

- **语言**：Swift
- **平台**：macOS（利用 Apple Silicon 的 Neural Engine）
- **特点**：MIT 协议，专为 Swift 开发优化，利用 Apple Intelligence 框架
- **来源**：[Blog](https://barrasso.me/posts/2026-04-09-on-device-coding-with-apple-intelligence/)

### Codex CLI（混合模式）

OpenAI 的终端原生 Coding Agent，虽然主要依赖云端 API，但支持 MCP 服务器和本地工具调用。

- **Stars**：87k+（2026-06 核对，`openai/codex`）<!-- 修复于 2026-06-02: 75.6k → 87k+，GitHub API 实测 -->
- **特点**：支持 MCP 服务器、并行工具调用、ChatGPT 计划集成
- **来源**：[GitHub](https://github.com/openai/codex)

## 3. 本地模型选择

| 模型 | 参数量 | 量化 | 内存需求 | 编码能力 |
|------|--------|------|---------|---------|
| Qwen3-Coder-32B | 32B | Q4_K_M | ~20GB | ★★★★ |
| DeepSeek-Coder-V2-16B | 16B | Q4_K_M | ~10GB | ★★★ |
| CodeLlama-34B | 34B | Q4_K_M | ~22GB | ★★★ |
| Qwen2.5-Coder-7B | 7B | Q4_K_M | ~5GB | ★★ |

> ⚠️ 待确认：上述模型的具体编码基准测试成绩需要进一步验证

## 4. 局限性

```
本地 Coding Agent 的当前局限：
├─ 模型能力差距：本地模型 vs 云端前沿模型仍有明显差距
├─ 硬件要求：32B+ 模型需要 32GB+ 内存和高端 GPU/Apple Silicon
├─ 上下文窗口：本地模型的上下文窗口通常较小（8K-32K）
├─ 多模态限制：本地模型的视觉/多模态能力有限
└─ 更新频率：开源模型的迭代速度慢于商业模型
```

## 5. 混合策略建议

对于大多数开发者，推荐**混合策略**：

```
日常编码（低敏感度）→ 云端 Agent（Claude Code / Codex）
  - 利用最强模型能力
  - 复杂重构、架构设计

敏感代码（高隐私要求）→ 本地 Agent（OpenCode / Junco）
  - 代码不离开本地
  - 零 API 成本

CI/CD 集成 → 按需选择
  - 公开仓库 → 云端 Agent
  - 私有仓库 → 本地 Agent 或自托管模型
```

## 6. DeepClaude：云端 Agent 的"换脑不换壳"降本方案

> 🔄 更新于 2026-05-04

<!-- version-check: DeepClaude, checked 2026-05-04 -->

DeepClaude 代表了一种新的降本思路：保留 Claude Code 的完整工具链（文件编辑、bash 执行、子 Agent 生成、Git 操作），但将 API 调用重定向到更便宜的模型后端。

```
┌─────────── DeepClaude 架构 ───────────┐
│                                        │
│  你的终端                               │
│  └── Claude Code CLI（工具循环不变）    │
│       └── API 调用 → DeepSeek V4 Pro   │
│           （$0.87/M vs Anthropic $15/M）│
│                                        │
│  支持后端：                             │
│  ├─ DeepSeek（默认，$0.44/$0.87/M）    │
│  ├─ OpenRouter（最便宜，$0.44/$0.87/M）│
│  ├─ Fireworks AI（最快，$1.74/$3.48/M）│
│  └─ Anthropic（原版，$3/$15/M）        │
│                                        │
│  降本效果：                             │
│  ├─ 轻度使用：90% 节省（$200→$20/月）  │
│  ├─ 重度使用：75% 节省（$200→$50/月）  │
│  └─ DeepSeek 上下文缓存：$0.004/M      │
└────────────────────────────────────────┘
```

与纯本地方案的区别：DeepClaude 仍然使用云端 API，代码会发送到 DeepSeek 服务器。如果有严格隐私要求，仍需使用 OpenCode/Junco 等纯本地方案。

- **来源**：[GitHub](https://github.com/aattaran/deepclaude)

## 🔗 相关文档

- [Claude Code 与终端 Agent](./01-Claude%20Code与终端Agent.md)
- [Cursor-Kiro-Windsurf IDE Agent](./03-Cursor-Kiro-Windsurf%20IDE%20Agent.md)
- [Devin 与自主开发 Agent](./04-Devin与自主开发Agent.md)
