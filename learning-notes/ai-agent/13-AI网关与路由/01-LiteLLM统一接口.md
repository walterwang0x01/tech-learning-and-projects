# LiteLLM 统一接口
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

LiteLLM 提供统一的 OpenAI 兼容接口，支持 100+ LLM 提供商（OpenAI、Anthropic、Google、AWS Bedrock、Azure 等）。核心价值：一套代码切换任意模型。

```
┌─────────────────────────────────────────┐
│            应用 / Agent                  │
│         OpenAI 兼容 API 调用             │
├─────────────────────────────────────────┤
│              LiteLLM                     │
│  ┌────────┐ ┌────────┐ ┌────────────┐  │
│  │统一接口 │ │负载均衡 │ │预算管理     │  │
│  │Unified │ │Load    │ │Budget     │  │
│  │API     │ │Balance │ │Tracking   │  │
│  └────────┘ └────────┘ └────────────┘  │
├──────┬──────┬──────┬──────┬────────────┤
│OpenAI│Claude│Gemini│Bedrock│ 100+ 更多  │
└──────┴──────┴──────┴──────┴────────────┘
```

## 2. Python SDK 基础用法

```bash
pip install litellm
```

<!-- version-check: LiteLLM 1.83.x, checked 2026-05-13 -->
<!-- 修复于 2026-05-13: gpt-4o → gpt-5.2（gpt-4o 已从 ChatGPT 退役，推荐使用新模型） -->

```python
import litellm

# 统一接口调用不同模型 — 完全兼容 OpenAI SDK 格式
# OpenAI
response = litellm.completion(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "你好"}],
)

# Anthropic Claude
response = litellm.completion(
    model="claude-sonnet-4-6-20260217",
    messages=[{"role": "user", "content": "你好"}],
)

# Google Gemini
response = litellm.completion(
    model="gemini/gemini-2.5-pro",
    messages=[{"role": "user", "content": "你好"}],
)

# AWS Bedrock
response = litellm.completion(
    model="bedrock/anthropic.claude-sonnet-4-6-20260217-v1:0",
    messages=[{"role": "user", "content": "你好"}],
)

# 所有响应格式统一为 OpenAI 格式
print(response.choices[0].message.content)
print(response.usage.total_tokens)
```

## 3. 流式输出与异步

```python
import litellm

# 流式输出
response = litellm.completion(
    model="claude-sonnet-4-6-20260217",
    messages=[{"role": "user", "content": "写一首诗"}],
    stream=True,
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# 异步调用
import asyncio

async def async_call():
    response = await litellm.acompletion(
        model="gpt-5.2",
        messages=[{"role": "user", "content": "你好"}],
    )
    return response.choices[0].message.content

result = asyncio.run(async_call())
```

## 4. LiteLLM Proxy Server

代理服务器模式，为团队提供统一的 API 端点。

```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-5.2
    litellm_params:
      model: openai/gpt-5.2
      api_key: sk-xxx

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-6-20260217
      api_key: sk-ant-xxx

  - model_name: fast-model  # 负载均衡：多个模型轮询
    litellm_params:
      model: openai/gpt-5-mini
      api_key: sk-xxx
  - model_name: fast-model
    litellm_params:
      model: anthropic/claude-haiku-3-5
      api_key: sk-ant-xxx

general_settings:
  master_key: sk-litellm-master-key  # 管理员密钥

litellm_settings:
  drop_params: true  # 自动丢弃不支持的参数
  set_verbose: false
```

```bash
# 启动代理服务器
litellm --config litellm_config.yaml --port 4000
```

```python
# 客户端使用（标准 OpenAI SDK）
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000",
    api_key="sk-litellm-master-key",
)

# 通过代理调用任意模型
response = client.chat.completions.create(
    model="claude-sonnet",  # 映射到 Claude
    messages=[{"role": "user", "content": "你好"}],
)
```

## 5. 负载均衡与 Fallback

```yaml
# litellm_config.yaml
model_list:
  # 主模型
  - model_name: main-model
    litellm_params:
      model: openai/gpt-5.2
      api_key: sk-xxx
    model_info:
      priority: 1  # 优先级

  # 备用模型（Fallback）
  - model_name: main-model
    litellm_params:
      model: anthropic/claude-sonnet-4-6-20260217
      api_key: sk-ant-xxx
    model_info:
      priority: 2

router_settings:
  routing_strategy: "least-busy"  # 路由策略
  # 可选: simple-shuffle, least-busy, latency-based-routing
  num_retries: 3
  timeout: 30
  fallbacks:
    - main-model: ["claude-sonnet"]  # GPT-5.2 失败时切换到 Claude
```

