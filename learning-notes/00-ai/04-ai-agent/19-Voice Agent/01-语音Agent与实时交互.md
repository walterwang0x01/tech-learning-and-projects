# 语音 Agent 与实时交互
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

语音 Agent 是 AI Agent 的语音交互形态，用户通过自然语音与 Agent 实时对话，Agent 能听、能说、能执行工具调用。2025 年是语音 Agent 爆发元年，OpenAI Realtime API 正式 GA，ElevenLabs、LiveKit、Vapi 等平台快速成熟。

核心技术演进：从传统 STT→LLM→TTS 三段式管道，到原生音频模型（Audio-to-Audio）的端到端处理。

```
┌─────────────── 语音 Agent 技术演进 ───────────────┐
│                                                     │
│  传统管道架构（高延迟 ~2-5s）                        │
│  ┌──────┐    ┌──────┐    ┌──────┐                  │
│  │ STT  │ →  │ LLM  │ →  │ TTS  │                  │
│  │语音→文│    │文本推理│    │文→语音│                  │
│  └──────┘    └──────┘    └──────┘                  │
│     ↓ 文本      ↓ 文本      ↓ 音频                  │
│  延迟累加：STT延迟 + LLM延迟 + TTS延迟              │
│                                                     │
│  ─────────────────────────────────────              │
│                                                     │
│  原生音频模型（低延迟 ~300ms-1s）                    │
│  ┌──────────────────────────────┐                  │
│  │   Native Audio Model         │                  │
│  │   (gpt-realtime-2 / Gemini)  │                  │
│  │   音频输入 → 直接音频输出      │                  │
│  │   保留语气、情感、韵律         │                  │
│  └──────────────────────────────┘                  │
│  单模型端到端，延迟大幅降低                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 2. OpenAI Realtime API（gpt-realtime）

> 🔄 更新于 2026-05-20

2026 年 Realtime API 正式 GA（脱离 Beta），模型从 `gpt-4o-realtime-preview` 升级为独立的 `gpt-realtime` 系列。2026-04 OpenAI 发布 **GPT-Realtime-2**（首个 GPT-5 类推理能力的语音模型）+ **GPT-Realtime-Translate**（70+ 语言实时翻译）+ **GPT-Realtime-Whisper**（流式语音转文本）。来源：[OpenAI - Advancing Voice Intelligence](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)

<!-- version-check: gpt-realtime-2, gpt-realtime-translate, gpt-realtime-whisper, checked 2026-05-20 -->
<!-- 修复于 2026-05-20: 补充 GPT-Realtime-2/Translate/Whisper 三个新模型，标注 GA 后 OpenAI-Beta header 已移除 -->

```
核心特性（2026 GA）：
├─ 原生音频：音频直入直出，保留语气和情感
├─ WebSocket / WebRTC / SIP：三种连接方式
├─ Function Calling：语音模式下调用工具
├─ 远程 MCP Server：直接连接 MCP 工具（GA 新增）
├─ SIP 电话：连接 PSTN 电话网络（GA 新增）
├─ 图像输入：多模态（看图+听声+回答）
├─ 中断处理：用户随时打断，Agent 立即停止
├─ 多种语音：ash, ballad, coral, sage, verse, cedar, marin
├─ 转录模型：约 90% 更少幻觉（对比 Whisper v2）
└─ gpt-realtime-2：GPT-5 类推理，对话更自然，处理更复杂请求
```

**GPT-Realtime-2 关键改进**（2026-04）：
- 首个具备 GPT-5 类推理能力的语音模型
- 更好的上下文处理和多轮对话能力
- 支持更复杂的工具调用场景
- WebSocket URL 改为 `wss://api.openai.com/v1/realtime?model=gpt-realtime-2`

**GA 版本的重要变更**（与旧 Beta 版对比）：
- 移除 `OpenAI-Beta: realtime=v1` header（不再需要）
- 引入 `client_secrets` 端点（用于客户端临时凭证）
- 引入 `session_type` 字段
- `input_audio_transcription` 配置已变更（详见 GA 迁移指南）
- 部分事件名更新

### WebSocket 连接与 Function Calling 示例

> 🔄 更新于 2026-05-20: 模型名 `gpt-4o-realtime-preview` → `gpt-realtime-2`，移除 GA 后不再需要的 `OpenAI-Beta` header

