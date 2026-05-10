# AI Agent 可观测性

> Author: Walter Wang

<!-- version-check: LangSmith Fleet, Langfuse 4.x, Phoenix 6.x, OTel GenAI semconv, checked 2026-05-10 -->

## 1. 为什么 LLM 系统需要独立的可观测性

传统服务观测关心："请求是不是成功，快不快。"
LLM 系统还要回答：**"回答得好不好，花了多少 Token，Prompt 模板改了之后是变好了还是变差了？"**

```
┌─────── 传统系统 vs LLM 系统 ───────┐
│                                     │
│  传统系统：                           │
│  ├─ 输入输出确定                     │
│  ├─ 失败有明确的状态码                │
│  ├─ 成本按 CPU/内存计                │
│  └─ "正确"由单元测试保证              │
│                                     │
│  LLM 系统：                          │
│  ├─ 输入输出是开放的自然语言           │
│  ├─ 失败形式多样（幻觉、偏题、乱码）   │
│  ├─ 成本按 Token 计，单次可能几美元    │
│  └─ "正确"需要人工评估或 LLM-as-Judge │
└────────────────────────────────────┘
```

## 2. 关键观测维度

```
LLM 观测三层：
├─ 单次调用
│   ├─ Prompt（完整的 system + user + tools）
│   ├─ Response（包括 function calls）
│   ├─ Token 消耗（输入 / 输出 / 缓存）
│   ├─ 模型、温度、top_p
│   └─ 耗时（首 Token / 全部完成）
│
├─ 一次 Agent 运行
│   ├─ 工具调用序列
│   ├─ 子 Agent 调用
│   ├─ 整体耗时、总成本
│   ├─ Plan → Act → Reflect 循环
│   └─ 最终结果 vs 预期
│
└─ 生产流量聚合
    ├─ 按 prompt 版本对比成功率
    ├─ 按模型对比成本
    ├─ 用户反馈关联（点赞/点踩）
    └─ 定期自动评估（eval dataset）
```

## 3. 工具生态（2026）

| 工具 | 定位 | 特点 |
|------|------|------|
| **LangSmith Fleet** | LangChain 官方 | Agent 身份、团队协作、审计追踪 |
| **Langfuse** | 开源 | 自托管首选，OTel 原生 |
| **Arize Phoenix** | 开源，专注 eval | RAG 评估、embedding 可视化最强 |
| **Weights & Biases Traces** | 实验管理 | 适合研究型、训练+推理结合 |
| **Datadog LLM Observability** | SaaS 综合 | 与业务 APM 统一 |
| **Honeycomb** | 分布式追踪 | GenAI 语义约定支持最快 |
| **OpenTelemetry + 自建** | 标准 | 不锁定厂商，灵活 |

**选型建议**：
- 个人/小团队：**Langfuse** 自托管 + OTel
- LangChain 生态：**LangSmith Fleet**
- 重 RAG / 评估：**Phoenix**
- 已用 Datadog：**Datadog LLM Observability**

## 4. OpenTelemetry GenAI 语义约定

2026 年 OTel 正式发布了 `gen_ai.*` 命名空间，标准化 LLM 的观测。

```
核心属性（Span Attributes）：

gen_ai.system              openai / anthropic / google / ...
gen_ai.request.model       gpt-5.5 / claude-opus-4-7 / gemini-3-flash
gen_ai.request.temperature 0.0 - 2.0
gen_ai.request.max_tokens  1024
gen_ai.request.top_p       0.9
gen_ai.request.top_k       40
gen_ai.request.stream      true/false

gen_ai.response.id         响应 ID
gen_ai.response.model      实际使用的模型（可能和请求不一样）
gen_ai.response.finish_reasons [stop, length, tool_calls, ...]

gen_ai.usage.input_tokens  输入 token 数
gen_ai.usage.output_tokens 输出 token 数
gen_ai.usage.total_tokens  总 token 数

gen_ai.conversation.id     会话 ID
gen_ai.operation.name      chat / completion / embeddings / tool
```

