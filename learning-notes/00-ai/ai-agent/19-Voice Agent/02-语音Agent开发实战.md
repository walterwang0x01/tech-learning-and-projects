# 语音 Agent 开发实战
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

本文是语音 Agent 的实战开发指南，覆盖 OpenAI Realtime API、LiveKit Agents、ElevenLabs 三大平台的完整开发流程，以及语音 Agent 的核心设计模式。

```
┌─────────────── 语音 Agent 开发全景 ───────────────┐
│                                                     │
│  平台选择                                           │
│  ├─ OpenAI Realtime API → 原生音频，最低延迟        │
│  ├─ LiveKit Agents      → 开源，插件化管道          │
│  └─ ElevenLabs          → 最佳语音质量，Widget 集成 │
│                                                     │
│  开发流程                                           │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐           │
│  │连接建立│→│会话配置│→│事件处理│→│工具调用│           │
│  └──────┘  └──────┘  └──────┘  └──────┘           │
│       ↓                              ↓              │
│  ┌──────┐                      ┌──────┐            │
│  │错误处理│                      │部署上线│            │
│  └──────┘                      └──────┘            │
└─────────────────────────────────────────────────────┘
```

## 2. OpenAI Realtime API 完整开发

### 2.1 环境准备

> 🔄 更新于 2026-05-20

<!-- version-check: OpenAI Realtime API GA (gpt-realtime-2 / gpt-realtime-translate / gpt-realtime-whisper), checked 2026-05-20 -->

```bash
pip install websockets openai pyaudio numpy
# pyaudio 用于麦克风录音和音频播放
# 需要系统安装 portaudio: brew install portaudio (macOS)
```

### 2.2 完整工作示例：带 Function Calling 的语音客服

