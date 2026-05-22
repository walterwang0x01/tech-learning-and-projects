# AI Agent 开发实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 构建能够自主决策和执行任务的智能代理系统

<!-- version-check: LangChain 1.x（create_agent 标准 API）, langchain-openai 1.x, checked 2026-05-22 -->

> 🔄 更新于 2026-05-22：本文档已迁移到 LangChain 1.0+ 推荐 API（`create_agent` 替代废弃的 `initialize_agent` 和 `create_openai_tools_agent`）。

## 1. AI Agent 概述

AI Agent（智能代理）是一个能够感知环境、做出决策并执行动作的自主系统。现代 AI Agent 通常基于大语言模型（LLM），能够：
- **理解任务**：解析用户意图
- **规划步骤**：制定执行计划
- **使用工具**：调用外部API和工具
- **执行动作**：完成任务并反馈结果

## 2. Agent 架构设计

### 2.1 核心组件

```
AI Agent 架构
├── 感知层（Perception）
│   ├── 用户输入解析
│   └── 环境状态感知
├── 决策层（Decision）
│   ├── 任务理解
│   ├── 规划生成
│   └── 工具选择
├── 执行层（Execution）
│   ├── 工具调用
│   ├── 动作执行
│   └── 结果验证
└── 记忆层（Memory）
    ├── 短期记忆
    ├── 长期记忆
    └── 经验学习
```

### 2.2 Agent 类型

- **ReAct Agent**：推理+行动循环
- **Plan-and-Execute Agent**：先规划后执行
- **AutoGPT Agent**：自主目标导向
- **BabyAGI Agent**：任务分解和优先级

## 3. 基础 Agent 实现

### 3.1 简单工具调用 Agent

```python
from typing import List
from langchain.agents import create_agent  # LangChain 1.0+ 标准 API（修复于 2026-05-22）
from langchain_openai import ChatOpenAI

class SimpleAgent:
    """LangChain 1.0+ 标准 Agent 封装。
    
    修复于 2026-05-22：废弃的 `create_openai_tools_agent` + `AgentExecutor` 模式
    已替换为 `create_agent`，后者基于 LangGraph runtime，支持持久化状态、流式输出和中间件。
    """
    
    def __init__(self, tools: List, llm: ChatOpenAI):
        self.tools = tools
        self.llm = llm
        # create_agent 内部使用 ReAct 模式（推理+行动循环）
        self.agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="你是一个有用的AI助手，可以使用工具来帮助用户。",
        )
    
    def run(self, query: str) -> str:
        result = self.agent.invoke({"messages": [{"role": "user", "content": query}]})
        return result["messages"][-1].content
```

### 3.2 工具定义

```python
from langchain_core.tools import BaseTool
import requests

class WeatherTool(BaseTool):
    # 修复于 2026-05-22：Pydantic v2 要求字段必须有类型注解
    name: str = "get_weather"
    description: str = "获取指定城市的天气信息"
    
    def _run(self, city: str) -> str:
        # 调用天气API
        api_key = "your-api-key"
        url = f"https://api.weather.com/v1/current?city={city}&key={api_key}"
        response = requests.get(url)
        data = response.json()
        return f"{city}的天气：{data['temperature']}°C, {data['condition']}"
    
    async def _arun(self, city: str) -> str:
        return self._run(city)

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "执行数学计算"
    
    def _run(self, expression: str) -> str:
        try:
            # 注意：生产环境不要使用 eval，应使用 ast.literal_eval 或专用解析器
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"计算错误: {e}"

# 创建工具列表
tools = [WeatherTool(), CalculatorTool()]
```

> 推荐用 `@tool` 装饰器：LangChain 1.x 中创建工具的更简洁做法是使用 `from langchain_core.tools import tool` 装饰器，配合 docstring 自动提取 description。详见 → [Function Calling机制](../../../ai-agent/07-工具与Function Calling/01-Function Calling机制.md)。

