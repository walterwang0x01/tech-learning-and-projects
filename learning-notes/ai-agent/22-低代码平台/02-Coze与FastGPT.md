# Coze 与 FastGPT
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Coze 平台概述

Coze（扣子）是字节跳动推出的 AI Bot 构建平台，支持零代码创建 Agent，内置丰富的插件市场。

```
┌─────────────────────────────────────────┐
│              Coze 平台                    │
├──────────┬──────────┬──────────────────┤
│ Bot 构建  │ 插件市场  │  工作流          │
├──────────┼──────────┼──────────────────┤
│ 人设配置  │ 搜索插件  │ 可视化编排       │
│ 知识库    │ 代码插件  │ 条件分支         │
│ 长期记忆  │ API 插件  │ 变量传递         │
└──────────┴──────────┴──────────────────┘
```

## 2. Coze Bot 构建

```python
# Coze API 调用
import httpx

COZE_API = "https://api.coze.com/v3"
COZE_TOKEN = "pat_xxx"
BOT_ID = "bot_xxx"

async def chat_with_coze_bot(query: str, user_id: str, conversation_id: str = "") -> dict:
    """调用 Coze Bot"""
    async with httpx.AsyncClient() as client:
        payload = {
            "bot_id": BOT_ID,
            "user_id": user_id,
            "stream": False,
            "additional_messages": [
                {"role": "user", "content": query, "content_type": "text"}
            ],
        }
        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = await client.post(
            f"{COZE_API}/chat",
            headers={
                "Authorization": f"Bearer {COZE_TOKEN}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        return response.json()

# 查询对话结果
async def get_chat_result(conversation_id: str, chat_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{COZE_API}/chat/message/list",
            headers={"Authorization": f"Bearer {COZE_TOKEN}"},
            params={"conversation_id": conversation_id, "chat_id": chat_id},
        )
        return response.json()
```

## 3. Coze 插件开发

```python
# Coze 自定义插件（HTTP API 方式）
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SearchRequest(BaseModel):
    keyword: str
    limit: int = 10

class SearchResponse(BaseModel):
    results: list[dict]

@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    """搜索接口 — 注册为 Coze 插件"""
    results = await perform_search(req.keyword, req.limit)
    return SearchResponse(results=results)

# 在 Coze 平台注册：
# 1. 创建插件 → API 插件
# 2. 填写 API URL: https://your-server.com/search
# 3. 配置请求/响应 Schema
# 4. 在 Bot 中启用该插件
```

## 4. FastGPT 概述

FastGPT 是开源的知识库问答系统，专注于 RAG 场景，支持可视化工作流编排。

```
FastGPT 核心能力：
├── 知识库管理（多种文档格式、自动分块、QA 拆分）
├── 工作流编排（可视化拖拽、条件分支、HTTP 节点）
├── 对话管理（多轮对话、变量提取、内容补全）
└── API 发布（OpenAI 兼容接口、嵌入式 Widget）
```

## 5. FastGPT 知识库问答

```python
# FastGPT 兼容 OpenAI API 格式
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/api/v1",
    api_key="fastgpt-xxx",  # FastGPT API Key
)

# 直接对话（自动检索知识库）
response = client.chat.completions.create(
    model="fastgpt-app-id",  # FastGPT 应用 ID
    messages=[
        {"role": "user", "content": "公司的年假政策是什么？"},
    ],
    stream=False,
)
print(response.choices[0].message.content)

# 流式对话
stream = client.chat.completions.create(
    model="fastgpt-app-id",
    messages=[{"role": "user", "content": "如何申请报销？"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## 6. FastGPT 私有部署

```yaml
# docker-compose.yaml
services:
  fastgpt:
    image: ghcr.io/labring/fastgpt:latest
    ports:
      - "3000:3000"
    environment:
      - DEFAULT_ROOT_PSW=admin123
      - OPENAI_BASE_URL=https://api.openai.com/v1
      - CHAT_API_KEY=sk-xxx
      - DB_MAX_LINK=30
      - TOKEN_KEY=any-random-string
    depends_on:
      - mongo
      - pg

  mongo:
    image: mongo:5.0
    volumes:
      - ./data/mongo:/data/db

  pg:
    image: ankane/pgvector:latest
    environment:
      - POSTGRES_PASSWORD=postgrespassword
    volumes:
      - ./data/pg:/var/lib/postgresql/data