```python
import asyncio
import websockets
import json
import base64
import pyaudio
import numpy as np
from datetime import datetime

# ─── 音频配置 ───
SAMPLE_RATE = 24000   # OpenAI Realtime 要求 24kHz
CHANNELS = 1
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16

# ─── 工具定义 ───
TOOLS = [
    {
        "type": "function",
        "name": "query_order",
        "description": "根据订单号查询订单状态和物流信息",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "订单编号，如 ORD-20250101-001"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "type": "function",
        "name": "create_ticket",
        "description": "创建客服工单",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["退款", "换货", "投诉", "咨询"],
                    "description": "工单类别"
                },
                "description": {
                    "type": "string",
                    "description": "问题描述"
                },
                "priority": {
                    "type": "string",
                    "enum": ["低", "中", "高", "紧急"],
                    "description": "优先级"
                }
            },
            "required": ["category", "description"]
        }
    },
    {
        "type": "function",
        "name": "transfer_to_human",
        "description": "当用户明确要求或问题超出能力范围时，转接人工客服",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "转接原因"},
                "department": {
                    "type": "string",
                    "enum": ["售后", "技术", "投诉", "VIP"],
                }
            },
            "required": ["reason"]
        }
    }
]

# ─── 工具执行函数 ───
async def execute_tool(name: str, args: dict) -> str:
    """模拟工具执行，生产环境替换为真实 API 调用"""
    if name == "query_order":
        # 模拟数据库查询
        return json.dumps({
            "order_id": args["order_id"],
            "status": "已发货",
            "courier": "顺丰速运",
            "tracking": "SF1234567890",
            "estimated_delivery": "2025-08-15",
        })
    elif name == "create_ticket":
        return json.dumps({
            "ticket_id": f"TK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "已创建",
            "category": args["category"],
        })
    elif name == "transfer_to_human":
        return json.dumps({
            "status": "transferring",
            "queue_position": 3,
            "estimated_wait": "2分钟",
        })
    return json.dumps({"error": "未知工具"})


class RealtimeVoiceAgent:
    """OpenAI Realtime API 语音 Agent 完整实现"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.ws = None
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_playing = False

    async def connect(self):
        """建立 WebSocket 连接（GA 版本）"""
        # 修复于 2026-05-20: 模型名 gpt-4o-realtime-preview → gpt-realtime-2，移除已废弃的 OpenAI-Beta header
        url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            # 注意：GA 版本不再需要 "OpenAI-Beta": "realtime=v1"
        }
        self.ws = await websockets.connect(
            url,
            extra_headers=headers,
            ping_interval=20,      # 保活心跳
            ping_timeout=10,
            max_size=10 * 1024 * 1024,  # 10MB 最大消息
        )
        print("✅ WebSocket 连接成功")

    async def configure_session(self):
        """配置会话参数"""
        await self.ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "coral",
                "instructions": """你是「小智」，XX 电商平台的 AI 客服。
规则：
1. 用简洁友好的中文回答，每次回复不超过 3 句话
2. 涉及订单问题先用 query_order 查询
3. 用户要求退款/换货时创建工单
4. 无法解决的问题转人工客服
5. 不要编造信息，查不到就说查不到""",
                "tools": TOOLS,
                "tool_choice": "auto",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 600,
                },
                "input_audio_transcription": {
                    "model": "whisper-1",  # 同时输出用户语音的文字转录
                    # ⚠️ 注意：GA 版本对此配置有变更，新版可使用 gpt-realtime-whisper 模型，请参考最新文档
                },
                "temperature": 0.7,
                "max_response_output_tokens": 500,
            }
        }))
        print("✅ 会话配置完成")

    async def send_audio(self):
        """从麦克风捕获音频并发送"""
        stream = self.audio.open(
            format=FORMAT, channels=CHANNELS,
            rate=SAMPLE_RATE, input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        self.is_recording = True
        print("🎤 开始录音...")

        try:
            while self.is_recording:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                encoded = base64.b64encode(data).decode("utf-8")
                await self.ws.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": encoded,
                }))
                await asyncio.sleep(0.01)  # 避免阻塞事件循环
        finally:
            stream.stop_stream()
            stream.close()

    async def receive_events(self):
        """接收并处理服务端事件"""
        audio_buffer = bytearray()

        async for message in self.ws:
            event = json.loads(message)
            event_type = event.get("type", "")

            match event_type:
                # ─── 用户语音转录 ───
                case "conversation.item.input_audio_transcription.completed":
                    print(f"👤 用户: {event.get('transcript', '')}")

                # ─── Agent 文本响应 ───
                case "response.text.delta":
                    print(event.get("delta", ""), end="", flush=True)

                case "response.text.done":
                    print()  # 换行

                # ─── Agent 音频响应 ───
                case "response.audio.delta":
                    audio_data = base64.b64decode(event["delta"])
                    audio_buffer.extend(audio_data)

                case "response.audio.done":
                    if audio_buffer:
                        self._play_audio(bytes(audio_buffer))
                        audio_buffer.clear()

                # ─── Function Calling ───
                case "response.function_call_arguments.done":
                    name = event["name"]
                    args = json.loads(event["arguments"])
                    call_id = event["call_id"]
                    print(f"🔧 调用工具: {name}({args})")

                    result = await execute_tool(name, args)
                    print(f"📋 工具结果: {result}")

                    # 返回工具结果
                    await self.ws.send(json.dumps({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": result,
                        }
                    }))
                    await self.ws.send(json.dumps({
                        "type": "response.create"
                    }))

                # ─── 中断处理 ───
                case "input_audio_buffer.speech_started":
                    print("🔇 用户开始说话，Agent 停止播放")
                    self.is_playing = False

                # ─── 错误处理 ───
                case "error":
                    error = event.get("error", {})
                    print(f"❌ 错误: {error.get('message', '未知错误')}")
                    if error.get("code") == "session_expired":
                        await self.reconnect()

    def _play_audio(self, audio_data: bytes):
        """播放音频"""
        stream = self.audio.open(
            format=FORMAT, channels=CHANNELS,
            rate=SAMPLE_RATE, output=True,
        )
        self.is_playing = True
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

    async def reconnect(self):
        """断线重连"""
        print("🔄 正在重连...")
        try:
            await self.ws.close()
        except Exception:
            pass
        await asyncio.sleep(1)
        await self.connect()
        await self.configure_session()
        print("✅ 重连成功")

    async def run(self):
        """启动 Agent"""
        await self.connect()
        await self.configure_session()

        # 并行运行：发送音频 + 接收事件
        await asyncio.gather(
            self.send_audio(),
            self.receive_events(),
        )

    def cleanup(self):
        self.is_recording = False
        self.audio.terminate()


# 启动
if __name__ == "__main__":
    agent = RealtimeVoiceAgent(api_key="sk-xxx")
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        agent.cleanup()
        print("\n👋 Agent 已停止")
```

## 3. LiveKit Agents 完整开发

### 3.1 环境准备

```bash
pip install "livekit-agents[openai,deepgram,silero,elevenlabs]~=1.0"
# 或指定插件
pip install livekit-agents livekit-plugins-openai livekit-plugins-deepgram \
            livekit-plugins-silero livekit-plugins-elevenlabs
```

