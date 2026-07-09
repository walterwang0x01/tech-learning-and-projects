# Anthropic Claude Agent 能力
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Claude 模型家族

<!-- version-check: Claude Opus 4.7, Sonnet 4.6 (claude-sonnet-4-6), checked 2026-07-09 -->
<!-- 修复于 2026-07-09: claude-sonnet-4-6 → claude-sonnet-4-6（Anthropic 推荐无日期 ID） -->

> 🔄 更新于 2026-04-18

```
┌──────────────────────────────────────────────────────────────┐
│              Claude 模型家族（2026）                            │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  Opus    │  Sonnet  │  Haiku   │  Mythos  │  定位            │
│  最强推理 │  均衡     │  快速    │  前沿预览 │                  │
│  复杂Agent│  通用Agent│  简单任务│  研究级   │                  │
│  $5/M    │  $3/M    │  $0.25/M │  未公开   │  输入价格/1M     │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘

最新模型（2026-04-16）：
├─ Claude Opus 4.7（claude-opus-4-7）— 最新旗舰，SWE-bench Pro 64.3%
│   ├─ 1M Token 上下文窗口
│   ├─ 3.75MP 高分辨率视觉
│   ├─ xhigh 推理层级（Extended Thinking 增强）
│   ├─ 文件系统级记忆
│   └─ 新 Tokenizer 2.0（同文本可能多 ~35% Token）
├─ Claude Sonnet 4.6（claude-sonnet-4-6）— 通用性价比最优
├─ Claude Haiku 3.5 — 高吞吐简单任务
└─ Claude Mythos Preview — 最强但受限访问

Agent 场景推荐：
├─ 复杂推理/长时 Agent 工作流 → Claude Opus 4.7
├─ 通用 Agent → Claude Sonnet 4（性价比最优）
├─ 高吞吐简单任务 → Claude Haiku
└─ 代码生成 → Claude Opus 4.7（SWE-bench Pro 64.3%，CursorBench 70%）
```

> 来源：[Anthropic Newsroom](https://www.anthropic.com/news)、[Axios 报道](https://www.axios.com/2026/04/16/anthropic-claude-opus-model-mythos)

## 2. Extended Thinking（扩展思考）

让 Claude 在回答前进行深度推理，类似 Chain-of-Thought。

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,  # 思考预算（Token 数）
    },
    messages=[{
        "role": "user",
        "content": "设计一个支持 100 万并发用户的实时聊天系统架构"
    }],
)

# 查看思考过程和最终回答
for block in response.content:
    if block.type == "thinking":
        print(f"💭 思考过程:\n{block.thinking}")
    elif block.type == "text":
        print(f"\n📝 回答:\n{block.text}")
```

## 3. Tool Use（工具调用）

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_stock_price",
        "description": "获取股票实时价格",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "股票代码，如 AAPL"},
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "calculate",
        "description": "执行数学计算",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式"},
            },
            "required": ["expression"],
        },
    },
]

def execute_tool(name: str, input: dict) -> str:
    if name == "get_stock_price":
        return f'{{"symbol": "{input["symbol"]}", "price": 198.50, "change": "+2.3%"}}'
    elif name == "calculate":
        return str(eval(input["expression"]))

# Agent 循环
def claude_agent(task: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": task}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        # 处理工具调用
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})

    return "达到最大轮次"

answer = claude_agent("AAPL 当前股价多少？如果我持有 100 股，总价值是多少？")
```

## 4. Computer Use（计算机操作）

```python
from anthropic import Anthropic

client = Anthropic()

# Computer Use：Claude 操作桌面环境
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1920,
            "display_height_px": 1080,
            "display_number": 1,
        },
        {
            "type": "text_editor_20250124",
            "name": "str_replace_editor",
        },
        {
            "type": "bash_20250124",
            "name": "bash",
        },
    ],
    messages=[{
        "role": "user",
        "content": "打开浏览器，搜索 'AI Agent frameworks 2025'，截图第一页结果"
    }],
)

# Claude 会返回鼠标点击、键盘输入等操作指令
for block in response.content:
    if block.type == "tool_use":
        print(f"操作: {block.name} → {block.input}")
```

## 5. 多模态输入

```python
import base64

# 图片分析
with open("architecture.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": image_data},
            },
            {
                "type": "text",
                "text": "分析这个系统架构图，指出潜在的性能瓶颈",
            },
        ],
    }],
)

# PDF 文档分析
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data},
            },
            {"type": "text", "text": "总结这份文档的核心要点"},
        ],
    }],
)
```

## 6. Batch API（批量处理）

```python
from anthropic import Anthropic

client = Anthropic()

# 批量处理：适合大规模数据处理，成本降低 50%
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"task-{i}",
            "params": {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": f"分析数据点 {i}: {data}"}],
            },
        }
        for i, data in enumerate(dataset)
    ]
)

# 查询批次状态
status = client.messages.batches.retrieve(batch.id)
print(f"状态: {status.processing_status}")
print(f"完成: {status.request_counts.succeeded}/{status.request_counts.processing}")

# 获取结果
if status.processing_status == "ended":
    for result in client.messages.batches.results(batch.id):
        print(f"{result.custom_id}: {result.result.message.content[0].text}")
```