## 4. ReAct Agent 实现

### 4.1 ReAct 模式

ReAct（Reasoning + Acting）结合了推理和行动。在 LangChain 1.0+ 中，`create_agent` 默认就是 ReAct 模式：

```python
# 修复于 2026-05-22：废弃的 initialize_agent + AgentType.REACT_DOCSTORE 模式
# 已被 LangChain 1.0+ 的 create_agent 替代（自带 ReAct 推理+行动循环）
from langchain.agents import create_agent

react_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个推理型 Agent，使用工具回答问题前先思考下一步行动。",
)

# 流式查看中间推理步骤
for chunk in react_agent.stream(
    {"messages": [{"role": "user", "content": "北京今天天气怎么样？如果温度高于20度，计算20*3等于多少"}]},
    stream_mode="updates",
):
    print(chunk)
```

> 升级路径参考：
> - 旧 `initialize_agent(..., agent=AgentType.REACT_DOCSTORE)` → 新 `create_agent(model, tools)`
> - 旧 `agent_executor.invoke({"input": ...})` → 新 `agent.invoke({"messages": [...]})`

### 4.2 自定义 ReAct Agent

```python
class ReActAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.memory = []
    
    def think(self, observation: str) -> Dict:
        """思考下一步行动"""
        prompt = f"""
        观察: {observation}
        可用工具: {list(self.tools.keys())}
        
        请思考下一步应该做什么：
        1. 如果还需要更多信息，使用工具
        2. 如果有足够信息，给出最终答案
        
        格式：Thought: [你的思考]
               Action: [工具名称]
               Action Input: [工具输入]
        """
        
        response = self.llm.invoke(prompt)
        return self._parse_response(response.content)
    
    def act(self, action: str, action_input: str) -> str:
        """执行动作"""
        if action in self.tools:
            tool = self.tools[action]
            return tool._run(action_input)
        return f"未知工具: {action}"
    
    def run(self, query: str, max_iterations: int = 10) -> str:
        """运行Agent"""
        observation = query
        
        for i in range(max_iterations):
            # 思考
            decision = self.think(observation)
            
            if decision.get("final_answer"):
                return decision["final_answer"]
            
            # 行动
            action = decision.get("action")
            action_input = decision.get("action_input")
            observation = self.act(action, action_input)
            
            # 记录
            self.memory.append({
                "thought": decision.get("thought"),
                "action": action,
                "observation": observation
            })
        
        return "达到最大迭代次数，无法完成任务"
```

## 5. Plan-and-Execute Agent

### 5.1 规划器实现

```python
class Planner:
    def __init__(self, llm):
        self.llm = llm
    
    def create_plan(self, goal: str) -> List[str]:
        """创建执行计划"""
        prompt = f"""
        目标: {goal}
        
        请创建一个详细的执行计划，将目标分解为多个步骤。
        每个步骤应该是具体可执行的。
        
        格式：
        1. [步骤1]
        2. [步骤2]
        3. [步骤3]
        """
        
        response = self.llm.invoke(prompt)
        plan = self._parse_plan(response.content)
        return plan
    
    def _parse_plan(self, text: str) -> List[str]:
        """解析计划文本"""
        steps = []
        for line in text.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                step = line.split('.', 1)[1].strip()
                steps.append(step)
        return steps

class Executor:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
    
    def execute_step(self, step: str, context: Dict) -> str:
        """执行单个步骤"""
        prompt = f"""
        步骤: {step}
        上下文: {context}
        可用工具: {list(self.tools.keys())}
        
        请执行这个步骤，如果需要使用工具，请说明。
        """
        
        response = self.llm.invoke(prompt)
        # 解析工具调用
        tool_calls = self._extract_tool_calls(response.content)
        
        results = []
        for tool_name, tool_input in tool_calls:
            if tool_name in self.tools:
                result = self.tools[tool_name]._run(tool_input)
                results.append(result)
        
        return ' '.join(results)
    
    def _extract_tool_calls(self, text: str) -> List[tuple]:
        """提取工具调用"""
        # 简单的解析逻辑，实际应该更复杂
        tool_calls = []
        # 实现工具调用解析
        return tool_calls

class PlanAndExecuteAgent:
    def __init__(self, llm, tools):
        self.planner = Planner(llm)
        self.executor = Executor(llm, tools)
        self.context = {}
    
    def run(self, goal: str) -> str:
        """运行Agent"""
        # 创建计划
        plan = self.planner.create_plan(goal)
        print(f"执行计划: {plan}")
        
        # 执行每个步骤
        results = []
        for step in plan:
            result = self.executor.execute_step(step, self.context)
            results.append(result)
            self.context[f"step_{len(results)}"] = result
        
        return '\n'.join(results)
```