### 3.2 完整 Pipeline Agent

```python
"""LiveKit Voice Agent — 完整管道式语音 Agent"""

import logging
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, elevenlabs

logger = logging.getLogger("voice-agent")

# ─── 自定义工具 ───
class AgentTools(llm.FunctionContext):
    """Agent 可调用的工具集"""

    @llm.ai_callable(description="查询商品价格和库存")
    async def check_product(
        self,
        product_name: str = llm.TypeInfo(description="商品名称"),
    ) -> str:
        logger.info(f"查询商品: {product_name}")
        # 模拟数据库查询
        products = {
            "iPhone 16": {"price": 7999, "stock": 150},
            "MacBook Pro": {"price": 14999, "stock": 30},
            "AirPods Pro": {"price": 1899, "stock": 500},
        }
        product = products.get(product_name)
        if product:
            return f"{product_name} 价格 {product['price']} 元，库存 {product['stock']} 件"
        return f"未找到商品: {product_name}"

    @llm.ai_callable(description="创建退货申请")
    async def create_return(
        self,
        order_id: str = llm.TypeInfo(description="订单号"),
        reason: str = llm.TypeInfo(description="退货原因"),
    ) -> str:
        logger.info(f"创建退货: 订单 {order_id}, 原因: {reason}")
        return f"退货申请已创建，订单 {order_id}，预计 3-5 个工作日处理完成"

    @llm.ai_callable(description="转接人工客服")
    async def transfer_human(
        self,
        reason: str = llm.TypeInfo(description="转接原因"),
    ) -> str:
        logger.info(f"转接人工: {reason}")
        return "正在为您转接人工客服，请稍候..."


async def entrypoint(ctx: JobContext):
    """Agent 入口函数"""

    # 连接到 LiveKit 房间
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"用户 {participant.identity} 已加入")

    # 初始化工具
    tools = AgentTools()

    # 构建对话上下文
    chat_ctx = llm.ChatContext().append(
        role="system",
        text="""你是「小助」，一个友好的中文语音客服助手。
规则：
- 回答简洁，每次不超过 2-3 句话（语音对话要简短）
- 涉及商品问题用 check_product 查询
- 退货请求用 create_return 处理
- 无法解决的问题用 transfer_human 转人工
- 语气亲切自然，像朋友聊天一样"""
    )

    # 构建语音管道
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),                     # 语音活动检测
        stt=deepgram.STT(                          # 语音转文本
            language="zh",
            model="nova-2",
        ),
        llm=openai.LLM(                           # 大语言模型
            model="gpt-5.2",                       # 修复于 2026-05-20: gpt-4o → gpt-5.2
            temperature=0.7,
        ),
        tts=elevenlabs.TTS(                        # 文本转语音
            voice_id="your-chinese-voice-id",
            model_id="eleven_turbo_v2_5",
            language="zh",
        ),
        chat_ctx=chat_ctx,
        fnc_ctx=tools,                             # 注册工具
        # 高级配置
        min_endpointing_delay=0.5,                 # 最小端点检测延迟
        max_endpointing_delay=5.0,                 # 最大端点检测延迟
    )

    # 事件监听
    @agent.on("user_speech_committed")
    def on_user_speech(msg):
        logger.info(f"👤 用户: {msg.content}")

    @agent.on("agent_speech_committed")
    def on_agent_speech(msg):
        logger.info(f"🤖 Agent: {msg.content}")

    @agent.on("function_calls_collected")
    def on_function_call(calls):
        for call in calls:
            logger.info(f"🔧 工具调用: {call.function_name}")

    # 启动 Agent
    agent.start(ctx.room, participant)

    # 发送欢迎语
    await agent.say("你好！我是小助，有什么可以帮您的吗？")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # LiveKit 服务器配置（环境变量或直接指定）
            # ws_url="wss://your-livekit-server.com",
            # api_key="your-api-key",
            # api_secret="your-api-secret",
        )
    )
```

### 3.3 部署架构