```python
import asyncio
import websockets
import json

async def realtime_voice_agent():
    """OpenAI Realtime API — WebSocket 连接与 Function Calling（GA 版本）"""
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
    headers = {
        "Authorization": "Bearer sk-xxx",
        # 注意：GA 版本不再需要 "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        # 1. 配置会话：语音、工具、指令
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "coral",
                "instructions": "你是一个友好的中文客服助手，帮用户查询订单和解答问题。",
                "tools": [
                    {
                        "type": "function",
                        "name": "query_order",
                        "description": "根据订单号查询订单状态",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "order_id": {"type": "string", "description": "订单编号"}
                            },
                            "required": ["order_id"]
                        }
                    },
                    {
                        "type": "function",
                        "name": "transfer_to_human",
                        "description": "转接人工客服",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "reason": {"type": "string"}
                            }
                        }
                    }
                ],
                "turn_detection": {
                    "type": "server_vad",       # 服务端语音活动检测
                    "threshold": 0.5,
                    "silence_duration_ms": 500,  # 静默 500ms 判定说完
                }
            }
        }))

        # 2. 发送音频数据（从麦克风捕获）
        # audio_data = capture_from_microphone()
        # await ws.send(json.dumps({
        #     "type": "input_audio_buffer.append",
        #     "audio": base64_encode(audio_data),
        # }))

        # 3. 监听响应事件
        async for message in ws:
            event = json.loads(message)

            match event["type"]:
                case "response.audio.delta":
                    # 收到音频流，播放给用户
                    play_audio(event["delta"])

                case "response.function_call_arguments.done":
                    # 收到 Function Call，执行工具
                    name = event["name"]
                    args = json.loads(event["arguments"])

                    if name == "query_order":
                        result = await query_order_db(args["order_id"])
                    elif name == "transfer_to_human":
                        result = await transfer_human(args["reason"])

                    # 返回工具结果
                    await ws.send(json.dumps({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": event["call_id"],
                            "output": json.dumps(result),
                        }
                    }))
                    # 触发 Agent 继续回复
                    await ws.send(json.dumps({
                        "type": "response.create"
                    }))

                case "response.done":
                    print("Agent 回复完成")

                case "error":
                    print(f"错误: {event['error']}")

asyncio.run(realtime_voice_agent())
```

### 定价模型

> 🔄 更新于 2026-05-20: 定价数据为 2025 年 GA 后的标准价，gpt-4o 引用更新为 gpt-5.2

```
OpenAI Realtime API 定价（2025 GA 标价）：
├─ 音频输入：  $0.06 / 分钟（约 $0.001/秒）
├─ 音频输出：  $0.24 / 分钟
├─ 文本输入：  $5.00 / 1M tokens
├─ 文本输出：  $20.00 / 1M tokens
└─ 典型通话：  5 分钟对话 ≈ $1.50

对比传统管道：
├─ Whisper STT:    $0.006 / 分钟
├─ GPT-5.2:        ~$0.01 / 请求
├─ TTS:            $0.015 / 1K 字符
└─ 管道总计 5 分钟 ≈ $0.30（更便宜但延迟高）
```

## 3. ElevenLabs Conversational AI 2.0

> 🔄 更新于 2026-04-21

