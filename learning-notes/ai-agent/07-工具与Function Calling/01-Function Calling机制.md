# Function Calling 机制
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 核心流程

```
用户请求 → LLM 判断是否需要工具 → 生成工具调用参数 → 执行工具 → 结果返回 LLM → 生成最终回答

┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│ User │ →  │ LLM  │ →  │ Tool │ →  │ LLM  │ → 最终回答
│      │    │判断+参数│   │ 执行  │    │ 整合  │
└──────┘    └──────┘    └──────┘    └──────┘
```

## 2. OpenAI Function Calling

```python
from openai import OpenAI
import json

client = OpenAI()

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["city"],
            },
        },
    }
]

# 第一轮：LLM 决定调用工具
response = client.chat.completions.create(
    model="gpt-5.2",  # <!-- 修复于 2026-05-13: gpt-4o 已退役 -->
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools,
    tool_choice="auto",  # auto / required / none / {"type":"function","function":{"name":"..."}}
)

message = response.choices[0].message
if message.tool_calls:
    # 执行工具
    tool_call = message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    result = get_weather(**args)  # 实际调用

    # 第二轮：将结果返回 LLM
    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=[
            {"role": "user", "content": "北京今天天气怎么样？"},
            message,
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)},
        ],
    )
    print(response.choices[0].message.content)
```

## 3. Claude Function Calling

```python
import anthropic

client = anthropic.Anthropic()

# Claude 工具定义
tools = [
    {
        "name": "query_database",
        "description": "查询数据库获取信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQL 查询语句"},
                "database": {"type": "string", "description": "数据库名称"},
            },
            "required": ["sql"],
        },
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6-20260217",  # <!-- 修复于 2026-05-13: claude-sonnet-4-20250514 过时 -->
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "查询上月销售额最高的产品"}],
)

# 处理工具调用
for block in response.content:
    if block.type == "tool_use":
        tool_input = block.input  # {"sql": "SELECT ...", "database": "sales"}
        result = execute_sql(tool_input["sql"])

        # 返回结果
        response = client.messages.create(
            model="claude-sonnet-4-6-20260217",
            max_tokens=1024,
            tools=tools,
            messages=[
                {"role": "user", "content": "查询上月销售额最高的产品"},
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(result)}
                ]},
            ],
        )
```

## 4. 并行工具调用

```python
# OpenAI 支持一次返回多个工具调用
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "北京和上海今天天气怎么样？"}],
    tools=tools,
    parallel_tool_calls=True,  # 启用并行调用
)

message = response.choices[0].message
# message.tool_calls 可能包含多个调用
# [ToolCall(function="get_weather", args={"city":"北京"}),
#  ToolCall(function="get_weather", args={"city":"上海"})]

# 并行执行所有工具调用
import asyncio

async def execute_parallel(tool_calls):
    tasks = []
    for tc in tool_calls:
        args = json.loads(tc.function.arguments)
        tasks.append(asyncio.create_task(async_get_weather(**args)))
    return await asyncio.gather(*tasks)
```

## 5. 流式工具调用

```python
# 流式响应中处理工具调用
stream = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "查询天气"}],
    tools=tools,
    stream=True,
)

tool_calls_buffer = {}
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.tool_calls:
        for tc in delta.tool_calls:
            idx = tc.index
            if idx not in tool_calls_buffer:
                tool_calls_buffer[idx] = {"name": "", "arguments": ""}
            if tc.function.name:
                tool_calls_buffer[idx]["name"] = tc.function.name
            if tc.function.arguments:
                tool_calls_buffer[idx]["arguments"] += tc.function.arguments

# 流式完成后，解析并执行工具
for idx, tc in tool_calls_buffer.items():
    args = json.loads(tc["arguments"])
    result = execute_tool(tc["name"], args)
```

## 6. 多模型对比

> 🔄 更新于 2026-04-18

<!-- version-check: OpenAI Responses API (replacing Assistants API, deadline 2026-08-26), Claude Opus 4.7, checked 2026-04-18 -->

| 特性 | OpenAI | Claude | Gemini |
|------|--------|--------|--------|
| 工具定义 | JSON Schema | input_schema | FunctionDeclaration |
| 并行调用 | ✅ | ✅ | ✅ |
| 流式调用 | ✅ | ✅ | ✅ |
| 强制调用 | tool_choice | tool_choice | tool_config |
| 嵌套对象 | 支持 | 支持 | 支持 |
| 最大工具数 | 128 | 64 | 128 |
| 工具可靠性 | 6.3/10 | 8.4/10 | 7.9/10 |

> **2026 重要变化**：
> - **OpenAI Assistants API 将于 2026-08-26 关闭**，替代方案为 [Responses API](https://platform.openai.com/docs/api-reference/responses)，需在截止日期前完成迁移
> - **Claude 工具可靠性领先**：Q1 2026 评测中，Anthropic 工具调用可靠性评分 8.4/10，content-block 架构将工具调用与文本响应清晰分离，strict mode 确保 Schema 合规（[来源](https://www.digitalapplied.com/blog/ai-function-calling-guide-openai-anthropic-google)）
> - **OpenAI Agents SDK** 引入沙箱执行和 Harness 架构，从原型工具向企业级平台转型
## 🎬 推荐视频资源

- [DeepLearning.AI - Functions, Tools and Agents with LangChain](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) — Function Calling实战（免费）
- [OpenAI - Function Calling Guide](https://www.youtube.com/watch?v=0lOSvOoF2to) — OpenAI Function Calling讲解
