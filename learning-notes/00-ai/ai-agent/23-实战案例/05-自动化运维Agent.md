# 自动化运维 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                 DevOps/SRE Agent                     │
├──────────┬──────────┬──────────┬───────────────────┤
│ 监控分析  │ 告警响应  │ 故障诊断  │ 自动修复          │
├──────────┼──────────┼──────────┼───────────────────┤
│Prometheus│PagerDuty │日志分析   │K8s 操作           │
│Grafana   │Slack通知  │链路追踪   │服务重启           │
│CloudWatch│事件分类   │根因定位   │扩缩容             │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ Human-in-the-Loop（关键操作审批）↕
```

## 2. 工具定义

```python
from langchain_core.tools import tool
import subprocess
import json

@tool
def query_prometheus(query: str, duration: str = "1h") -> str:
    """查询 Prometheus 指标"""
    import requests
    resp = requests.get("http://prometheus:9090/api/v1/query", params={
        "query": query, "time": "", "timeout": "30s",
    })
    data = resp.json()
    if data["status"] == "success":
        results = data["data"]["result"]
        return json.dumps([{
            "metric": r["metric"],
            "value": r["value"][1],
        } for r in results[:10]], indent=2)
    return f"查询失败: {data.get('error', 'unknown')}"

@tool
def kubectl_command(command: str) -> str:
    """执行 kubectl 命令（只读操作）"""
    allowed_verbs = ["get", "describe", "logs", "top"]
    verb = command.split()[0] if command else ""
    if verb not in allowed_verbs:
        return f"安全限制：只允许 {allowed_verbs} 操作"
    result = subprocess.run(
        f"kubectl {command}".split(),
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout or result.stderr

@tool
def search_logs(service: str, keyword: str, minutes: int = 30) -> str:
    """搜索服务日志"""
    result = subprocess.run(
        ["kubectl", "logs", f"deployment/{service}", "--since", f"{minutes}m",
         "--tail", "100"],
        capture_output=True, text=True, timeout=30,
    )
    lines = result.stdout.split("\n")
    matched = [l for l in lines if keyword.lower() in l.lower()]
    return "\n".join(matched[:20]) or "未找到匹配日志"

@tool
def send_slack_alert(channel: str, message: str) -> str:
    """发送 Slack 告警通知"""
    import requests
    requests.post("https://slack.com/api/chat.postMessage", json={
        "channel": channel, "text": f"🤖 SRE Agent: {message}",
    }, headers={"Authorization": f"Bearer {SLACK_TOKEN}"})
    return f"已发送到 {channel}"
```

## 3. 危险操作工具（需审批）

```python
from langgraph.types import interrupt

@tool
def scale_deployment(deployment: str, replicas: int) -> str:
    """扩缩容部署（需要人工审批）"""
    # 通过 interrupt 实现人工审批
    approval = interrupt({
        "action": "scale",
        "deployment": deployment,
        "replicas": replicas,
        "message": f"是否将 {deployment} 扩缩容到 {replicas} 副本？",
    })
    if approval != "approved":
        return "操作已取消"
    result = subprocess.run(
        ["kubectl", "scale", f"deployment/{deployment}", f"--replicas={replicas}"],
        capture_output=True, text=True,
    )
    return result.stdout or result.stderr

@tool
def restart_deployment(deployment: str) -> str:
    """重启部署（需要人工审批）"""
    approval = interrupt({
        "action": "restart",
        "deployment": deployment,
        "message": f"是否重启 {deployment}？",
    })
    if approval != "approved":
        return "操作已取消"
    result = subprocess.run(
        ["kubectl", "rollout", "restart", f"deployment/{deployment}"],
        capture_output=True, text=True,
    )
    return result.stdout or result.stderr
```

## 4. 多 Agent 运维系统

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from operator import add

class IncidentState(TypedDict):
    alert: dict
    messages: Annotated[list, add]
    diagnosis: str
    severity: str
    actions_taken: list[str]
    resolved: bool

llm = ChatOpenAI(model="gpt-5.2")

# Agent 1：告警分类
async def triage_agent(state: IncidentState) -> dict:
    alert = state["alert"]
    response = await llm.ainvoke(f"""分析告警并分类严重程度：
告警：{json.dumps(alert, ensure_ascii=False)}

输出 JSON：{{"severity": "P0/P1/P2/P3", "category": "类别", "summary": "摘要"}}""")
    import json as j
    result = j.loads(response.content)
    return {"severity": result["severity"], "messages": [("triage", response.content)]}

# Agent 2：诊断
async def diagnosis_agent(state: IncidentState) -> dict:
    agent = create_react_agent(llm, tools=[
        query_prometheus, kubectl_command, search_logs,
    ])
    result = await agent.ainvoke({
        "messages": [("user", f"""诊断以下告警的根因：
告警：{json.dumps(state['alert'])}
严重程度：{state['severity']}

步骤：
1. 查询相关 Prometheus 指标
2. 检查 Pod 状态
3. 搜索错误日志
4. 给出根因分析""")]
    })
    return {"diagnosis": result["messages"][-1].content}

# Agent 3：修复
async def remediation_agent(state: IncidentState) -> dict:
    agent = create_react_agent(llm, tools=[
        scale_deployment, restart_deployment, send_slack_alert,
    ])
    result = await agent.ainvoke({
        "messages": [("user", f"""基于诊断结果执行修复：
诊断：{state['diagnosis']}
严重程度：{state['severity']}

如果是 P0/P1，先通知 Slack #incidents 频道。
根据诊断选择合适的修复操作。""")]
    })
    return {
        "actions_taken": [result["messages"][-1].content],
        "resolved": True,
    }

# 路由：根据严重程度决定流程
def severity_router(state: IncidentState) -> str:
    if state["severity"] in ["P0", "P1"]:
        return "diagnosis"  # 严重告警：诊断 → 修复
    return "auto_resolve"   # 低优先级：自动处理

# 构建工作流
graph = StateGraph(IncidentState)
graph.add_node("triage", triage_agent)
graph.add_node("diagnosis", diagnosis_agent)
graph.add_node("remediation", remediation_agent)
graph.add_node("auto_resolve", lambda s: {"resolved": True, "actions_taken": ["自动处理"]})

graph.add_edge(START, "triage")
graph.add_conditional_edges("triage", severity_router)
graph.add_edge("diagnosis", "remediation")
graph.add_edge("remediation", END)
graph.add_edge("auto_resolve", END)

from langgraph.checkpoint.memory import MemorySaver
incident_agent = graph.compile(checkpointer=MemorySaver())
```

## 5. Runbook 自动化

```python
# 预定义 Runbook（标准操作手册）
RUNBOOKS = {
    "high_cpu": {
        "name": "CPU 使用率过高",
        "steps": [
            "查询 CPU 使用率趋势：rate(container_cpu_usage_seconds_total[5m])",
            "检查 Pod 资源限制：kubectl describe pod",
            "查看进程级 CPU：kubectl top pods",
            "如果单 Pod 过高，考虑重启",
            "如果整体过高，考虑扩容",
        ],
    },
    "oom_killed": {
        "name": "OOM Killed",
        "steps": [
            "查看 OOM 事件：kubectl get events --field-selector reason=OOMKilled",
            "检查内存使用：container_memory_usage_bytes",
            "查看内存限制配置",
            "增加内存限制或优化内存使用",
        ],
    },
    "pod_crash_loop": {
        "name": "Pod CrashLoopBackOff",
        "steps": [
            "查看 Pod 状态：kubectl get pods",
            "查看崩溃日志：kubectl logs --previous",
            "检查健康检查配置",
            "检查依赖服务状态",
        ],
    },
}

@tool
def get_runbook(issue_type: str) -> str:
    """获取标准操作手册"""
    runbook = RUNBOOKS.get(issue_type)
    if not runbook:
        return f"未找到 {issue_type} 的 Runbook。可用：{list(RUNBOOKS.keys())}"
    steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(runbook["steps"]))
    return f"Runbook: {runbook['name']}\n{steps}"
```

## 6. 运行示例

```python
import asyncio

async def handle_incident():
    alert = {
        "name": "HighCPUUsage",
        "service": "api-server",
        "namespace": "production",
        "value": "95%",
        "threshold": "80%",
        "duration": "10m",
    }

    config = {"configurable": {"thread_id": f"incident-{alert['name']}-001"}}
    result = await incident_agent.ainvoke({
        "alert": alert,
        "messages": [],
        "diagnosis": "",
        "severity": "",
        "actions_taken": [],
        "resolved": False,
    }, config)

    print(f"严重程度: {result['severity']}")
    print(f"诊断: {result['diagnosis'][:200]}")
    print(f"已执行操作: {result['actions_taken']}")
    print(f"已解决: {result['resolved']}")

asyncio.run(handle_incident())
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [AWS - AI-Powered Operations](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AI驱动的运维自动化
- [freeCodeCamp - DevOps with AI](https://www.youtube.com/watch?v=GWB9ApTPTv4) — AI+DevOps实战

## 7. 2026 年 AIOps Agent 趋势

> 🔄 更新于 2026-05-04

<!-- version-check: AIOps Agent 2026, K8s 1.34, Prometheus, checked 2026-05-04 -->

2026 年运维 Agent 从告警响应工具演进为自主运维平台：

**核心变化**：
1. **MCP 标准化运维工具**：Prometheus、Grafana、K8s 等通过 MCP Server 暴露给 Agent，统一工具接口
2. **K8s 1.34 + Agent 协同**：Pod-level Resources、DRA 等新特性让 Agent 可以更精细地管理资源
3. **多 Agent 运维编排**：告警分类 → 诊断 → 修复的多 Agent 流水线成为标准模式
4. **Runbook 自动化升级**：从静态 Runbook 到 Agent 动态生成修复方案
5. **可观测性 + Agent**：OpenTelemetry 数据直接作为 Agent 上下文，LangSmith Fleet 管理运维 Agent 舰队

**2026 年运维 Agent 工具链**：

| 层级 | 工具 | Agent 集成方式 |
|------|------|---------------|
| 监控 | Prometheus + Grafana | MCP Server / API 工具 |
| 日志 | Elasticsearch 9.x / Loki | ES|QL 查询工具 |
| 追踪 | OpenTelemetry + Jaeger | OTel 数据作为上下文 |
| 编排 | K8s 1.34 | kubectl MCP Server |
| 通知 | Slack / PagerDuty | Webhook 工具 |
| Agent 管理 | LangSmith Fleet | Agent 身份 + 审计 |

来源：[MIT Sloan Review - AI Trends 2026](https://sloanreview.mit.edu/article/five-trends-in-ai-and-data-science-for-2026/)
