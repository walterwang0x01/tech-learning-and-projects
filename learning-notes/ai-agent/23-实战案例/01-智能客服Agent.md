# 智能客服 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   智能客服系统                         │
├──────────┬──────────┬──────────┬───────────────────┤
│ 接入层    │ Agent 层  │ 工具层    │ 数据层            │
├──────────┼──────────┼──────────┼───────────────────┤
│ Web/App  │ 分诊Agent │ 知识库检索│ 向量数据库         │
│ 微信/钉钉│ 客服Agent │ 订单查询  │ 业务数据库         │
│ API      │ 工单Agent │ 工单创建  │ 工单系统           │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ 人工坐席（Human-in-the-Loop）↕
```

## 2. 分诊 Agent

```python
from agents import Agent, handoff, Runner

# 子 Agent 需先定义，triage_agent 的 handoffs 引用的是 Agent 对象（非字符串）
product_agent = Agent(
    name="product_agent",
    instructions="你是产品咨询专家。基于知识库回答产品相关问题。",
    tools=[search_knowledge_base],
)

order_agent = Agent(
    name="order_agent",
    instructions="你是订单处理专家。帮助用户查询订单、处理退换货。",
    tools=[query_order, create_return_request],
)

complaint_agent = Agent(
    name="complaint_agent",
    instructions="你是投诉处理专家。安抚用户情绪，记录投诉并创建工单。",
    tools=[create_ticket, escalate_to_human],
)

# 分诊 Agent：根据问题类型路由
# 修复于 2026-05-31: OpenAI Agents SDK 的 handoffs 接受 Agent 对象列表，非字符串
triage_agent = Agent(
    name="triage",
    instructions="""你是智能客服分诊员。根据用户问题分类并转交：
    - 产品咨询 → product_agent
    - 订单问题 → order_agent
    - 投诉建议 → complaint_agent
    - 无法处理 → 转人工""",
    handoffs=[product_agent, order_agent, complaint_agent],
)
```

## 3. 知识库检索工具

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-service-tools")

@mcp.tool()
async def search_knowledge_base(query: str, category: str = "all") -> str:
    """搜索客服知识库"""
    results = await vectorstore.similarity_search(
        query, k=3, filter={"category": category} if category != "all" else None,
    )
    return "\n\n".join(f"[{i+1}] {doc.page_content}" for i, doc in enumerate(results))

@mcp.tool()
def query_order(order_id: str) -> dict:
    """查询订单详情"""
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        return {"error": "订单不存在"}
    return {
        "order_id": order["id"],
        "status": order["status"],
        "items": order["items"],
        "created_at": order["created_at"],
    }

@mcp.tool()
def create_ticket(title: str, description: str, priority: str = "medium") -> dict:
    """创建客服工单"""
    ticket_id = db.execute(
        "INSERT INTO tickets (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority),
    ).lastrowid
    return {"ticket_id": ticket_id, "message": f"工单 #{ticket_id} 已创建"}
```

## 4. 多轮对话管理

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import TypedDict, Annotated
from operator import add

class CustomerServiceState(TypedDict):
    messages: Annotated[list, add]
    customer_id: str
    intent: str
    satisfaction: float

def detect_intent(state: CustomerServiceState) -> dict:
    """意图识别"""
    last_msg = state["messages"][-1]["content"]
    intent = llm.invoke(
        f"识别用户意图（product/order/complaint/chat）：{last_msg}"
    ).content.strip()
    return {"intent": intent}

def route_by_intent(state: CustomerServiceState) -> str:
    intent = state["intent"]
    routes = {"product": "product_qa", "order": "order_service", "complaint": "complaint_handler"}
    return routes.get(intent, "general_chat")

def check_satisfaction(state: CustomerServiceState) -> str:
    """检查用户满意度，决定是否转人工"""
    last_msg = state["messages"][-1]["content"]
    negative_signals = ["不满意", "投诉", "找人工", "经理"]
    if any(signal in last_msg for signal in negative_signals):
        return "human_handoff"
    return "continue"

graph = StateGraph(CustomerServiceState)
graph.add_node("detect_intent", detect_intent)
graph.add_node("product_qa", product_qa_node)
graph.add_node("order_service", order_service_node)
graph.add_node("complaint_handler", complaint_node)
graph.add_node("human_handoff", human_handoff_node)

