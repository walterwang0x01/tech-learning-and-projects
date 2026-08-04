# Dapr Agents 分布式运行时
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

<!-- version-check: Dapr Agents v1.0.5 (2026-06-15), checked 2026-07-10 -->

> 🔄 更新于 2026-04-18

Dapr Agents 基于 Dapr 的 Sidecar 架构，为 AI Agent 提供分布式运行时能力：Agent 间通信、状态管理、工作流编排、弹性伸缩。

**v1.0 GA 里程碑**（2026-03-23，KubeCon Europe Amsterdam）：
- **CNCF 托管**：由 Cloud Native Computing Foundation 正式发布 GA 版本
- **生产就绪**：持久化工作流、状态管理、安全多 Agent 协调
- **NVIDIA 合作**：与 NVIDIA 和 Dapr 开源社区联合开发
- **企业级特性**：内置可观测性、遥测、安全性

> 来源：[CNCF 公告](https://cloudnativenow.com/kubecon-cloudnativecon-europe-2026/cncf-announces-general-availability-of-dapr-agents-v1-0-for-production-ai-workloads/)、[Forbes 报道](https://www.forbes.com/sites/janakirammsv/2026/03/28/cncfs-dapr-agents-tackles-the-problem-most-ai-frameworks-ignore/)

```
┌─────────────────────────────────────────────────┐
│              Dapr Agents 架构                     │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │       │
│  │ (研究员) │  │ (写作者) │  │ (审查者) │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐       │
│  │Dapr      │  │Dapr      │  │Dapr      │       │
│  │Sidecar   │  │Sidecar   │  │Sidecar   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       └──────────────┼──────────────┘              │
│                      ↓                             │
│  ┌─────────────────────────────────────────────┐  │
│  │  Dapr 基础设施                                │  │
│  │  Pub/Sub │ State Store │ Workflow │ Bindings │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

核心价值：将 Agent 作为微服务运行，利用 Dapr 的分布式能力实现生产级部署。

## 2. 快速开始

```bash
pip install dapr-agents
```

```python
from dapr_agents import Agent, tool
from dapr_agents.llm import OpenAIChatClient

# 创建 LLM 客户端
llm = OpenAIChatClient(model="gpt-4o")

# 定义工具
@tool
def search_web(query: str) -> str:
    """搜索互联网获取信息"""
    return f"搜索结果: {query} 的相关信息..."

@tool
def calculate(expression: str) -> str:
    """执行数学计算"""
    return str(eval(expression))

# 创建 Agent
agent = Agent(
    name="research-assistant",
    role="研究助手",
    instructions="你是研究助手，使用工具搜索信息并回答问题。",
    llm=llm,
    tools=[search_web, calculate],
)

# 运行
result = agent.run("2025年全球AI市场规模是多少？计算同比增长率。")
print(result)
```

## 3. Agent 间通信（Pub/Sub）

```python
from dapr_agents import Agent, AgentService
from dapr_agents.llm import OpenAIChatClient

llm = OpenAIChatClient(model="gpt-4o")

# Agent A：研究员
researcher = Agent(
    name="researcher",
    role="研究员",
    instructions="调研给定主题，输出调研报告。",
    llm=llm,
    tools=[search_web],
)

# Agent B：写作者
writer = Agent(
    name="writer",
    role="技术作者",
    instructions="基于调研材料撰写文章。",
    llm=llm,
)

# 通过 Dapr Pub/Sub 通信
# Agent 发布消息到主题
researcher_service = AgentService(
    agent=researcher,
    message_bus_name="pubsub",       # Dapr Pub/Sub 组件
    agents_registry_store_name="statestore",  # 状态存储
)

writer_service = AgentService(
    agent=writer,
    message_bus_name="pubsub",
    agents_registry_store_name="statestore",
)

# 启动服务（每个 Agent 作为独立微服务）
# researcher_service.start()
# writer_service.start()
```

## 4. 状态管理

```python
from dapr_agents import Agent
from dapr.clients import DaprClient

class StatefulAgent:
    """有状态的 Agent，使用 Dapr State Store"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.dapr = DaprClient()

    def save_state(self, key: str, value: dict):
        """保存 Agent 状态"""
        self.dapr.save_state(
            store_name="statestore",
            key=f"{self.agent_id}-{key}",
            value=str(value),
        )

    def get_state(self, key: str) -> dict:
        """获取 Agent 状态"""
        state = self.dapr.get_state(
            store_name="statestore",
            key=f"{self.agent_id}-{key}",
        )
        return eval(state.data) if state.data else {}

    def save_memory(self, conversation: list):
        """保存对话记忆"""
        self.save_state("memory", {"conversations": conversation})

    def load_memory(self) -> list:
        """加载对话记忆"""
        state = self.get_state("memory")
        return state.get("conversations", [])
```

## 5. 工作流编排

```python
from dapr_agents.workflow import WorkflowApp, DaprWorkflowContext, WorkflowActivityContext

# 定义工作流活动（步骤）
def research_activity(ctx: WorkflowActivityContext, topic: str) -> str:
    """研究活动"""
    agent = Agent(name="researcher", role="研究员", llm=llm, tools=[search_web])
    return agent.run(f"调研：{topic}")

def write_activity(ctx: WorkflowActivityContext, research: str) -> str:
    """写作活动"""
    agent = Agent(name="writer", role="作者", llm=llm)
    return agent.run(f"基于以下材料写文章：{research}")

def review_activity(ctx: WorkflowActivityContext, article: str) -> dict:
    """审查活动"""
    agent = Agent(name="reviewer", role="审查者", llm=llm)
    review = agent.run(f"审查文章质量，回答PASS/FAIL：{article}")
    return {"passed": "PASS" in review, "feedback": review}

# 定义工作流
def content_workflow(ctx: DaprWorkflowContext, topic: str):
    """内容创作工作流"""
    # 步骤1：研究
    research = yield ctx.call_activity(research_activity, input=topic)

    # 步骤2：写作
    article = yield ctx.call_activity(write_activity, input=research)

    # 步骤3：审查（循环直到通过）
    for _ in range(3):
        review = yield ctx.call_activity(review_activity, input=article)
        if review["passed"]:
            return article
        # 重写
        article = yield ctx.call_activity(
            write_activity, input=f"{research}\n改进建议：{review['feedback']}"
        )

    return article

# 注册并启动工作流
wf_app = WorkflowApp()
wf_app.register_workflow(content_workflow)
wf_app.register_activity(research_activity)
wf_app.register_activity(write_activity)
wf_app.register_activity(review_activity)
wf_app.start()
```

## 6. 弹性与容错

```yaml
# Dapr 弹性策略配置
# resiliency.yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: agent-resiliency
spec:
  policies:
    retries:
      llm-retry:
        policy: constant
        duration: 5s
        maxRetries: 3
    timeouts:
      agent-timeout: 60s
    circuitBreakers:
      llm-breaker:
        maxRequests: 1
        interval: 10s
        timeout: 30s
        trip: consecutiveFailures >= 3

  targets:
    components:
      pubsub:
        outbound:
          retry: llm-retry
          timeout: agent-timeout
```

## 7. Kubernetes 部署

```yaml
# agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-agent
spec:
  replicas: 3  # 多副本弹性伸缩
  selector:
    matchLabels:
      app: research-agent
  template:
    metadata:
      labels:
        app: research-agent
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "research-agent"
        dapr.io/app-port: "8080"
    spec:
      containers:
        - name: agent
          image: my-registry/research-agent:latest
          ports:
            - containerPort: 8080
          env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ai-secrets
                  key: openai-key
```

## 8. 与现有微服务集成

```python
from dapr.clients import DaprClient

class AgentMicroserviceIntegration:
    """Agent 与现有微服务集成"""

    def __init__(self):
        self.dapr = DaprClient()

    async def call_existing_service(self, app_id: str, method: str, data: dict):
        """调用现有微服务"""
        response = self.dapr.invoke_method(
            app_id=app_id,       # 目标服务 ID
            method_name=method,  # API 方法
            data=str(data),
        )
        return response.data

    async def agent_with_services(self, query: str):
        """Agent 调用现有微服务获取数据"""
        # 调用用户服务
        user_data = await self.call_existing_service(
            "user-service", "get-profile", {"user_id": "123"}
        )
        # 调用订单服务
        orders = await self.call_existing_service(
            "order-service", "list-orders", {"user_id": "123"}
        )
        # Agent 综合分析
        agent = Agent(name="analyst", role="分析师", llm=llm)
        return agent.run(f"分析用户数据：{user_data}\n订单：{orders}\n问题：{query}")
```

## 9. 适用场景

> 🔄 更新于 2026-04-18

```
Dapr Agents v1.0 GA 最适合：
├─ 已有 Dapr/微服务架构的团队
├─ 需要 Agent 与现有服务集成
├─ 需要分布式部署和弹性伸缩
├─ 多语言 Agent 协作（Python + Go + Java）
├─ 企业级生产环境（CNCF 托管，生产就绪）
└─ 需要持久化工作流保证任务完成

不太适合：
├─ 简单的单 Agent 应用
├─ 快速原型开发
└─ 无 Kubernetes 环境
```

## 9.5 GA 后的版本演进（2026-07 更新）

> 更新于 2026-07-10

<!-- version-check: Dapr Agents v1.0.5 (2026-06-15), checked 2026-07-10 -->

v1.0 GA（2026-03-23）之后，项目保持稳定的补丁节奏，**当前最新版本为 v1.0.5**（2026-06-15），语言支持仍是 **Python only**（官方路线图显示"Other Languages"为 TBD，多语言支持尚未有明确排期，本文档中"多语言 Agent 协作（Python + Go + Java）"更多是通过 Dapr 底层 Sidecar 实现跨语言微服务集成，而非 Dapr Agents SDK 本身的多语言 API）。

GA 后几个 minor 补丁中的重点变化：

- **`agents as tools`**：一个 Agent 可以把另一个 Agent 包装成 Tool 调用，简化多 Agent 编排的组合方式
- **`ToolExecutionMode`**：工具执行支持并行 / 串行两种模式显式配置
- **`agent.workflow` start 方法**：简化以 workflow 方式启动 Agent 的 API
- **MCP 支持增强**：`MCPServer` 通过 Dapr metadata API 自动发现 + workflow 编排集成
- **HITL（Human-in-the-loop）审批**：状态存储层修复了审批流程的状态一致性问题

来源：[dapr/dapr-agents GitHub Releases](https://github.com/dapr/dapr-agents/releases)、[Dapr Agents 官方文档](https://docs.dapr.io/developing-ai/dapr-agents/dapr-agents-introduction/)

## 🎬 推荐视频资源

### 🌐 YouTube
- [Microsoft - Dapr Overview](https://www.youtube.com/watch?v=pHksBVqH7uI) — Dapr概述
- [Dapr - Getting Started](https://www.youtube.com/watch?v=vU2S6dVf79M) — Dapr入门教程

### 📖 官方文档
- [Dapr Docs](https://docs.dapr.io/) — Dapr官方文档
- [Dapr Agents GitHub](https://github.com/dapr/dapr-agents) — Dapr Agents项目
