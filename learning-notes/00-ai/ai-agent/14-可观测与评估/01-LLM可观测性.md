# LLM 可观测性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 🔄 更新于 2026-07-08
>
> **LangSmith SDK v0.9.7**（2026-07-02）：Google ADK Live 语音追踪 + 成本归因；**LangFuse v3.206.0**（2026-07-07）：Experiments Public API / MCP 支持 CI 门禁；**Phoenix Eval CI**（2026-07-07）：`@pytest.mark.phoenix` 将评估写入版本化 Experiment。
>
> 来源：[LangSmith SDK v0.9.7](https://github.com/langchain-ai/langsmith-sdk/releases/tag/v0.9.7) · [LangFuse Experiments API](https://langfuse.com/changelog/2026-07-07-experiments-public-api-and-mcp) · [Phoenix Eval CI Blog](https://arize.com/blog/evals-in-ci-how-to-write-llm-evals-as-tests/)

<!-- version-check: LangSmith SDK v0.9.7, LangFuse v3.206.0, Phoenix eval CI, checked 2026-07-08 -->
<!-- version-check: LangSmith, LangFuse v4, Phoenix, checked 2026-05-13 -->

## 1. 可观测性概览

```
┌─────────────────────────────────────────┐
│           LLM 可观测性                    │
├──────────┬──────────┬──────────────────┤
│  Tracing  │ Metrics  │  Logging         │
│  链路追踪  │ 指标监控  │  日志记录        │
├──────────┼──────────┼──────────────────┤
│ Trace/Span│ Token 用量│ 输入/输出日志     │
│ 调用链路  │ 延迟 P99  │ 错误日志         │
│ 工具调用  │ 成本统计  │ 审计日志         │
└──────────┴──────────┴──────────────────┘
```

## 2. LangSmith 集成

> **2026-07 增量**：SDK v0.9.7 新增 Google ADK Live 语音 trace；JS `wrapAnthropic` 支持 Claude Managed Agents。Engine 技术架构见 [How We Built LangSmith Engine](https://www.langchain.com/blog/how-we-built-langsmith-engine-our-agent-for-improving-agents)。

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls_xxx"
os.environ["LANGCHAIN_PROJECT"] = "my-agent"

# LangChain 自动追踪所有调用
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.2")  <!-- 修复于 2026-05-13: gpt-4o 已从 ChatGPT 退役 -->
prompt = ChatPromptTemplate.from_template("解释 {topic}")
chain = prompt | llm

# 每次调用自动记录到 LangSmith
result = chain.invoke({"topic": "RAG 架构"})
# LangSmith 控制台可查看：输入、输出、Token、延迟、成本
```

## 3. LangFuse 自托管追踪

> **2026-07 增量**：Experiments Public API（`GET /api/public/experiments`）+ MCP `listExperiments` 工具，支持 CI/CD 拉取分数做回归门禁。详见 [Changelog](https://langfuse.com/changelog/2026-07-07-experiments-public-api-and-mcp)。

```python
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

langfuse = Langfuse(
    public_key="pk-xxx",
    secret_key="sk-xxx",
    host="http://localhost:3000",  # 自托管地址
)

@observe()  # 自动追踪函数调用
def rag_pipeline(question: str) -> str:
    # 检索
    docs = retrieve_documents(question)

    # 生成
    langfuse_context.update_current_observation(
        metadata={"retrieved_docs": len(docs)}
    )
    answer = generate_answer(question, docs)
    return answer

@observe(as_type="generation")
def generate_answer(question: str, docs: list) -> str:
    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=[{"role": "user", "content": f"上下文：{docs}\n问题：{question}"}],
    )
    # 自动记录 token 用量和成本
    langfuse_context.update_current_observation(
        usage={"input": response.usage.prompt_tokens, "output": response.usage.completion_tokens},
        model="gpt-5.2",
    )
    return response.choices[0].message.content

result = rag_pipeline("什么是 MCP？")
langfuse.flush()
```

## 4. Phoenix（Arize）实时监控

> **2026-07 增量**：可用 `@pytest.mark.phoenix` 将 LLM 评估写成普通 pytest 测试，每次运行自动记录为 Phoenix Experiment（`arize-phoenix-client` 2.10.0+）。Vitest/Jest 支持见 `@arizeai/phoenix-client` 6.11.1+（beta）。指南：[Eval CI with pytest](https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments/eval-ci-with-pytest)。

```python
import phoenix as px
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor

# 启动 Phoenix 本地服务
px.launch_app()

# 注册 OpenTelemetry 追踪
tracer_provider = register(project_name="my-agent")
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

# 之后所有 OpenAI 调用自动追踪
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "你好"}],
)
# 打开 http://localhost:6006 查看追踪数据
```

## 5. Trace/Span 链路追踪

```python
from langfuse import Langfuse

langfuse = Langfuse()

# 手动创建 Trace
trace = langfuse.trace(name="customer-service", user_id="user-123")

# Span: 检索步骤
retrieval_span = trace.span(name="retrieval", input={"query": "退货政策"})
docs = retriever.invoke("退货政策")
retrieval_span.end(output={"doc_count": len(docs)})

# Generation: LLM 调用
generation = trace.generation(
    name="answer-generation",
    model="gpt-5.2",
    input=[{"role": "user", "content": "退货政策是什么？"}],
)
response = llm.invoke(...)
generation.end(
    output=response.content,
    usage={"input": 150, "output": 200},
    metadata={"temperature": 0.7},
)

# Score: 评分
trace.score(name="user_satisfaction", value=0.9, comment="回答准确")
```

## 6. 成本与延迟监控

```python
import time
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class LLMMetrics:
    """LLM 调用指标收集器"""
    latencies: list[float] = field(default_factory=list)
    token_usage: dict = field(default_factory=lambda: defaultdict(int))
    costs: list[float] = field(default_factory=list)
    errors: int = 0

    def record_call(self, model: str, latency: float, input_tokens: int, output_tokens: int):
        self.latencies.append(latency)
        self.token_usage[f"{model}_input"] += input_tokens
        self.token_usage[f"{model}_output"] += output_tokens

    def summary(self) -> dict:
        return {
            "total_calls": len(self.latencies),
            "avg_latency_ms": sum(self.latencies) / len(self.latencies) * 1000 if self.latencies else 0,
            "p99_latency_ms": sorted(self.latencies)[int(len(self.latencies) * 0.99)] * 1000 if self.latencies else 0,
            "total_tokens": sum(self.token_usage.values()),
            "error_rate": self.errors / max(len(self.latencies), 1),
        }

metrics = LLMMetrics()

# 包装 LLM 调用
def tracked_completion(model: str, messages: list) -> str:
    start = time.time()
    response = client.chat.completions.create(model=model, messages=messages)
    latency = time.time() - start
    metrics.record_call(model, latency, response.usage.prompt_tokens, response.usage.completion_tokens)
    return response.choices[0].message.content
```
## 🎬 推荐视频资源

- [DeepLearning.AI - Evaluating and Debugging Generative AI](https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/) — LLM评估与调试（免费）
- [LangSmith - Getting Started](https://www.youtube.com/watch?v=tFXm5ijih98) — LangSmith可观测性平台入门
- [Phoenix Eval CI Blog](https://arize.com/blog/evals-in-ci-how-to-write-llm-evals-as-tests/) — 用 pytest/Vitest 写评估门禁（2026-07）