```

## 7. 平台对比

| 特性 | Coze | FastGPT | Dify |
|------|------|---------|------|
| 类型 | SaaS | 开源自托管 | 开源自托管 |
| 知识库 | ✅ | ✅（强） | ✅ |
| 工作流 | ✅ | ✅ | ✅（强） |
| 插件市场 | ✅（丰富） | 有限 | 有限 |
| Agent 模式 | ✅ | ✅ | ✅ |
| 私有部署 | ❌ | ✅ | ✅ |
| 适用场景 | 快速构建Bot | 知识库问答 | 复杂工作流 |
## 8. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Coze 2.5, Coze Studio v0.5.0, checked 2026-05-31 -->

### Coze 2.5："Agent World" 生态

字节跳动于 2026-04-07 发布 Coze 2.5，引入"Agent World"生态系统，让 AI Agent 突破聊天界面限制：

**三大核心能力**：

1. **全装备（Full-Equipped Devices）**：
   - 云端 PC：基于 Ubuntu，2 核 4G 内存，含浏览器、文件系统、终端
   - 云端手机：支持 App 操作和移动端任务
   - 独立邮箱：Agent 拥有专属邮件地址
   - 支持运行代码脚本、浏览网页、处理文件，保持登录状态

2. **全技能（Full-Equipped Skills）**：
   - 视频创作、编程、行业专业技能
   - Agent 可独立学习和协作

3. **全人格（Full-Equipped Personalities）**：
   - 可管理的记忆系统
   - 数字社交 ID
   - 独立身份和长期记忆

### Coze Studio 开源

Coze Studio（扣子开源版）于 2025-07 正式开源，基于 Apache 2.0 许可：

- GitHub 仓库：[coze-dev/coze-studio](https://github.com/coze-dev/coze-studio)
- 当前版本：v0.5.0（2026 年发布；支持 chatflow、工作流、Agent、应用场景）<!-- 修复于 2026-05-31: v0.3.0 已过时，SourceForge/GitHub 镜像确认最新为 v0.5.0 -->
- 提供可视化工具，支持无代码/低代码方式构建 AI Agent
- 配套 [Coze Loop](https://github.com/coze-dev/coze-loop)：Agent 全生命周期管理平台（开发、调试、评估、监控）

### 平台对比更新

| 特性 | Coze（SaaS） | Coze Studio（开源） | FastGPT |
|------|-------------|-------------------|---------|
| 类型 | SaaS 平台 | 开源自托管 | 开源自托管 |
| Agent World | ✅（v2.5） | ❌ | ❌ |
| 云端设备 | ✅（PC + 手机） | ❌ | ❌ |
| 知识库 | ✅ | ✅ | ✅（强） |
| 工作流 | ✅ | ✅（chatflow） | ✅ |
| 许可证 | 商业 | Apache 2.0 | Apache 2.0 |

> 来源：[KuCoin News](https://www.kucoin.com/news/flash/bytedance-s-coze-launches-version-2-5-introduces-agent-world-ecosystem)、[AIBase](https://news.aibase.com/news/27013)、[Coze Studio GitHub](https://github.com/coze-dev/coze-studio)

## 🎬 推荐视频资源

### 🌐 YouTube
- [Coze Official - Build AI Bot](https://www.youtube.com/watch?v=CgMd0zsz_BQ) — Coze官方教程

### 📺 B站
- [Coze扣子平台实战教程](https://www.bilibili.com/video/BV1Bz421B7bG) — Coze中文实战
- [FastGPT部署与使用教程](https://www.bilibili.com/video/BV1PD421E7mN) — FastGPT中文教程

### 📖 官方文档
- [Coze官方文档](https://www.coze.com/docs) — Coze平台文档
- [FastGPT文档](https://doc.fastgpt.in/) — FastGPT官方文档