**标准 Span 结构**：

```python
from opentelemetry import trace

tracer = trace.get_tracer("my-agent")

with tracer.start_as_current_span("chat gpt-5.5") as span:
    span.set_attribute("gen_ai.system", "openai")
    span.set_attribute("gen_ai.request.model", "gpt-5.5")
    span.set_attribute("gen_ai.request.temperature", 0.7)
    span.set_attribute("gen_ai.operation.name", "chat")

    # Prompt 作为 Event（而不是 Attribute，避免属性过大）
    span.add_event("gen_ai.content.prompt", {
        "gen_ai.prompt": json.dumps(messages),
    })

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=messages,
        temperature=0.7,
    )

    span.set_attribute("gen_ai.response.id", response.id)
    span.set_attribute("gen_ai.response.model", response.model)
    span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
    span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)
    span.set_attribute("gen_ai.usage.total_tokens", response.usage.total_tokens)
    span.set_attribute("gen_ai.response.finish_reasons",
                       [c.finish_reason for c in response.choices])

    span.add_event("gen_ai.content.completion", {
        "gen_ai.completion": json.dumps([c.model_dump() for c in response.choices]),
    })
```

## 5. Langfuse 生产接入示例

Langfuse 是 2026 年最活跃的开源 LLM 观测平台：

```bash
pip install langfuse
```

```python
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

# 初始化（环境变量优先）
langfuse = Langfuse(
    public_key="pk-lf-xxx",
    secret_key="sk-lf-xxx",
    host="https://cloud.langfuse.com",  # 或自托管地址
)

@observe(as_type="generation")
def call_llm(messages, user_id: str):
    """自动生成 trace，记录 prompt/completion。"""
    response = openai.chat.completions.create(
        model="gpt-5.5",
        messages=messages,
    )

    # Langfuse 自动抓取 usage，但可以手动补充
    langfuse_context.update_current_observation(
        input=messages,
        output=response.choices[0].message.content,
        usage={
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
        },
        model="gpt-5.5",
        metadata={"user_id": user_id},
    )

    return response

@observe()
def customer_service_agent(question: str, user_id: str):
    """完整 Agent 运行作为父 trace。"""
    langfuse_context.update_current_trace(
        user_id=user_id,
        tags=["production", "cs-agent"],
    )

    # 步骤 1：检索知识库
    docs = retrieve_docs(question)

    # 步骤 2：生成回答
    messages = build_prompt(question, docs)
    response = call_llm(messages, user_id=user_id)

    return response
```

**关键能力**：
- 生产流量自动采样
- Prompt Management：Prompt 版本化，A/B 对比
- Evaluations：定期跑 eval 集合
- Datasets：收集 bad case 持续迭代
- 用户反馈关联：点赞/点踩直接挂到 Trace

## 6. Agent 运行的多层 Span

```
Trace: order_query_agent
├── Span: retrieve_context        (RAG)
│   ├── Span: embed_query         (embedding call)
│   └── Span: vector_search       (Qdrant/Pinecone)
├── Span: chat gpt-5.5            (第一次推理)
│   └── Event: gen_ai.content.prompt
├── Span: tool.get_order          (工具调用)
│   └── Span: http POST /orders/:id
├── Span: chat gpt-5.5            (第二次推理，融合工具结果)
└── Span: guardrail.check         (输出安全检查)
```

每一层都要可以独立查看和断点排查，整体也要能聚合看总 Token 和总成本。

## 7. 评估（Evaluation）

生产 LLM 系统必须有"持续评估"机制。

```
评估分两类：

离线评估（Offline Eval）
├─ 人工标注 benchmark 集
├─ 每次 prompt 改动跑一遍
├─ 分数和历史版本对比
└─ 类似 CI 中的单元测试

在线评估（Online Eval）
├─ 生产流量采样，让 LLM-as-Judge 打分
├─ 关联用户反馈（点赞、重试）
├─ 实时监控质量下降
└─ 类似 APM 中的 Golden Signals
```