```python
# 代码级 Fallback
from litellm import Router

router = Router(
    model_list=[
        {"model_name": "primary", "litellm_params": {"model": "gpt-5.2", "api_key": "sk-xxx"}},
        {"model_name": "fallback", "litellm_params": {"model": "claude-sonnet-4-6-20260217", "api_key": "sk-ant-xxx"}},
    ],
    fallbacks=[{"primary": ["fallback"]}],
    num_retries=2,
)

response = router.completion(
    model="primary",
    messages=[{"role": "user", "content": "你好"}],
)
```

## 6. 预算与用量管理

```yaml
# litellm_config.yaml
general_settings:
  master_key: sk-master
  database_url: postgresql://user:pass@host/litellm  # 持久化用量数据

litellm_settings:
  max_budget: 1000.0        # 全局月预算（美元）
  budget_duration: "1mo"
```

```python
# 通过 API 管理用户预算
import requests

# 创建用户并设置预算
requests.post("http://localhost:4000/user/new", json={
    "user_id": "alice",
    "max_budget": 50.0,       # 月预算 $50
    "budget_duration": "1mo",
}, headers={"Authorization": "Bearer sk-master"})

# 创建团队预算
requests.post("http://localhost:4000/team/new", json={
    "team_alias": "ai-team",
    "max_budget": 500.0,
    "members": [{"user_id": "alice"}, {"user_id": "bob"}],
}, headers={"Authorization": "Bearer sk-master"})

# 生成用户专属 API Key
resp = requests.post("http://localhost:4000/key/generate", json={
    "user_id": "alice",
    "team_id": "ai-team",
    "max_budget": 50.0,
    "models": ["gpt-5.2", "claude-sonnet"],  # 限制可用模型
}, headers={"Authorization": "Bearer sk-master"})
user_key = resp.json()["key"]
```

## 7. 与 Agent 框架集成

```python
# LangChain 集成
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="claude-sonnet",
    base_url="http://localhost:4000",
    api_key="sk-user-key",
)

# CrewAI 集成
from crewai import Agent
agent = Agent(
    role="研究员",
    llm="openai/claude-sonnet",  # 通过 LiteLLM 代理
    # 设置环境变量 OPENAI_API_BASE=http://localhost:4000
)

# OpenAI Agents SDK 集成
from openai import OpenAI
client = OpenAI(base_url="http://localhost:4000", api_key="sk-user-key")
```

## 8. 速率限制与缓存

```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-5.2
    litellm_params:
      model: openai/gpt-5.2
      api_key: sk-xxx
      rpm: 100   # 每分钟请求数限制
      tpm: 50000 # 每分钟 Token 数限制

litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: localhost
    port: 6379
    ttl: 3600  # 缓存 1 小时
```

## 9. 监控面板

```
LiteLLM 内置管理界面：http://localhost:4000/ui

功能：
├─ 实时请求日志
├─ 模型用量统计
├─ 成本追踪（按用户/团队/模型）
├─ 错误率监控
├─ API Key 管理
└─ 模型配置管理
```

| 特性         | LiteLLM          | Vercel AI Gateway | Portkey          |
|-------------|------------------|-------------------|------------------|
| 模型支持     | 100+             | 主流模型           | 1600+            |
| 部署方式     | 自托管            | 云服务             | 云服务/自托管     |
| 负载均衡     | ✅               | ✅                | ✅               |
| 预算管理     | ✅ 细粒度         | ✅ 基础           | ✅               |
| 缓存         | ✅ Redis         | ❌                | ✅ 语义缓存       |
| 开源         | ✅ Apache 2.0    | ❌                | ❌               |
| 适用场景     | 团队自托管网关     | Vercel 生态       | 企业级 AI 网关    |
## 🎬 推荐视频资源

### 🌐 YouTube
- [LiteLLM - Unified LLM API](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — LiteLLM统一接口教程

### 📖 官方文档
- [LiteLLM Docs](https://docs.litellm.ai/) — LiteLLM官方文档（支持100+模型）
