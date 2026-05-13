# Portkey 与 AI 网关对比
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Portkey 概述

> 🔄 更新于 2026-05-13
>
> **Portkey Agent Gateway**（2026-02）：Portkey 从 AI Gateway 升级为 Agent Gateway，新增 Agent 级别的治理、可观测性和控制能力。支持 1600+ 模型（之前 200+）。同时发布 MCP Gateway（2026-01 GA），支持 MCP 协议的集中式管理。OSS Gateway 1.8.2，Enterprise Gateway 2.6.2。
> 来源：[Portkey Blog - Agent Gateway](https://portkey.ai/blog/agent-gateway/)、[Portkey Changelog](https://portkey.ai/docs/changelog)

<!-- version-check: Portkey OSS Gateway 1.8.2, Enterprise 2.6.2, checked 2026-05-13 -->

Portkey 是面向生产环境的 AI 网关（现已升级为 Agent Gateway），提供自动重试、Fallback、负载均衡、缓存、护栏、可观测性等企业级功能。支持 1600+ 语言、视觉、音频和图像模型。

```
┌─────────────────────────────────────────────┐
│              AI 应用 / Agent                  │
├─────────────────────────────────────────────┤
│              Portkey AI Gateway              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │
│  │重试     │ │Fallback│ │负载均衡 │ │缓存   │ │
│  │Retry   │ │        │ │LB     │ │Cache │ │
│  └────────┘ └────────┘ └────────┘ └──────┘ │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │
│  │护栏     │ │可观测   │ │分析     │ │日志   │ │
│  │Guard   │ │Observe │ │Analytic│ │Logs  │ │
│  └────────┘ └────────┘ └────────┘ └──────┘ │
├──────┬──────┬──────┬──────┬────────────────┤
│OpenAI│Claude│Gemini│Azure │ 200+ Providers  │
└──────┴──────┴──────┴──────┴────────────────┘
```

## 2. 快速开始

```bash
pip install portkey-ai
```

```python
from portkey_ai import Portkey

# 初始化（OpenAI 兼容接口）
portkey = Portkey(
    api_key="pk-xxx",
    virtual_key="openai-key-xxx",  # Portkey 托管的 API Key
)

# 调用方式与 OpenAI SDK 完全一致
response = portkey.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "你好"}],
)
print(response.choices[0].message.content)
```

## 3. 自动重试与 Fallback

```python
from portkey_ai import Portkey, createHeaders

# 方式1：配置级 Fallback
portkey = Portkey(
    api_key="pk-xxx",
    config={
        "strategy": {"mode": "fallback"},
        "targets": [
            {
                "virtual_key": "openai-key",
                "override_params": {"model": "gpt-5.2"},
                "retry": {"attempts": 2, "on_status_codes": [429, 500, 502]},
            },
            {
                "virtual_key": "anthropic-key",
                "override_params": {"model": "claude-sonnet-4-6-20260217"},
                "retry": {"attempts": 2},
            },
            {
                "virtual_key": "gemini-key",
                "override_params": {"model": "gemini-2.5-pro"},
            },
        ],
    },
)

# 自动：GPT-5.2 → 重试2次 → Claude → 重试2次 → Gemini
response = portkey.chat.completions.create(
    messages=[{"role": "user", "content": "你好"}],
)
```

## 4. 负载均衡

```python
portkey = Portkey(
    api_key="pk-xxx",
    config={
        "strategy": {"mode": "loadbalance"},
        "targets": [
            {
                "virtual_key": "openai-key-1",
                "weight": 0.7,  # 70% 流量
                "override_params": {"model": "gpt-5.2"},
            },
            {
                "virtual_key": "openai-key-2",
                "weight": 0.3,  # 30% 流量
                "override_params": {"model": "gpt-5.2"},
            },
        ],
    },
)

# 请求自动按权重分配到不同 API Key
response = portkey.chat.completions.create(
    messages=[{"role": "user", "content": "你好"}],
)
```

## 5. 语义缓存

```python
portkey = Portkey(
    api_key="pk-xxx",
    virtual_key="openai-key",
    config={
        "cache": {
            "mode": "semantic",       # 语义缓存（相似问题命中）
            "max_age": 3600,          # 缓存 1 小时
        },
    },
)

# 第一次调用：实际请求 LLM
r1 = portkey.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "什么是机器学习？"}],
)

# 第二次调用：语义相似，命中缓存（毫秒级响应）
r2 = portkey.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "解释一下机器学习"}],
)
```

## 6. 护栏（Guardrails）

```python
portkey = Portkey(
    api_key="pk-xxx",
    virtual_key="openai-key",
    config={
        "before_request_hooks": [{
            "id": "input-guardrail",
            "checks": [
                {"type": "pii_detection", "action": "block"},      # PII 检测
                {"type": "prompt_injection", "action": "block"},   # 注入检测
                {"type": "toxicity", "threshold": 0.7, "action": "block"},
            ],
        }],
        "after_request_hooks": [{
            "id": "output-guardrail",
            "checks": [
                {"type": "toxicity", "threshold": 0.5, "action": "block"},
                {"type": "relevance", "threshold": 0.3, "action": "flag"},
            ],
        }],
    },
)

# 请求自动经过护栏检查
try:
    response = portkey.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": user_input}],
    )
except Exception as e:
    print(f"护栏拦截: {e}")
```

## 7. 可观测性与分析

```python
from portkey_ai import Portkey

# 添加追踪元数据
portkey = Portkey(
    api_key="pk-xxx",
    virtual_key="openai-key",
)

response = portkey.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "你好"}],
    metadata={
        "trace_id": "req-001",
        "user_id": "alice",
        "environment": "production",
        "feature": "customer-support",
    },
)

# Portkey Dashboard 提供：
# ├─ 请求日志（输入/输出/延迟/成本）
# ├─ 成本分析（按模型/用户/功能）
# ├─ 延迟分布（P50/P95/P99）
# ├─ 错误率追踪
# ├─ Token 用量趋势
# └─ 自定义告警
```

## 8. 与 Agent 框架集成

```python
# LangChain 集成
from langchain_openai import ChatOpenAI
from portkey_ai import createHeaders

llm = ChatOpenAI(
    model="gpt-5.2",
    base_url="https://api.portkey.ai/v1",
    default_headers=createHeaders(
        api_key="pk-xxx",
        virtual_key="openai-key",
    ),
)

# CrewAI 集成
from crewai import Agent
agent = Agent(
    role="研究员",
    llm=llm,  # 使用 Portkey 代理的 LLM
)

# OpenAI SDK 集成
from openai import OpenAI
client = OpenAI(
    base_url="https://api.portkey.ai/v1",
    default_headers=createHeaders(api_key="pk-xxx", virtual_key="openai-key"),
)
```

## 9. AI 网关全面对比

| 特性           | LiteLLM        | Vercel Gateway  | Portkey         | Helicone        |
|---------------|----------------|-----------------|-----------------|-----------------|
| 模型支持       | 100+           | 主流            | 1600+           | 主流            |
| 部署方式       | 自托管          | 云服务          | 云服务/自托管    | 云服务          |
| 负载均衡       | ✅             | ✅              | ✅              | ❌              |
| Fallback      | ✅             | ✅              | ✅ 多级         | ❌              |
| 自动重试       | ✅             | ✅              | ✅ 细粒度       | ❌              |
| 语义缓存       | ✅ Redis       | ❌              | ✅ 内置         | ✅              |
| 护栏           | ❌             | ❌              | ✅ 内置         | ❌              |
| 可观测性       | ✅ 基础        | ✅ 基础         | ✅ 全面         | ✅ 核心功能      |
| 预算管理       | ✅ 细粒度      | ✅ 基础         | ✅              | ✅              |
| 开源           | ✅ Apache 2.0  | ❌              | ❌              | ✅ 部分         |
| 定价           | 免费（自托管）  | 按用量          | 免费层+付费      | 免费层+付费     |
| 适用场景       | 自托管团队      | Vercel 生态     | 企业级生产       | 轻量可观测      |

## 10. 选型指南

```
选型决策树：

需要自托管？ ──→ YES ──→ LiteLLM（开源，完全控制）
     │
     NO
     ↓
用 Vercel/Next.js？ ──→ YES ──→ Vercel AI Gateway（原生集成）
     │
     NO
     ↓
需要护栏+高级可观测？ ──→ YES ──→ Portkey（企业级功能）
     │
     NO
     ↓
只需要日志和分析？ ──→ YES ──→ Helicone（零代码集成）
     │
     NO
     ↓
预算有限？ ──→ LiteLLM 自托管（免费）

组合方案：
├─ 小团队：LiteLLM 自托管 + LangFuse 可观测
├─ 中型团队：Portkey 云服务（网关+可观测一体）
├─ 大型企业：Portkey/LiteLLM + 自建护栏 + Datadog 监控
└─ Vercel 用户：Vercel AI SDK + AI Gateway（最佳体验）
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [Portkey - AI Gateway](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Portkey AI网关介绍

### 📖 官方文档
- [Portkey Docs](https://portkey.ai/docs) — Portkey官方文档