```
┌─────────────── LiveKit 部署架构 ───────────────┐
│                                                  │
│  ┌──────────┐        ┌──────────────┐           │
│  │ 用户浏览器 │ WebRTC │ LiveKit SFU  │           │
│  │ (JS SDK)  │←──────→│ (媒体服务器)  │           │
│  └──────────┘        └──────┬───────┘           │
│                             │                    │
│                    ┌────────┴────────┐           │
│                    │ Agent Worker    │           │
│                    │ (Python 进程)   │           │
│                    │                 │           │
│                    │ ┌─────────────┐ │           │
│                    │ │ VAD → STT   │ │           │
│                    │ │  → LLM      │ │           │
│                    │ │  → TTS      │ │           │
│                    │ └─────────────┘ │           │
│                    └─────────────────┘           │
│                                                  │
│  部署命令：                                       │
│  python agent.py start                           │
│  python agent.py dev  # 开发模式（自动重载）       │
└──────────────────────────────────────────────────┘
```

## 4. ElevenLabs Conversational AI 开发

### 4.1 创建 Agent 并配置知识库

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="your-api-key")

# 上传知识库文档
knowledge_base = client.conversational_ai.add_to_knowledge_base(
    agent_id="your-agent-id",
    file=open("product-faq.pdf", "rb"),
)

# 创建带工具和知识库的 Agent
agent = client.conversational_ai.create_agent(
    name="电商客服",
    first_message="您好，欢迎致电 XX 商城，请问有什么可以帮您？",
    language="zh",
    llm={
        "provider": "openai",
        "model": "gpt-5.2",  # 修复于 2026-05-20: gpt-4o → gpt-5.2
        "system_prompt": """你是 XX 商城的客服助手。
- 优先从知识库中查找答案
- 回答简洁，不超过 3 句话
- 无法回答时使用 transfer_to_human 工具""",
        "temperature": 0.5,
    },
    voice={
        "voice_id": "your-voice-id",
        "stability": 0.7,
        "similarity_boost": 0.8,
        "style": 0.3,
    },
    tools=[
        {
            "name": "query_order_status",
            "description": "查询订单状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            },
            "webhook_url": "https://api.myshop.com/orders/status"
        },
        {
            "name": "transfer_to_human",
            "description": "转接人工",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"}
                }
            },
            "webhook_url": "https://api.myshop.com/transfer"
        }
    ],
    conversation_config={
        "max_duration_seconds": 600,       # 最长通话 10 分钟
        "silence_timeout_seconds": 30,     # 静默 30 秒自动结束
        "client_events": [                 # 推送给前端的事件
            "agent_response",
            "user_transcript",
            "tool_call",
        ]
    }
)
print(f"Agent 创建成功: {agent.agent_id}")
```

### 4.2 React 前端集成

```typescript
import { useConversation } from "@11labs/react";
import { useState, useCallback } from "react";

interface Message {
  role: "user" | "agent";
  content: string;
  timestamp: Date;
}

export function ElevenLabsVoiceAgent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isActive, setIsActive] = useState(false);

  const conversation = useConversation({
    agentId: process.env.NEXT_PUBLIC_ELEVENLABS_AGENT_ID!,

    onMessage: (msg) => {
      setMessages((prev) => [...prev, {
        role: msg.source === "ai" ? "agent" : "user",
        content: msg.message,
        timestamp: new Date(),
      }]);
    },

    onError: (error) => {
      console.error("ElevenLabs 错误:", error);
    },

    onStatusChange: (status) => {
      console.log("状态变更:", status);
      setIsActive(status === "connected");
    },

    onModeChange: (mode) => {
      // mode: "speaking" | "listening"
      console.log("模式:", mode);
    },
  });

  const startConversation = useCallback(async () => {
    try {
      // 请求麦克风权限
      await navigator.mediaDevices.getUserMedia({ audio: true });
      await conversation.startSession();
    } catch (err) {
      console.error("启动失败:", err);
    }
  }, [conversation]);

  return (
    <div className="voice-agent-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <span className="role">{msg.role === "agent" ? "🤖" : "👤"}</span>
            <p>{msg.content}</p>
          </div>
        ))}
      </div>

      <div className="controls">
        {!isActive ? (
          <button onClick={startConversation} className="start-btn">
            🎤 开始对话
          </button>
        ) : (
          <button onClick={() => conversation.endSession()} className="stop-btn">
            ⏹ 结束对话
          </button>
        )}
        <span className="status">
          {conversation.isSpeaking ? "🔊 Agent 说话中..." : "👂 聆听中..."}
        </span>
      </div>
    </div>
  );
}
```

## 5. 语音 Agent 设计模式

### 5.1 中断处理模式

```python
# ─── 中断处理策略 ───