## 7. Claude Code（终端 Agent）

```bash
# Claude Code：命令行 AI Agent
# 安装
npm install -g @anthropic-ai/claude-code

# 使用
claude  # 启动交互式会话

# 常用命令
claude "重构 src/utils.py，添加类型注解和错误处理"
claude "找到并修复项目中的安全漏洞"
claude "为 UserService 类编写单元测试"

# Claude Code 能力：
# ├─ 读写文件
# ├─ 执行终端命令
# ├─ 搜索代码库
# ├─ Git 操作
# ├─ 运行测试
# └─ 多步骤推理和规划
```

## 8. API 最佳实践

```python
# Token 优化策略
def optimized_agent_call(task: str) -> str:
    """优化 Token 使用的 Agent 调用"""

    # 1. 使用 system prompt 缓存（减少重复 Token）
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": "你是 AI 助手...(长 system prompt)",
            "cache_control": {"type": "ephemeral"},  # 启用缓存
        }],
        messages=[{"role": "user", "content": task}],
    )

    # 2. 流式输出（减少等待时间）
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": task}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    return response.content[0].text

# 3. 模型选择策略
def select_model(task_complexity: str) -> str:
    """根据任务复杂度选择模型"""
    models = {
        "simple": "claude-haiku-3-5",       # 简单分类/提取
        "medium": "claude-sonnet-4-6",  # 通用任务
        "complex": "claude-opus-4-7",          # 复杂推理（2026-04-16 发布）
    }
    return models.get(task_complexity, "claude-sonnet-4-6")
```

## 9. 与其他模型对比（Agent 场景）

> 🔄 更新于 2026-04-18

| 能力           | Claude Opus 4.7  | GPT-5.4         | Gemini 3.1 Pro  |
|---------------|------------------|-----------------|-----------------|
| 工具调用       | ✅ 原生          | ✅ 原生         | ✅ 原生          |
| 扩展思考       | ✅ xhigh 层级    | ✅ o3/o4        | ✅ Thinking     |
| 计算机操作     | ✅ Computer Use  | ❌              | ❌              |
| 多模态         | ✅ 图片+PDF+3.75MP| ✅ 图片+音频   | ✅ 全模态        |
| 上下文窗口     | 1M               | 128K            | 1M              |
| 批量 API      | ✅ 50% 折扣     | ✅ 50% 折扣    | ❌              |
| 代码能力       | ★★★★★（SWE-bench Pro 64.3%）| ★★★★★ | ★★★★          |
| 指令遵循       | ★★★★★          | ★★★★           | ★★★★           |

> 来源：[devtoolpicks.com 评测](https://devtoolpicks.com/blog/claude-opus-4-7-launch-review-2026)

> 更新于 2026-07-09

### Computer Use 与 Agent SDK 分工（2026-07）

**重要区分**：Claude **Agent SDK**（`@anthropic-ai/claude-agent-sdk`）内置 Read/Write/Bash/WebSearch 等工具，但**不包含** Computer Use；桌面/浏览器自动化需用 **Anthropic Client SDK** 直接调 beta API。

| 能力 | API / 工具版本 | 适用模型 |
| ---- | ------------- | -------- |
| **Computer Use 增强版** | `computer_20251124` + beta `computer-use-2025-11-24` | Opus 4.8/4.7/4.6、Sonnet 5/4.6、Opus 4.5 |
| **Computer Use 经典版** | `computer_20250124` + beta `computer-use-2025-01-24` | Sonnet 4.5、Haiku 4.5 等 |
| **新增 zoom 动作** | `enable_zoom: true`（仅 `computer_20251124`） | 全分辨率局部放大，适合密集 UI |

**生产最佳实践**（Anthropic 2026-05 指南）：

- 图像裁剪 + 历史截图剪枝，降低 token 成本
- Prompt caching + server-side compaction 控制长会话开销
- 沙箱 shell + 轨迹录制，便于审计与复现
- Opus 4.7+ 用 **adaptive thinking**（模型自决推理深度）；4.6 族仍用 extended thinking

```python
# Computer Use 需 client.beta.messages.create，非 Agent SDK
from anthropic import Anthropic

client = Anthropic()
response = client.beta.messages.create(
    model="claude-opus-4-8",
    betas=["computer-use-2025-11-24"],
    max_tokens=4096,
    tools=[{
        "type": "computer_20251124",
        "name": "computer",
        "display_width_px": 1920,
        "display_height_px": 1080,
        "enable_zoom": True,
    }],
    messages=[{"role": "user", "content": "打开设置页面并截图"}],
)
# 应用层必须实现 screenshot/click/type 执行循环
```

> 来源：[Computer Use Tool 文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)、[Computer Use 最佳实践](https://claude.com/blog/best-practices-for-computer-and-browser-use-with-claude)、[Agent SDK Overview](https://code.claude.com/docs/en/agent-sdk/overview)、[computer-use-demo](https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo)

## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude 4 Capabilities](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude能力介绍
- [Anthropic - Extended Thinking](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude扩展思考

### 📖 官方文档
- [Anthropic Docs](https://docs.anthropic.com/) — Claude官方文档