## 6. 记忆系统

### 6.1 短期记忆

```python
import time
from collections import deque
from typing import Dict, List

class ShortTermMemory:
    def __init__(self, max_size: int = 10):
        self.memory = deque(maxlen=max_size)
    
    def add(self, observation: str, action: str, result: str):
        """添加记忆"""
        self.memory.append({
            "observation": observation,
            "action": action,
            "result": result,
            "timestamp": time.time()
        })
    
    def get_recent(self, n: int = 5) -> List[Dict]:
        """获取最近的记忆"""
        return list(self.memory)[-n:]
    
    def search(self, query: str) -> List[Dict]:
        """搜索相关记忆"""
        relevant = []
        for item in self.memory:
            if query.lower() in item["observation"].lower():
                relevant.append(item)
        return relevant
```

### 6.2 长期记忆

```python
import json
from datetime import datetime

class LongTermMemory:
    def __init__(self, storage_path: str = "memory.json"):
        self.storage_path = storage_path
        self.memory = self._load()
    
    def _load(self) -> Dict:
        """加载记忆"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"facts": [], "experiences": []}
    
    def save(self):
        """保存记忆"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def add_fact(self, fact: str, source: str = ""):
        """添加事实"""
        self.memory["facts"].append({
            "fact": fact,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def add_experience(self, task: str, success: bool, notes: str = ""):
        """添加经验"""
        self.memory["experiences"].append({
            "task": task,
            "success": success,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def recall(self, query: str) -> List[Dict]:
        """回忆相关信息"""
        relevant = []
        for fact in self.memory["facts"]:
            if query.lower() in fact["fact"].lower():
                relevant.append(fact)
        return relevant
```

## 7. 工具系统

### 7.1 工具注册

```python
from typing import Optional
from langchain_core.tools import BaseTool

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())
    
    def get_tool_descriptions(self) -> str:
        """获取工具描述"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"- {name}: {tool.description}")
        return '\n'.join(descriptions)
```

### 7.2 工具链

```python
class ToolChain:
    def __init__(self, tools: List[BaseTool]):
        self.tools = tools
        self.execution_history = []
    
    def execute(self, tool_name: str, input_data: str) -> str:
        """执行工具"""
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            return f"工具 {tool_name} 不存在"
        
        try:
            result = tool._run(input_data)
            self.execution_history.append({
                "tool": tool_name,
                "input": input_data,
                "output": result,
                "success": True
            })
            return result
        except Exception as e:
            self.execution_history.append({
                "tool": tool_name,
                "input": input_data,
                "error": str(e),
                "success": False
            })
            return f"执行失败: {e}"
```

## 8. 实际应用示例

### 8.1 代码生成 Agent

```python
class CodeGenerationAgent:
    def __init__(self, llm, tools):
        self.agent = PlanAndExecuteAgent(llm, tools)
    
    def generate_code(self, requirement: str) -> str:
        """生成代码"""
        goal = f"根据以下需求生成Python代码：{requirement}"
        return self.agent.run(goal)
    
    def refactor_code(self, code: str, improvement: str) -> str:
        """重构代码"""
        goal = f"重构以下代码，改进：{improvement}\n\n代码：\n{code}"
        return self.agent.run(goal)
```