LangSmith / Langfuse / Phoenix 都提供内置 evaluators：

```python
# Langfuse 评估示例
from langfuse import Langfuse

langfuse = Langfuse()

@langfuse.evaluator("relevance")
def check_relevance(trace) -> dict:
    """用另一个 LLM 判断回答是否切题。"""
    judge_prompt = f"""
    Question: {trace.input}
    Answer: {trace.output}
    Rate 0-1 whether the answer addresses the question.
    """
    # ... 调用 judge LLM
    return {"score": 0.85, "comment": "Mostly relevant"}
```

## 8. 成本监控

```python
# Prometheus 指标示例
from prometheus_client import Counter

LLM_TOKENS = Counter(
    "llm_tokens_total",
    "Total tokens consumed",
    ["model", "type", "user_tier"],  # type=input/output
)

LLM_COST_USD = Counter(
    "llm_cost_usd_total",
    "Total cost in USD",
    ["model", "user_tier"],
)

def record_usage(response, user_tier: str):
    model = response.model
    LLM_TOKENS.labels(model=model, type="input", user_tier=user_tier).inc(
        response.usage.prompt_tokens
    )
    LLM_TOKENS.labels(model=model, type="output", user_tier=user_tier).inc(
        response.usage.completion_tokens
    )
    # 按定价计算成本
    cost = calculate_cost(model, response.usage)
    LLM_COST_USD.labels(model=model, user_tier=user_tier).inc(cost)
```

**注意**：`user_tier`、`model` 是有限枚举，不会爆标签。不要直接用 `user_id`。

## 9. 常见问题

```
问题："Prompt 改了之后效果下降了 5%，怎么定位？"
工具：Langfuse Dataset + Evaluator + 历史对比

问题："一个用户一天花了 $50，怎么发现的？"
方案：Prometheus LLM_COST_USD by user_id + 告警阈值（但 user_id 基数高，要在应用层做）

问题："Agent 有时进入死循环怎么检测？"
方案：
  ├─ 单 Trace 步骤数 > 20 → 告警
  ├─ 单 Trace 耗时 > 5 分钟 → 告警
  └─ 相同工具调用次数 > 5 → 代码层熔断

问题："RAG 有时检索不到相关文档怎么发现？"
方案：Phoenix 的 retrieval evaluation，自动跑 "precision@k"、"recall@k"

问题："如何对比 GPT-5.5 和 Claude Opus 4.7 在我场景下的表现？"
方案：
  ├─ 生产流量同时路由到两个模型（A/B）
  ├─ 用户反馈关联到 Trace
  └─ Langfuse 按 model 维度聚合指标
```

## 10. 生产检查清单

```
☐ OTel GenAI 语义约定统一使用
☐ Prompt 版本化（Git + Langfuse）
☐ 用户反馈通道（点赞/点踩）接入 Trace
☐ Token 和成本按 user_tier/model 聚合
☐ 离线评估集持续维护（每次 prompt 改动必跑）
☐ 在线 LLM-as-Judge 采样评估（10-20%）
☐ 单 Agent 运行步数上限 + 熔断
☐ 敏感数据脱敏（PII、业务数据）
☐ 模型切换开关（Feature Flag）
☐ 关联用户 ID 但不作为高基数标签
```

## 📖 参考资料

- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Langfuse 文档](https://langfuse.com/docs)
- [LangSmith Fleet](https://docs.langchain.com/langsmith/)
- [Arize Phoenix](https://phoenix.arize.com/)
- [LLM Observability Guide (Martin Fowler)](https://martinfowler.com/articles/llm-observability.html)
- 关联：[ai-agent/14-可观测与评估/](../ai-agent/14-可观测与评估/)