graph.add_edge(START, "detect_intent")
graph.add_conditional_edges("detect_intent", route_by_intent)

app = graph.compile(checkpointer=PostgresSaver.from_conn_string("postgresql://..."))
```

## 5. 人工转接

```python
from langgraph.types import interrupt

def human_handoff_node(state: CustomerServiceState) -> dict:
    """转接人工坐席"""
    # 生成对话摘要
    summary = llm.invoke(
        f"请用 3 句话摘要以下客服对话的关键信息：\n{state['messages']}"
    ).content

    # 中断等待人工接入
    human_response = interrupt({
        "type": "human_handoff",
        "customer_id": state["customer_id"],
        "summary": summary,
        "message": "用户请求转接人工，请人工坐席接入",
    })

    return {"messages": [{"role": "assistant", "content": human_response}]}
```

## 6. 满意度评估

```python
class SatisfactionEvaluator:
    """客服满意度评估"""

    def __init__(self, llm):
        self.llm = llm

    async def evaluate(self, conversation: list[dict]) -> dict:
        prompt = f"""分析以下客服对话，评估用户满意度。

对话记录：
{self._format(conversation)}

请输出 JSON：
{{"score": 0.0-1.0, "resolved": true/false, "sentiment": "positive/neutral/negative", "improvement": "改进建议"}}"""

        result = (await self.llm.ainvoke(prompt)).content
        return eval(result)

    def _format(self, messages: list[dict]) -> str:
        return "\n".join(f"{m['role']}: {m['content']}" for m in messages)

evaluator = SatisfactionEvaluator(llm)
score = await evaluator.evaluate(conversation_messages)
# {"score": 0.85, "resolved": True, "sentiment": "positive", "improvement": "可以更主动提供相关信息"}
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Building Systems with ChatGPT API](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/) — 构建客服系统（免费）
- [LangChain - Customer Support Bot](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 客服Bot实战

### 📺 B站
- [AI智能客服实战项目](https://www.bilibili.com/video/BV1PD421E7mN) — 智能客服中文实战

> 🔄 更新于 2026-05-02

<!-- version-check: AI Customer Service Agent 2026, MCP+A2A, checked 2026-05-02 -->

## 7. 2026 年智能客服 Agent 趋势

### 7.1 行业数据

- **Gartner 预测**：到 2028 年，至少 70% 的客户将使用对话式 AI 界面开始客户旅程
- **Salesforce 数据**：AI Agent 预计将降低约 20% 的服务费用和案例解决时间
- **Forrester 预测**：2026 年 1/4 品牌将实现简单自助服务交互成功率提升 10%
- **G2 报告**：所有受访企业在 2026 年已进入 AI 客服规模化或全面运营阶段

### 7.2 架构演进：MCP + A2A 双协议栈

```
2024 年架构：
  用户 → 单一 Agent → 工具调用（自定义 API）

2026 年架构：
  用户 → 路由 Agent → MCP（工具层）+ A2A（Agent 间协作）
                         │                    │
                    知识库检索              跨厂商 Agent 协作
                    订单系统               计费 Agent（不同供应商）
                    工单系统               物流 Agent（第三方）
```

**关键变化：**
- **MCP 标准化工具接入**：知识库、订单系统、工单系统通过 MCP Server 暴露，Agent 框架无关
- **A2A 跨组织协作**：客服 Agent 可以将任务委托给其他厂商的专业 Agent（如计费、物流）
- **Voice AI 替代传统 IVR**：语音 Agent 直接处理电话客服，不再需要按键菜单

### 7.3 五大趋势

1. **从 Copilot 到 Autonomy**：AI 从辅助人工坐席演进为自主处理完整对话，人工只处理复杂升级
2. **Voice AI 成为核心**：对话式语音 AI 替代传统 IVR，Zowie Hello 等产品可在 2 分钟内完成航班改签
3. **实时 Agent 辅助**：AI 实时分析对话，为人工坐席提供建议回复、知识库推荐、情绪分析
4. **预测性服务**：基于用户行为数据主动触发服务（如检测到异常订单主动联系用户）
5. **多模态交互**：支持文本、语音、图片、视频等多种输入，Agent 可理解截图中的错误信息