class InterruptionHandler:
    """语音 Agent 中断处理"""

    def __init__(self, strategy: str = "immediate"):
        self.strategy = strategy  # immediate | finish_sentence | smart
        self.is_agent_speaking = False
        self.current_utterance = ""

    async def handle_interruption(self, user_audio_detected: bool):
        if not self.is_agent_speaking or not user_audio_detected:
            return

        match self.strategy:
            case "immediate":
                # 立即停止 Agent 说话
                await self.stop_agent_speech()
                await self.process_user_input()

            case "finish_sentence":
                # 等 Agent 说完当前句子
                await self.wait_for_sentence_end()
                await self.process_user_input()

            case "smart":
                # 智能判断：短语气词（嗯、啊）不打断
                is_real_interruption = await self.classify_interruption()
                if is_real_interruption:
                    await self.stop_agent_speech()
                    await self.process_user_input()
                # 否则忽略，Agent 继续说
```

### 5.2 静默检测与超时

```python
# ─── 静默检测 ───

class SilenceDetector:
    """检测用户是否长时间沉默"""

    def __init__(self):
        self.silence_start = None
        self.prompts = [
            "您还在吗？请问还有其他问题吗？",
            "如果没有其他问题，我就先挂了哦。",
            "感谢您的来电，再见！",
        ]
        self.prompt_index = 0

    async def on_silence(self, duration_seconds: float):
        if duration_seconds > 10 and self.prompt_index == 0:
            await self.agent_say(self.prompts[0])
            self.prompt_index = 1
        elif duration_seconds > 20 and self.prompt_index == 1:
            await self.agent_say(self.prompts[1])
            self.prompt_index = 2
        elif duration_seconds > 30:
            await self.agent_say(self.prompts[2])
            await self.end_session()
```

### 5.3 上下文跨轮次保持

```python
# ─── 对话上下文管理 ───

class ConversationContext:
    """跨轮次保持对话上下文"""

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.turns = []
        self.extracted_info = {}  # 提取的关键信息

    def add_turn(self, role: str, content: str, tool_calls=None):
        self.turns.append({
            "role": role,
            "content": content,
            "tool_calls": tool_calls,
        })
        # 超过最大轮次，压缩早期对话
        if len(self.turns) > self.max_turns:
            self._compress_history()

    def _compress_history(self):
        """压缩早期对话为摘要"""
        early_turns = self.turns[:10]
        summary = f"[早期对话摘要: 用户咨询了{len(early_turns)}轮，"
        summary += f"涉及: {', '.join(self.extracted_info.keys())}]"
        self.turns = [{"role": "system", "content": summary}] + self.turns[10:]

    def extract_info(self, key: str, value: str):
        """提取并保存关键信息（订单号、姓名等）"""
        self.extracted_info[key] = value
```

### 5.4 人工转接兜底

```python
# ─── 人工转接 ───

class HumanHandoff:
    """语音 Agent 转人工客服"""

    HANDOFF_TRIGGERS = [
        "转人工", "找人工", "真人客服",
        "你听不懂", "我要投诉",
    ]

    async def should_handoff(self, user_text: str, failed_attempts: int) -> bool:
        # 1. 用户明确要求
        if any(trigger in user_text for trigger in self.HANDOFF_TRIGGERS):
            return True
        # 2. 连续失败超过 3 次
        if failed_attempts >= 3:
            return True
        # 3. 情感检测：用户愤怒
        sentiment = await self.analyze_sentiment(user_text)
        if sentiment == "angry" and failed_attempts >= 2:
            return True
        return False

    async def execute_handoff(self, context: dict):
        """执行转接"""
        await self.agent_say("好的，正在为您转接人工客服，请稍候...")
        # 传递对话上下文给人工客服
        await self.transfer_with_context(
            department=context.get("department", "售后"),
            summary=context.get("summary", ""),
            customer_info=context.get("customer", {}),
        )
```

### 5.5 多语言支持

```python
# ─── 多语言语音 Agent ───

LANGUAGE_CONFIG = {
    "zh": {
        "stt_model": "deepgram/nova-2",
        "stt_language": "zh",
        "tts_voice": "chinese-female-voice-id",
        "greeting": "您好！请问有什么可以帮您？",
    },
    "en": {
        "stt_model": "deepgram/nova-2",
        "stt_language": "en",
        "tts_voice": "english-female-voice-id",
        "greeting": "Hello! How can I help you?",
    },
    "ja": {
        "stt_model": "deepgram/nova-2",
        "stt_language": "ja",
        "tts_voice": "japanese-female-voice-id",
        "greeting": "こんにちは！何かお手伝いできますか？",
    },
}

