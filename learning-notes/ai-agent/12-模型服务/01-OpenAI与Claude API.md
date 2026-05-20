# OpenAI 与 Claude API
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. OpenAI Chat Completions API

<!-- version-check: GPT-5.2 gpt-5.2, checked 2026-05-13 -->
<!-- 修复于 2026-05-13: gpt-4o → gpt-5.2（gpt-4o 已从 ChatGPT 退役，API 仍可用但推荐使用新模型） -->

```python
from openai import OpenAI

client = OpenAI()  # 自动读取 OPENAI_API_KEY

# 基础调用
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "解释什么是 RAG"},
    ],
    temperature=0.7,
    max_tokens=1000,
)
print(response.choices[0].message.content)
print(f"Token 用量: {response.usage.prompt_tokens} + {response.usage.completion_tokens}")

# 流式响应
stream = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "写一首关于编程的诗"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## 2. Anthropic Messages API

<!-- version-check: Claude Sonnet 4.6 claude-sonnet-4-6-20260217, checked 2026-04-18 -->

```python
import anthropic

client = anthropic.Anthropic()  # 自动读取 ANTHROPIC_API_KEY

# 基础调用
response = client.messages.create(
    model="claude-sonnet-4-6-20260217",  # Sonnet 4.6，$3/$15 per MTok
    max_tokens=1024,
    system="你是一个专业的技术顾问",
    messages=[{"role": "user", "content": "对比 MCP 和 A2A 协议"}],
)
print(response.content[0].text)
print(f"Token: {response.usage.input_tokens} + {response.usage.output_tokens}")