### 8.2 数据分析 Agent

```python
class DataAnalysisAgent:
    def __init__(self, llm, tools):
        self.agent = PlanAndExecuteAgent(llm, tools)
        self.data_cache = {}
    
    def analyze(self, data_path: str, question: str) -> str:
        """分析数据"""
        # 加载数据
        if data_path not in self.data_cache:
            self.data_cache[data_path] = self._load_data(data_path)
        
        goal = f"""
        分析数据文件 {data_path}，回答以下问题：
        {question}
        
        数据概览：
        {self.data_cache[data_path].head().to_string()}
        """
        
        return self.agent.run(goal)
    
    def _load_data(self, path: str):
        import pandas as pd
        return pd.read_csv(path)
```

## 9. 监控和调试

### 9.1 Agent 监控

```python
class AgentMonitor:
    def __init__(self):
        self.metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_steps": 0,
            "tool_usage": {}
        }
    
    def record_run(self, success: bool, steps: int, tools_used: List[str]):
        """记录运行"""
        self.metrics["total_runs"] += 1
        if success:
            self.metrics["successful_runs"] += 1
        else:
            self.metrics["failed_runs"] += 1
        
        # 更新平均步数
        total = self.metrics["total_runs"]
        current_avg = self.metrics["average_steps"]
        self.metrics["average_steps"] = (
            (current_avg * (total - 1) + steps) / total
        )
        
        # 记录工具使用
        for tool in tools_used:
            self.metrics["tool_usage"][tool] = \
                self.metrics["tool_usage"].get(tool, 0) + 1
    
    def get_report(self) -> str:
        """生成报告"""
        success_rate = (
            self.metrics["successful_runs"] / self.metrics["total_runs"] * 100
            if self.metrics["total_runs"] > 0 else 0
        )
        
        report = f"""
        Agent 运行报告
        ==============
        总运行次数: {self.metrics["total_runs"]}
        成功次数: {self.metrics["successful_runs"]}
        失败次数: {self.metrics["failed_runs"]}
        成功率: {success_rate:.2f}%
        平均步数: {self.metrics["average_steps"]:.2f}
        
        工具使用统计:
        {json.dumps(self.metrics["tool_usage"], indent=2)}
        """
        return report
```

## 10. 最佳实践

### 10.1 错误处理

```python
class RobustAgent:
    def __init__(self, agent, max_retries=3):
        self.agent = agent
        self.max_retries = max_retries
    
    def run(self, query: str) -> str:
        """带重试的运行"""
        for attempt in range(self.max_retries):
            try:
                return self.agent.run(query)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"执行失败: {e}"
                print(f"尝试 {attempt + 1} 失败，重试...")
```

### 10.2 成本控制

```python
class CostAwareAgent:
    def __init__(self, agent, budget: float = 1.0):
        self.agent = agent
        self.budget = budget
        self.cost = 0.0
    
    def estimate_cost(self, query: str) -> float:
        """估算成本"""
        # 简单的token估算
        tokens = len(query.split()) * 1.3  # 粗略估算
        return tokens * 0.0001  # 假设每token成本
    
    def run(self, query: str) -> str:
        """成本感知运行"""
        estimated_cost = self.estimate_cost(query)
        if self.cost + estimated_cost > self.budget:
            return "超出预算，无法执行"
        
        result = self.agent.run(query)
        self.cost += estimated_cost
        return result
```

## 11. 总结

AI Agent 开发的关键要素：
- **清晰的架构**：分离感知、决策、执行
- **强大的工具系统**：灵活的工具注册和调用
- **有效的记忆管理**：短期和长期记忆结合
- **完善的监控**：跟踪性能和成本
- **错误处理**：确保系统稳定性

通过合理设计，可以构建出强大、可靠的 AI Agent 系统。