async def create_multilingual_agent(detected_language: str):
    """根据检测到的语言创建对应 Agent"""
    config = LANGUAGE_CONFIG.get(detected_language, LANGUAGE_CONFIG["en"])
    # 动态配置 STT/TTS 语言
    return config
```

### 5.6 电话集成（SIP/PSTN）

```
┌─────────── 电话集成架构 ───────────┐
│                                     │
│  PSTN 电话网络                      │
│  ┌──────────┐                      │
│  │ 用户手机  │                      │
│  └─────┬────┘                      │
│        │ 电话呼叫                   │
│  ┌─────┴────┐                      │
│  │ SIP Trunk │  Twilio / Vonage    │
│  │ (电话网关) │  / Telnyx           │
│  └─────┬────┘                      │
│        │ SIP 协议                   │
│  ┌─────┴────────────┐              │
│  │ Voice Agent 平台  │              │
│  │ (Vapi/Retell/     │              │
│  │  OpenAI+LiveKit)  │              │
│  └──────────────────┘              │
│                                     │
│  集成方式：                          │
│  ├─ Vapi/Retell：内置电话支持       │
│  ├─ OpenAI Realtime：SIP 连接      │
│  └─ LiveKit：SIP Bridge 插件       │
└─────────────────────────────────────┘
```

## 6. 开发平台对比

| 维度 | OpenAI Realtime | LiveKit Agents | ElevenLabs |
|------|----------------|----------------|------------|
| 开发难度 | 中（WebSocket 手动管理） | 低（SDK 封装好） | 低（Widget 即用） |
| 灵活性 | 高 | 最高（插件化） | 中 |
| 前端集成 | 需自建 | JS SDK | React Widget |
| 工具调用 | 原生 Function Calling | Python 装饰器 | Webhook |
| 调试 | 日志 + Playground | LiveKit Dashboard | ElevenLabs Dashboard |
| 生产就绪 | ✅ GA | ✅ | ✅ |
| 成本控制 | 按分钟计费 | 开源（自托管免费） | 按字符/分钟 |
| 最佳场景 | 低延迟原生语音 | 自定义管道 | 快速集成 |

## 7. 生产部署检查清单

```
语音 Agent 上线前检查：
│
├─ 音频质量
│   ├─ [ ] 测试不同网络环境（WiFi/4G/弱网）
│   ├─ [ ] 测试不同设备（手机/电脑/座机）
│   └─ [ ] 噪音环境测试
│
├─ 对话质量
│   ├─ [ ] 中断处理是否自然
│   ├─ [ ] 静默超时是否合理
│   ├─ [ ] 多轮对话上下文是否保持
│   └─ [ ] 工具调用是否正确
│
├─ 错误处理
│   ├─ [ ] WebSocket 断线重连
│   ├─ [ ] STT/TTS 服务降级
│   ├─ [ ] LLM 超时兜底
│   └─ [ ] 人工转接通道畅通
│
├─ 安全合规
│   ├─ [ ] 通话录音合规（需告知用户）
│   ├─ [ ] PII 数据脱敏
│   ├─ [ ] 敏感操作二次确认
│   └─ [ ] 通话时长限制
│
└─ 监控告警
    ├─ [ ] 延迟监控（P50/P95/P99）
    ├─ [ ] 错误率告警
    ├─ [ ] 通话质量评分
    └─ [ ] 成本监控
```

## 8. 相关文档

<!-- 修复于 2026-05-20: 内部链接缺少编号前缀，全部补全 -->

- 语音 Agent 概览 → `01-语音Agent与实时交互.md`（本目录，平台对比）
- Function Calling → `07-工具与Function Calling/01-Function Calling机制.md`
- Agent 设计模式 → `01-Agentic设计模式/02-Agentic设计模式大全.md`
- 可观测性 → `14-可观测与评估/01-LLM可观测性.md`
- 实战案例 → `23-实战案例/01-智能客服Agent.md`
## 🎬 推荐视频资源

### 🌐 YouTube
- [LiveKit - Build Your First Voice Agent in Python](https://livekit.com/blog/build-your-first-ai-voice-agent-python) — Python语音Agent教程
- [ElevenLabs - Building Conversational AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — 对话式AI构建

### 📖 官方文档
- [LiveKit Agents Python](https://docs.livekit.io/agents/) — LiveKit Python SDK
- [ElevenLabs Conversational AI](https://elevenlabs.io/docs/conversational-ai) — ElevenLabs对话AI文档