# 流式响应
with client.messages.stream(
    model="claude-sonnet-4-6-20260217",
    max_tokens=1024,
    messages=[{"role": "user", "content": "解释 Transformer 架构"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

> 🔄 更新于 2026-04-20
>
> **Claude Opus 4.7**（2026-04-16）：Anthropic 最强 GA 模型，替代 Opus 4.6 成为默认 Opus。`claude-opus-4-7`，定价不变 $5/$25 per MTok，1M 上下文窗口，128K 输出。核心提升：编码基准 +13%、Rakuten-SWE-Bench 生产任务 3x、高分辨率视觉 3.75MP（之前 1.15MP）、新增 xhigh 推理等级、Task Budgets 公测、文件系统级跨会话记忆。SWE-bench Verified 87.6%，CursorBench 70%。注意：新 tokenizer 可能导致 token 数量增加 1.0-1.35x。
> 来源：[Anthropic 官方](https://www.anthropic.com/news/) / [felloai](https://felloai.com/anthropic-claude-opus-4-7/)
>
> **Claude 4.6 系列**（2026-02）：Opus 4.6（`claude-opus-4-6`，$5/$25 per MTok，128K 输出）和 Sonnet 4.6（`claude-sonnet-4-6`，$3/$15 per MTok，64K 输出），均支持 1M 上下文窗口（beta）、Extended Thinking。Sonnet 4.6 在 Claude Code 测试中 70% 的情况下优于 Sonnet 4.5，59% 优于 Opus 4.5。
> 来源：[Anthropic 官网](https://www.anthropic.com/claude/sonnet)、[Claude API 定价](https://developer.puter.com/tutorials/claude-api-pricing/)
>
> **GPT-5.4-Cyber**（2026-04-14）：OpenAI 发布首个防御性网络安全微调模型，基于 GPT-5.4，降低安全场景的拒绝边界，增强二进制逆向工程能力。通过 Trusted Access for Cyber（TAC）计划面向验证用户开放。
> 来源：[OpenAI 官方博客](https://openai.com/index/scaling-trusted-access-for-cyber-defense/)
>
> **OpenAI Assistants API 废弃**：2026-08-26 正式关闭，迁移至 Responses API + Conversations API。Responses API 支持内置工具（deep research、MCP、computer use），单次调用可运行多步工作流。
> 来源：[OpenAI 社区公告](https://community.openai.com/t/assistants-api-beta-deprecation-august-26-2026-sunset/1354666)
>
> 🔄 更新于 2026-05-05
>
> **GPT-5.5**（2026-04-23）：OpenAI 最新旗舰模型（代号 Spud），$5/M 输入、$30/M 输出（GPT-5.5 Pro：$30/$180）。1M+ 上下文窗口（922K 输入 + 128K 输出），支持文本和图像输入。API 于 4/24 开放，支持 Responses API 和 Chat Completions。知识截止日期 2025-12-01。相比 GPT-5.4 价格翻倍但推理能力显著提升。
> 来源：[OpenAI API](https://openai.com/api)、[OpenRouter](https://openrouter.ai/openai/gpt-5.5)

<!-- version-check: Claude Opus 4.7 claude-opus-4-7, Sonnet 4/Opus 4 deprecated 2026-06-15, checked 2026-05-20 -->
<!-- version-check: GPT-5.5, checked 2026-05-05 -->

> 🔄 更新于 2026-04-21
>
> **Anthropic 多云算力战略**：Anthropic 在两周内完成了两笔历史性算力协议，锁定约 8.5GW 总算力：
> - 4/6：与 Google/Broadcom 签署 3.5GW 下一代 TPU 协议（2027 年上线）
> - 4/20：与 Amazon 签署最高 5GW Trainium 协议（含 Trainium2 + Trainium3），Amazon 追加投资最高 250 亿美元（首批 50 亿立即到位），Anthropic 估值达 3800 亿美元
>
> Anthropic 承诺未来十年在 AWS 投入超 1000 亿美元。当前年化收入已超 300 亿美元，超 10 万客户在 Bedrock 上运行 Claude。这种同时锁定 AWS 和 GCP 两大云平台定制芯片产能的多云算力战略在 AI 公司中尚属首次。对开发者的影响：Claude API 推理成本有望进一步下降，Bedrock 上的 Agent 部署体验将持续改善。
> 来源：[Anthropic](https://www.anthropic.com/news/anthropic-amazon-compute) / [Anthropic](https://www.anthropic.com/news/google-broadcom-partnership-compute) / [CNBC](https://www.cnbc.com/2026/04/20/amazon-invest-up-to-25-billion-in-anthropic-part-of-ai-infrastructure.html)

## 3. 多模态输入

```python
import base64

# OpenAI 图片输入
with open("chart.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "分析这张图表的趋势"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{image_data}"
            }},
        ],
    }],
)

# Claude 图片输入
response = anthropic_client.messages.create(
    model="claude-sonnet-4-6-20260217",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_data,
            }},
            {"type": "text", "text": "描述这张图片"},
        ],
    }],
)
```

## 4. Batch API（批量处理）

```python
# OpenAI Batch API：大批量请求，成本降低 50%
import json

# 1. 准备批量请求文件
requests = []
for i, question in enumerate(questions):
    requests.append({
        "custom_id": f"req-{i}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-5-mini",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500,
        },
    })

# 写入 JSONL 文件
with open("batch_input.jsonl", "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")

# 2. 上传并创建批量任务
batch_file = client.files.create(file=open("batch_input.jsonl", "rb"), purpose="batch")
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
)

# 3. 查询状态
status = client.batches.retrieve(batch.id)
print(f"状态: {status.status}")  # validating → in_progress → completed

# 4. 获取结果
if status.status == "completed":
    result_file = client.files.content(status.output_file_id)
    results = [json.loads(line) for line in result_file.text.strip().split("\n")]
```

## 5. 成本优化策略

```python
# 策略 1：模型分级使用
def select_model(task_complexity: str) -> str:
    models = {
        "simple": "gpt-5-mini",        # $0.25/1M input — 简单任务
        "medium": "gpt-5.2",           # $1.75/1M input — 常规任务
        "complex": "claude-opus-4-7",     # $5/1M input — 复杂推理
    }
    return models.get(task_complexity, "gpt-5-mini")

# 策略 2：Prompt 缓存（Claude）
# 对于重复的 system prompt，Claude 自动缓存，节省 90% 输入成本
response = anthropic_client.messages.create(
    model="claude-sonnet-4-6-20260217",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": "很长的系统提示...",
        "cache_control": {"type": "ephemeral"},  # 启用缓存
    }],
    messages=[{"role": "user", "content": "问题"}],
)

# 策略 3：Token 用量监控
class TokenTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0

    def track(self, usage):
        self.total_input += usage.prompt_tokens
        self.total_output += usage.completion_tokens

    @property
    def estimated_cost(self) -> float:
        # GPT-5.2 价格
        return (self.total_input * 1.75 + self.total_output * 14) / 1_000_000
```
## 🎬 推荐视频资源

- [DeepLearning.AI - ChatGPT Prompt Engineering for Developers](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) — OpenAI API实战（免费）
- [Anthropic - Claude API Tutorial](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude API使用教程