业界最佳语音质量和轮次管理，2026 年已从 TTS 工具升级为完整的对话式音频基础设施平台。Eleven v3 Conversational 模型 + Expressive Mode 让 AI 语音具备情感智能。来源：[ElevenLabs Changelog](https://elevenlabs.io/docs/changelog)

<!-- version-check: ElevenLabs Eleven v3 Conversational, checked 2026-04-21 -->

```
核心特性（2026）：
├─ Eleven v3 Conversational：情感智能语音模型
├─ Expressive Mode：笑声、叹息等情感标签
├─ 高级轮次管理：理解 "嗯"、"啊" 等语气词
├─ 版本控制：Agent 分支、部署、合并（2026-01）
├─ 全球路由：自动选择最近服务器（2026-02 默认）
├─ 对话脱敏：自动脱敏姓名、邮箱等敏感信息
├─ 多 Agent 评估：按 Agent 独立评估对话质量
├─ Widget SDK：React / React Native / Web 组件
├─ 工具调用：自定义工具 + 知识库集成
├─ 30+ 语言：多语言支持，语音克隆
└─ WhatsApp 集成：连接 WhatsApp Business 账户
```

### Python SDK 示例

```python
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai import ConversationalAI

client = ElevenLabs(api_key="your-api-key")

# 创建 Conversational AI Agent
agent = client.conversational_ai.create_agent(
    name="中文客服助手",
    first_message="您好！我是智能客服，请问有什么可以帮您？",
    language="zh",
    llm={
        "provider": "openai",
        "model": "gpt-5.2",  # 修复于 2026-05-20: gpt-4o → gpt-5.2
        "system_prompt": "你是一个专业的中文客服，简洁友好地回答问题。"
    },
    voice={
        "voice_id": "your-cloned-voice-id",  # 可用克隆语音
        "stability": 0.7,
        "similarity_boost": 0.8,
    },
    tools=[
        {
            "name": "check_inventory",
            "description": "查询商品库存",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"}
                }
            },
            "webhook_url": "https://api.myshop.com/inventory"
        }
    ],
    knowledge_base={
        "files": ["faq.pdf", "product-catalog.pdf"],  # 上传知识库文档
    }
)

print(f"Agent ID: {agent.agent_id}")
```

### React Widget 集成

```typescript
import { useConversation } from "@11labs/react";

function VoiceAgent() {
  const conversation = useConversation({
    agentId: "your-agent-id",
    onMessage: (msg) => console.log("Agent:", msg.message),
    onError: (err) => console.error("Error:", err),
    onStatusChange: (status) => console.log("Status:", status),
  });

  return (
    <div>
      <button onClick={() => conversation.startSession()}>
        🎤 开始对话
      </button>
      <button onClick={() => conversation.endSession()}>
        ⏹ 结束对话
      </button>
      <p>状态: {conversation.status}</p>
      <p>Agent 正在说话: {conversation.isSpeaking ? "是" : "否"}</p>
    </div>
  );
}
```

## 4. LiveKit Agents（开源）

> 🔄 更新于 2026-05-20

开源实时通信框架，Agent 作为"参与者"加入音视频房间。**Python Agents v1.5.5**（2026-04 发布）持续改进自适应中断处理和动态端点检测，是语音 Agent 开源方案的标杆。来源：[LiveKit Community](https://community.livekit.io/t/released-agents-python-1-5-5-and-agents-nodejs-1-2-8/918)

<!-- version-check: LiveKit Agents Python 1.5.5, NodeJS 1.2.8, checked 2026-05-20 -->
<!-- 修复于 2026-05-20: 1.5.2 → 1.5.5（PyPI 确认） -->

```
核心特性（v1.5.x）：
├─ 自适应中断处理：ML 模型区分真实打断和背景噪音
│   ├─ 86% 精度，100% 召回（500ms 重叠语音）
│   ├─ 拒绝 51% 的 VAD 误报
│   ├─ 比纯 VAD 快 64% 检测真实中断
│   └─ 推理 ≤30ms，误判时自动恢复播放
├─ 动态端点检测：根据对话节奏自适应静默阈值
├─ 会话用量追踪：按模型/提供商分类的 Token/字符/音频统计
├─ 每轮延迟指标：转录延迟、轮次结束延迟
├─ 上下文摘要感知工具调用：摘要保留 Function Call 上下文
├─ 插件化架构：灵活组合 STT/LLM/TTS
├─ Python 3.10+：支持 Python 3.14
└─ Apache 2.0 开源
```

```
┌─────────────── LiveKit Agent 架构 ───────────────┐
│                                                    │
│  ┌──────────┐     LiveKit Server     ┌──────────┐│
│  │  用户     │ ←── WebRTC 音视频 ──→ │  Agent   ││
│  │ (浏览器)  │     (SFU 服务器)       │ (Python) ││
│  └──────────┘                        └────┬─────┘│
│                                           │      │
│                              ┌────────────┼──────┤
│                              │ Pipeline 插件      │
│                              ├────────────────────┤
│                              │ STT: Deepgram /    │
│                              │      Whisper /     │
│                              │      Azure Speech  │
│                              ├────────────────────┤
│                              │ LLM: OpenAI /      │
│                              │      Anthropic /   │
│                              │      Gemini        │
│                              ├────────────────────┤
│                              │ TTS: ElevenLabs /  │
│                              │      Cartesia /    │
│                              │      Azure Speech  │
│                              └────────────────────┘
└────────────────────────────────────────────────────┘
```

### Python Agent Pipeline 示例

```python
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, elevenlabs

async def entrypoint(ctx: JobContext):
    """LiveKit Voice Agent — 管道式架构"""

    # 等待用户加入房间
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()

    # 构建语音管道：VAD → STT → LLM → TTS
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),                    # 语音活动检测
        stt=deepgram.STT(language="zh"),           # 语音转文本
        llm=openai.LLM(model="gpt-5.2"),          # 修复于 2026-05-20: gpt-4o → gpt-5.2
        tts=elevenlabs.TTS(                        # 文本转语音
            voice_id="your-voice-id",
            model_id="eleven_turbo_v2_5",
        ),
        chat_ctx=openai.ChatContext().append(
            role="system",
            text="你是一个友好的中文语音助手，回答简洁明了。"
        ),
    )

    # Agent 加入房间并开始对话
    agent.start(ctx.room, participant)
    await agent.say("你好！我是语音助手，请问有什么可以帮您？")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

### 部署方式

```
LiveKit 部署选项：
├─ LiveKit Cloud：托管服务，免运维
├─ 自托管：Docker / Kubernetes 部署
│   docker run -d \
│     -p 7880:7880 -p 7881:7881 -p 7882:7882/udp \
│     livekit/livekit-server \
│     --keys "api-key: secret-key"
└─ 混合：LiveKit Cloud + 自托管 Agent Worker
```

## 5. Vapi — 电话语音 AI 平台

专注电话自动化的语音 AI 平台，支持呼入/呼出，Webhook 集成。

```
核心特性：
├─ 电话集成：呼入/呼出，PSTN/SIP 支持
├─ Function Calling：语音中调用自定义 API
├─ 知识库：上传文档，Agent 自动检索回答
├─ Webhook：通话事件实时推送
├─ Dashboard：通话监控、分析、录音回放
├─ 多 LLM：OpenAI / Anthropic / Groq / 自定义
└─ 多 TTS：ElevenLabs / PlayHT / Deepgram
```

```python
# Vapi — 创建呼出电话 Agent
import requests

response = requests.post(
    "https://api.vapi.ai/call/phone",
    headers={"Authorization": "Bearer your-vapi-key"},
    json={
        "assistantId": "your-assistant-id",
        "phoneNumberId": "your-phone-number-id",
        "customer": {
            "number": "+8613800138000",  # 拨打的电话号码
        },
        "assistantOverrides": {
            "firstMessage": "您好，这里是XX公司，请问是张先生吗？",
            "model": {
                "provider": "openai",
                "model": "gpt-5.2",
                "systemPrompt": "你是一个专业的电话销售助手...",
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "schedule_meeting",
                            "description": "为客户预约会议",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "date": {"type": "string"},
                                    "time": {"type": "string"}
                                }
                            }
                        },
                        "server": {
                            "url": "https://api.mycompany.com/webhook/vapi"
                        }
                    }
                ]
            }
        }
    }
)
print(response.json())
```

## 6. Retell AI — 对话式电话 Agent

专注低延迟自然对话的电话 Agent 平台。

```
核心特性：
├─ 超低延迟：端到端 ~800ms
├─ 自然对话：支持打断、停顿、语气词
├─ 电话集成：Twilio / Vonage / SIP
├─ 多语言：英语、中文、日语等
├─ 分析面板：通话质量、情感分析
└─ 合规：HIPAA / SOC2 认证
```

```python
# Retell AI — 创建语音 Agent
from retell import Retell

client = Retell(api_key="your-retell-key")

agent = client.agent.create(
    agent_name="客服 Agent",
    voice_id="11labs-Adrian",
    llm_websocket_url="wss://your-server.com/llm-ws",  # 自定义 LLM
    language="zh-CN",
    response_engine={
        "type": "retell-llm",
        "llm_id": "your-llm-id",
    },
    ambient_sound="office",  # 背景音效
    interruption_sensitivity=0.8,
    boosted_keywords=["订单", "退款", "投诉"],  # 关键词增强识别
)
```

## 7. Gemini Live API（Google）

Google 的双向音视频流式 API，原生多模态（看+听+说）。

> 🔄 更新于 2026-05-20

<!-- version-check: gemini-3.1-flash-live (2026-03), gemini-3.5-flash (2026-05-19 I/O 发布), checked 2026-05-20 -->
<!-- 修复于 2026-05-20: gemini-2.0-flash-live → gemini-3.1-flash-live（2026-03 发布）；Gemini 3.5 Flash 在 Google I/O 2026 发布 -->

**当前模型**（2026-05）：
- `gemini-3.1-flash-live`：Gemini Live 当前主力模型（2026-03 发布），低延迟语音交互
- `gemini-3.5-flash`：Google I/O 2026 发布的最新主力模型（2026-05-19），更强的 Agent 能力
- 旧的 `gemini-2.0-flash-live` 已被 3.x 系列取代

```
核心特性：
├─ 双向流：音频 + 视频实时双向传输
├─ 原生多模态：摄像头画面 + 语音同时处理
├─ Google ADK 集成：与 Agent Development Kit 无缝配合
├─ 长上下文：1M tokens 上下文窗口（Gemini 3.5 Flash）
├─ 工具调用：Function Calling + Google Search
└─ 免费额度：Gemini API 有免费调用额度
```

```python
import asyncio
from google import genai

client = genai.Client(api_key="your-gemini-key")
model = "gemini-3.1-flash-live"  # 修复于 2026-05-20: 旧的 gemini-2.0-flash-live 已被取代

config = {
    "response_modalities": ["AUDIO"],
    "speech_config": {
        "voice_config": {
            "prebuilt_voice_config": {
                "voice_name": "Kore"  # Aoede, Charon, Fenrir, Kore, Puck
            }
        }
    },
    "tools": [
        {"function_declarations": [
            {
                "name": "get_weather",
                "description": "获取指定城市的天气",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            }
        ]}
    ]
}

async def gemini_live_session():
    async with client.aio.live.connect(model=model, config=config) as session:
        # 发送音频流
        # audio_chunk = read_from_microphone()
        # await session.send({"data": audio_chunk, "mime_type": "audio/pcm"})

        # 接收响应
        async for response in session.receive():
            if response.data:
                play_audio(response.data)  # 播放音频响应
            if response.text:
                print(f"文本: {response.text}")
            if response.tool_call:
                # 处理工具调用
                result = handle_tool_call(response.tool_call)
                await session.send({"tool_response": result})

asyncio.run(gemini_live_session())
```

## 8. 综合对比表

| 特性 | OpenAI Realtime | ElevenLabs | LiveKit | Vapi | Retell AI | Gemini Live |
|------|----------------|------------|---------|------|-----------|-------------|
| 方式 | 原生音频模型 | STT+LLM+TTS | 插件管道 | 托管平台 | 托管平台 | 原生多模态 |
| 最新模型 | gpt-realtime-2 | Eleven v3 Conv. | v1.5.5 | — | — | Gemini 3.1 Flash Live / 3.5 Flash |
| 延迟 | ~300ms-1s | ~1s | ~1-2s（取决插件） | ~600ms | ~800ms | ~500ms-1s |
| 语言 | 50+ | 30+ | 取决 STT/TTS 插件 | 20+ | 10+ | 40+ |
| 电话支持 | ✅ SIP | ❌（需集成） | ✅ SIP/PSTN | ✅ 核心功能 | ✅ 核心功能 | ❌ |
| 开源 | ❌ | ❌ | ✅ Apache 2.0 | ❌ | ❌ | ❌ |
| MCP 支持 | ✅ 远程 MCP | ❌ | 可自行集成 | ❌ | ❌ | 通过 ADK |
| 视频/图像 | ✅ 图像输入 | ❌ | ✅ 音视频 | ❌ | ❌ | ✅ 音视频 |
| Function Call | ✅ 原生 | ✅ Webhook | ✅ 自定义 | ✅ Webhook | ✅ WebSocket | ✅ 原生 |
| 语音克隆 | ❌ | ✅ 业界最佳 | 取决 TTS 插件 | ✅（通过 TTS） | ✅ | ❌ |
| 自托管 | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| 版本控制 | ❌ | ✅ 分支/部署 | ❌ | ❌ | ❌ | ❌ |
| 定价 | $0.06-0.24/分 | $0.01-0.08/分 | 开源免费+云托管 | $0.05/分起 | $0.07-0.14/分 | 免费额度+按量 |
| 最佳场景 | 低延迟语音助手 | 高质量语音体验 | 自定义管道 | 电话自动化 | 电话客服 | 多模态交互 |

## 9. 应用场景

```
┌─────────────── 语音 Agent 应用场景 ───────────────┐
│                                                     │
│  客户服务                    销售与营销               │
│  ├─ 7×24 智能客服热线        ├─ 自动外呼营销          │
│  ├─ 订单查询/退换货          ├─ 预约确认/提醒         │
│  ├─ 技术支持                 ├─ 客户回访              │
│  └─ 人工转接兜底             └─ 线索筛选              │
│                                                     │
│  语音助手                    无障碍/辅助              │
│  ├─ 智能家居控制             ├─ 视障用户交互          │
│  ├─ 车载语音助手             ├─ 老年人友好界面         │
│  ├─ 会议纪要/翻译            ├─ 多语言实时翻译        │
│  └─ 语音搜索                 └─ 语音导航              │
│                                                     │
│  医疗健康                    教育培训                 │
│  ├─ 预约挂号                 ├─ 口语练习伙伴          │
│  ├─ 用药提醒                 ├─ 面试模拟              │
│  ├─ 症状初筛                 ├─ 语言学习              │
│  └─ 心理健康陪伴             └─ 互动式教学            │
└─────────────────────────────────────────────────────┘
```

## 10. 选型决策指南

```
你的需求是什么？
│
├─ 最低延迟 + 最自然的对话体验
│   └─ OpenAI Realtime API（原生音频，无管道延迟）
│
├─ 最佳语音质量 + 语音克隆
│   └─ ElevenLabs Conversational AI
│
├─ 电话自动化（呼入/呼出）
│   ├─ 快速上手，托管服务    → Vapi
│   ├─ 低延迟，企业合规      → Retell AI
│   └─ 自建，OpenAI 生态    → OpenAI Realtime + SIP
│
├─ 完全自定义 + 自托管
│   └─ LiveKit Agents（开源，插件化，灵活组合）
│
├─ 多模态（语音 + 视频 + 图像）
│   └─ Gemini Live API（原生多模态）
│
├─ 预算有限
│   ├─ 开源自托管           → LiveKit
│   └─ 有免费额度           → Gemini Live API
│
└─ 不确定？
    ├─ 原型验证             → OpenAI Realtime（最快出效果）
    └─ 生产部署             → 根据是否需要电话选 Vapi/Retell 或 OpenAI
```

## 11. 关键技术概念

### VAD（语音活动检测）

```
VAD 决定"用户是否在说话"：
├─ 服务端 VAD：服务器判断（OpenAI server_vad）
│   优点：统一处理，减少客户端负担
│   缺点：网络延迟影响判断
├─ 客户端 VAD：浏览器/App 端判断
│   优点：响应更快
│   缺点：需要客户端计算资源
└─ 混合 VAD：两端协同
    推荐：大多数场景用服务端 VAD
```

### 中断处理（Interruption）

```
用户打断 Agent 说话时的处理策略：
├─ 立即停止：Agent 立刻停止说话（OpenAI 默认）
├─ 完成当前句：Agent 说完当前句子再停
├─ 忽略：Agent 继续说完（不推荐）
└─ 智能判断：根据用户语气判断是否真的要打断
    （ElevenLabs 的高级轮次管理）
```

## 12. 相关文档

<!-- 修复于 2026-05-20: 内部链接缺少编号前缀，全部补全 -->

- Agent 协议 → `02-Agent协议/01-Agent协议全景图.md`（MCP 协议基础）
- Function Calling → `07-工具与Function Calling/01-Function Calling机制.md`
- 实时通信 → `02-语音Agent开发实战.md`（本目录，开发实战指南）
- 模型服务 → `12-模型服务/01-OpenAI与Claude API.md`（API 调用基础）
- 工具平台 → `08-工具平台与沙箱/01-Agent工具生态总览.md`
## 🎬 推荐视频资源

### 🌐 YouTube
- [OpenAI - Realtime API Demo](https://www.youtube.com/watch?v=JhCl-GeT4jw) — OpenAI Realtime API演示
- [ElevenLabs - Conversational AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — ElevenLabs语音Agent
- [LiveKit - Build Voice AI Agent](https://www.youtube.com/watch?v=dcgRMOG605w) — LiveKit语音Agent教程

### 📺 B站
- [语音Agent开发实战](https://www.bilibili.com/video/BV1dH4y1P7FY) — 语音Agent中文教程

### 📖 官方文档
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — OpenAI实时API文档
- [ElevenLabs Docs](https://elevenlabs.io/docs) — ElevenLabs文档
- [LiveKit Agents](https://docs.livekit.io/agents/) — LiveKit Agents文档
- [Vapi Docs](https://docs.vapi.ai/) — Vapi语音Agent文档
