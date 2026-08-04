# 从 Claude Code 学构建生产级 AI Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 如果你要从零构建一个 AI Agent 项目，Claude Code 的 512,000 行源码是目前最好的架构参考

<!-- version-check: Claude Code 2.1.145, Claude Code Desktop GA, Agent Teams public, checked 2026-05-21 -->

## 1. 为什么要学 Claude Code 的架构

Claude Code 泄露的源码揭示了一个关键事实：**模型只占代码量的 1.6%（~8,000 行），98.4% 是工程脚手架**。同一个 Claude 模型在 Web 版和 Claude Code 中表现差异巨大，原因不在模型，而在围绕模型构建的工程系统。

这意味着：如果你想构建一个强大的 AI Agent，重点不是选哪个模型，而是怎么设计围绕模型的系统。

```
你的 Agent 项目应该关注的层次：

┌─────────────────────────────────────────────┐
│  用户体验层（5%）  CLI / Web UI / IDE 插件    │
├─────────────────────────────────────────────┤
│  安全与权限层（15%）  权限模型 / 输入验证      │
├─────────────────────────────────────────────┤
│  工具系统层（25%）  工具定义 / Schema / 执行   │
├─────────────────────────────────────────────┤
│  编排与状态层（25%）  Agent循环 / 多Agent协调  │
├─────────────────────────────────────────────┤
│  上下文与记忆层（20%）  缓存 / 压缩 / 持久化  │
├─────────────────────────────────────────────┤
│  模型调用层（5%）  API调用 / 流式 / 重试      │
├─────────────────────────────────────────────┤
│  可观测层（5%）  日志 / 指标 / 成本追踪       │
└─────────────────────────────────────────────┘
```

## 2. Agent 主循环：最核心的 20 行代码

所有 Agent 的核心都是同一个循环。Claude Code 的实现（简化版）：

```python
"""Agent 主循环 — 所有 Agent 项目的起点"""

async def agent_loop(user_message: str, tools: list, system_prompt: str):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        # 1. 每轮注入系统提示（CLAUDE.md 每轮加载的原理）
        current_system = load_system_prompt(system_prompt)
        
        # 2. 调用 LLM
        response = await llm.create(
            system=current_system,
            messages=messages,
            tools=tools,
        )
        
        # 3. 如果没有工具调用 → 循环结束，返回结果
        if not response.tool_calls:
            return response.content
        
        # 4. 有工具调用 → 执行工具 → 结果反馈 → 继续循环
        for tool_call in response.tool_calls:
            # 权限检查（Claude Code 的五级权限在这里）
            if not check_permission(tool_call):
                result = "Permission denied"
            else:
                result = await execute_tool(tool_call)
            
            messages.append({"role": "tool", "content": result})
```

**Claude Code 的启示：**
- 循环本身很简单，复杂度在循环的每个环节里
- `load_system_prompt()` 每轮重新加载 → 这就是 CLAUDE.md 每轮注入的原理
- `check_permission()` 在工具执行前 → 安全是前置的，不是事后的
- 没有工具调用时循环才结束 → Agent 会持续工作直到任务完成


## 3. 工具设计：Anthropic 官方原则

Anthropic 在 2025 年发表了《Writing Effective Tools for AI Agents》，结合 Claude Code 源码，总结出以下工具设计原则：

### 原则一：为 Agent 设计，不是为开发者设计

```
❌ 传统 API 思维：
   list_contacts() → 返回所有联系人 → Agent 逐个读取 → 浪费上下文

✅ Agent 友好思维：
   search_contacts(name="Jane") → 只返回相关结果 → 节省上下文
```

Agent 的上下文窗口是有限的，而内存是廉价的。工具应该帮 Agent 跳到相关信息，而不是让它暴力搜索。

### 原则二：合并高频链式操作

```
❌ 碎片化工具：
   list_users() → list_events() → create_event()
   Agent 需要 3 次工具调用

✅ 合并工具：
   schedule_event(attendees=["Jane"], time="next week")
   一次调用完成查找可用时间 + 创建事件
```

### 原则三：返回有意义的上下文，而非原始数据

```python
# ❌ 返回原始 ID
{"user_id": "a1b2c3d4-e5f6-7890", "channel_id": "C0ABCDEF"}

# ✅ 返回可理解的信息
{"user_name": "Jane Smith", "channel_name": "#engineering"}
# 如果下游工具需要 ID，提供 response_format 参数切换详细/简洁模式
```

### 原则四：控制返回的 Token 量

```python
# Claude Code 默认限制工具响应为 25,000 tokens
MAX_TOOL_RESPONSE_TOKENS = 25_000

# 实现分页、过滤、截断
def search_logs(query: str, limit: int = 50, offset: int = 0) -> str:
    results = db.search(query, limit=limit, offset=offset)
    response = format_results(results)
    
    if len(response) > MAX_TOOL_RESPONSE_TOKENS:
        response = truncate(response)
        response += "\n[结果已截断，请使用更精确的查询或分页获取更多]"
    
    return response
```

### 原则五：错误信息要可操作

```python
# ❌ 无用的错误
raise ToolError("Error 422: Unprocessable Entity")

# ✅ 可操作的错误
raise ToolError(
    "日期格式无效。请使用 YYYY-MM-DD 格式，例如 '2026-04-01'。"
    "你提供的是: '4/1/2026'"
)
```

### 原则六：命名空间隔离

```python
# 当 Agent 有几十上百个工具时，命名空间防止混淆
tools = [
    "slack_search_messages",    # Slack 搜索
    "slack_send_message",       # Slack 发送
    "jira_search_issues",       # Jira 搜索
    "jira_create_issue",        # Jira 创建
    "github_search_code",       # GitHub 搜索
    "github_create_pr",         # GitHub PR
]
# 前缀命名让 Agent 清楚每个工具属于哪个服务
```


## 4. 权限系统：从 Claude Code 的五级模型学安全设计

```python
"""生产级 Agent 权限系统实现"""

from enum import Enum
from pathlib import Path
import fnmatch
import json

class PermissionLevel(Enum):
    ALWAYS_ALLOW = "always_allow"    # 无需确认
    AUTO_APPROVE = "auto_approve"    # 模式匹配自动批准
    PROMPT = "prompt"                # 需要用户确认
    PLAN_ONLY = "plan_only"          # 只规划不执行
    NEVER_ALLOW = "never_allow"      # 始终拒绝

class PermissionManager:
    def __init__(self, config_path: str = "~/.agent/permissions.json"):
        self.config = self._load_config(config_path)
    
    def check(self, tool_name: str, args: dict) -> PermissionLevel:
        # 1. 黑名单优先检查
        for pattern in self.config.get("deny", []):
            if self._matches(tool_name, args, pattern):
                return PermissionLevel.NEVER_ALLOW
        
        # 2. 白名单检查
        for pattern in self.config.get("allow", []):
            if self._matches(tool_name, args, pattern):
                return PermissionLevel.ALWAYS_ALLOW
        
        # 3. 自动批准规则
        for pattern in self.config.get("auto_approve", []):
            if self._matches(tool_name, args, pattern):
                return PermissionLevel.AUTO_APPROVE
        
        # 4. 默认需要确认
        return PermissionLevel.PROMPT
    
    def _matches(self, tool_name: str, args: dict, pattern: str) -> bool:
        # 支持 glob 模式：Read(**), Bash(npm test*), Write(src/**/*.ts)
        tool_pattern, _, arg_pattern = pattern.partition("(")
        arg_pattern = arg_pattern.rstrip(")")
        
        if not fnmatch.fnmatch(tool_name, tool_pattern):
            return False
        if arg_pattern and args:
            return any(fnmatch.fnmatch(str(v), arg_pattern) for v in args.values())
        return True
```

**配置示例：**

```json
{
  "allow": [
    "FileRead(**)",
    "Search(**)",
    "Bash(npm test*)",
    "Bash(git status)",
    "Bash(git diff*)"
  ],
  "auto_approve": [
    "FileWrite(src/**/*.test.*)",
    "Bash(python -m pytest*)"
  ],
  "deny": [
    "Bash(rm -rf *)",
    "FileRead(~/.ssh/**)",
    "FileRead(**/.env*)",
    "Bash(*sudo*)",
    "Bash(*curl*|*wget*)"
  ]
}
```


## 5. 上下文与记忆：长会话不崩溃的秘密

### 5.1 三层记忆架构

```
┌─────────────────────────────────────────────┐
│  第一层：工作记忆（对话上下文）                 │
│  ├─ 当前会话的消息历史                        │
│  ├─ 工具调用结果                              │
│  └─ 受上下文窗口限制（需要压缩策略）           │
├─────────────────────────────────────────────┤
│  第二层：项目记忆（CLAUDE.md / 配置文件）       │
│  ├─ 每轮重新加载（最高杠杆）                   │
│  ├─ 项目规范、编码风格、常用命令               │
│  └─ 不受上下文窗口限制（文件系统持久化）        │
├─────────────────────────────────────────────┤
│  第三层：长期记忆（memdir / 记忆蒸馏）          │
│  ├─ 跨会话持久化                              │
│  ├─ 自动提取关键知识                          │
│  └─ KAIROS autoDream 定期整理                 │
└─────────────────────────────────────────────┘
```

### 5.2 上下文压缩实现

```python
"""从 Claude Code 学到的上下文压缩策略"""

class ContextManager:
    MAX_CONTEXT_TOKENS = 128_000
    COMPACT_THRESHOLD = 0.8  # 80% 时开始压缩
    MAX_COMPACT_FAILURES = 3  # Claude Code 的教训：连续失败 3 次就停止
    
    def __init__(self, llm):
        self.llm = llm
        self.messages = []
        self.compact_failures = 0
    
    async def add_message(self, message: dict):
        self.messages.append(message)
        
        usage = self.estimate_tokens() / self.MAX_CONTEXT_TOKENS
        
        if usage > 0.95:
            # 策略5：PTL截断 — 最后手段，丢弃最早消息
            self._truncate_oldest()
        elif usage > self.COMPACT_THRESHOLD:
            # 策略4：Full Compact — 摘要整个历史
            await self._full_compact()
        
        # 策略1：Microcompact — 持续运行，清除旧工具结果
        self._microcompact()
    
    def _microcompact(self):
        """清除超过 10 轮的工具调用详细结果，只保留摘要"""
        for i, msg in enumerate(self.messages[:-10]):
            if msg.get("role") == "tool" and len(str(msg["content"])) > 500:
                msg["content"] = f"[工具结果已压缩: {msg['content'][:100]}...]"
    
    async def _full_compact(self):
        """用 LLM 摘要整个对话历史"""
        if self.compact_failures >= self.MAX_COMPACT_FAILURES:
            return  # Claude Code 的教训：避免无限重试
        
        try:
            summary = await self.llm.create(
                messages=[{
                    "role": "user",
                    "content": f"请摘要以下对话的关键决策和结论：\n{self._format_history()}"
                }]
            )
            # 用摘要替换历史消息
            self.messages = [
                {"role": "system", "content": f"[会话摘要]\n{summary}"},
                *self.messages[-5:]  # 保留最近 5 条
            ]
            self.compact_failures = 0
        except Exception:
            self.compact_failures += 1
    
    def _truncate_oldest(self):
        """丢弃最早的消息组"""
        # 保留系统消息和最近 10 条
        self.messages = [self.messages[0]] + self.messages[-10:]
```

### 5.3 cache_edits：标记删除而非真删除

```python
"""Claude Code 长会话不变慢的核心机制"""

class CacheAwareMessageStore:
    """标记删除旧消息，保持缓存连续性"""
    
    def __init__(self):
        self.messages = []
        self.skip_indices = set()  # 标记为跳过的消息索引
    
    def mark_skip(self, index: int):
        """标记消息为跳过（而非删除）"""
        self.skip_indices.add(index)
    
    def get_visible_messages(self) -> list:
        """返回模型可见的消息（跳过被标记的）"""
        return [
            msg for i, msg in enumerate(self.messages)
            if i not in self.skip_indices
        ]
    
    def get_cache_key(self) -> str:
        """缓存键基于完整消息列表（包括被跳过的）"""
        # 关键：缓存连续性不受 skip 影响
        return hash(tuple(str(m) for m in self.messages))
```


## 6. 多 Agent 编排：从单 Agent 到 Swarm

### 6.1 何时需要多 Agent

```
单 Agent 够用的场景：
├─ 单文件修改
├─ 简单问答
├─ 线性工作流（A → B → C）
└─ 上下文窗口内能完成的任务

需要多 Agent 的场景：
├─ 跨多个文件/模块的重构
├─ 需要不同专业知识的任务（前端 + 后端 + 测试）
├─ 任务可并行化（互不依赖的子任务）
└─ 单个上下文窗口装不下的大型任务
```

### 6.2 Claude Code 的 Swarm 模式实现

```python
"""从 Claude Code 学到的多 Agent 编排模式"""

import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class AgentTask:
    id: str
    description: str
    status: str = "pending"  # pending → running → completed → failed
    result: str = ""
    assigned_to: str = ""

@dataclass  
class AgentTeam:
    lead: str
    members: list[str] = field(default_factory=list)
    tasks: list[AgentTask] = field(default_factory=list)
    
    # Claude Code 的关键设计：文件系统通信
    workspace: Path = Path(".agent/team")
    
    def save_state(self):
        """持久化团队状态到磁盘（可恢复）"""
        self.workspace.mkdir(parents=True, exist_ok=True)
        state = {
            "lead": self.lead,
            "members": self.members,
            "tasks": [vars(t) for t in self.tasks],
        }
        (self.workspace / "team.json").write_text(json.dumps(state, indent=2))
    
    def send_message(self, from_agent: str, to_agent: str, content: str):
        """Agent 间通信：写入对方的 inbox 文件"""
        inbox = self.workspace / to_agent / "inbox.jsonl"
        inbox.parent.mkdir(parents=True, exist_ok=True)
        msg = json.dumps({"from": from_agent, "content": content})
        with open(inbox, "a") as f:
            f.write(msg + "\n")


async def run_swarm(task_description: str, llm):
    """Lead Agent 分解任务 → 分配给 Worker → 聚合结果"""
    
    # 1. Lead Agent 分解任务
    plan = await llm.create(messages=[{
        "role": "user",
        "content": f"将以下任务分解为可并行执行的子任务：\n{task_description}"
    }])
    
    subtasks = parse_subtasks(plan)
    team = AgentTeam(lead="lead", members=[f"worker_{i}" for i in range(len(subtasks))])
    
    # 2. 并行执行子任务（共享 Prompt Cache）
    async def run_worker(worker_id: str, task: AgentTask):
        # 关键：子 Agent 继承父上下文的缓存
        result = await llm.create(
            messages=[{"role": "user", "content": task.description}],
            # cache_control: 复用父上下文的缓存前缀
        )
        task.status = "completed"
        task.result = result
        team.save_state()  # 持久化到磁盘
    
    await asyncio.gather(*[
        run_worker(f"worker_{i}", task) 
        for i, task in enumerate(subtasks)
    ])
    
    # 3. Lead Agent 聚合结果
    results = "\n".join(f"子任务 {t.id}: {t.result}" for t in subtasks)
    final = await llm.create(messages=[{
        "role": "user",
        "content": f"以下是各子任务的结果，请合并为最终输出：\n{results}"
    }])
    
    return final
```

### 6.3 编排提示词而非代码

Claude Code 的一个关键发现：**多 Agent 编排算法是提示词，不是代码**。

```python
COORDINATOR_PROMPT = """
你是团队的 Lead Agent，负责协调多个 Worker Agent。

规则：
1. 不要橡皮图章式地批准低质量工作 — 如果 Worker 的输出不够好，要求重做
2. 你必须理解每个发现后才能指导后续工作 — 不要把理解工作转交给另一个 Worker
3. 分配任务时要明确：输入是什么、期望输出是什么、完成标准是什么
4. 当多个 Worker 的结果有冲突时，你负责裁决
5. 如果一个子任务失败了，评估是否影响其他子任务，必要时重新规划
"""
```


## 7. 成本工程：每个 Token 都是钱

### 7.1 缓存经济学

```
Claude Opus 4.6 定价：
├─ 标准输入：$5 / 百万 Token
├─ 缓存命中：$0.5 / 百万 Token（90% 折扣）
└─ 缓存未命中 = 成本 10x

→ 架构设计必须以缓存为中心
```

### 7.2 成本优化策略

```python
"""从 Claude Code 学到的成本优化"""

class CostOptimizer:
    # 策略1：模型路由 — 用最便宜的够用模型
    MODEL_TIERS = {
        "simple": "claude-haiku",      # 简单任务（格式化、分类）
        "standard": "claude-sonnet",   # 标准任务（代码编写、分析）
        "complex": "claude-opus",      # 复杂任务（架构设计、多步推理）
    }
    
    # 策略2：缓存友好的消息结构
    @staticmethod
    def build_messages(system: str, history: list, user_msg: str):
        return [
            # 静态内容放前面 → 缓存命中率高
            {"role": "system", "content": system, "cache_control": {"type": "ephemeral"}},
            # 历史消息 → 增量追加，不重排序
            *history,
            # 动态内容放最后 → 只有这部分是新的
            {"role": "user", "content": user_msg},
        ]
    
    # 策略3：工具响应 Token 限制
    MAX_TOOL_RESPONSE = 25_000  # Claude Code 的默认值
    
    # 策略4：子 Agent 复用父缓存
    # fork 子 Agent 时，创建父上下文的字节级副本
    # 共享 Prompt Cache → 并行 Agent 几乎不增加额外成本
```

### 7.3 成本监控

```python
"""Token 成本追踪器"""

class CostTracker:
    PRICING = {
        "claude-opus": {"input": 5.0, "output": 25.0, "cache_read": 0.5},
        "claude-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
        "claude-haiku": {"input": 1.0, "output": 5.0, "cache_read": 0.1},
    }
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cache_hits = 0
        self.total_cost_usd = 0.0
    
    def track(self, model: str, usage: dict):
        pricing = self.PRICING[model]
        input_cost = usage["input_tokens"] * pricing["input"] / 1_000_000
        output_cost = usage["output_tokens"] * pricing["output"] / 1_000_000
        cache_savings = usage.get("cache_read_tokens", 0) * (
            pricing["input"] - pricing["cache_read"]
        ) / 1_000_000
        
        self.total_cost_usd += input_cost + output_cost
        print(f"本次: ${input_cost + output_cost:.4f} | 缓存节省: ${cache_savings:.4f}")
```

## 8. 安全加固：23 项检查的启示

### 8.1 输入验证清单

```python
"""从 Claude Code 的 bashSecurity.ts 学到的安全检查"""

DANGEROUS_PATTERNS = [
    # 1. 危险命令
    r"rm\s+-rf\s+/",
    r"mkfs\.",
    r"dd\s+if=",
    r":(){ :|:& };:",  # Fork bomb
    
    # 2. 权限提升
    r"\bsudo\b",
    r"\bsu\s+-",
    r"chmod\s+777",
    
    # 3. 网络外传
    r"\bcurl\b.*\|\s*bash",
    r"\bwget\b.*\|\s*sh",
    
    # 4. 环境变量注入
    r"export\s+.*=.*\$\(",
    r"\beval\b",
    
    # 5. Zsh 特有攻击（Claude Code 的发现）
    r"=curl",           # Zsh 等号扩展绕过
    r"\x00",            # IFS null-byte 注入
    r"[\u200b-\u200f]", # Unicode 零宽字符注入
]

def validate_command(command: str) -> tuple[bool, str]:
    """验证命令安全性，返回 (是否安全, 原因)"""
    import re
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command):
            return False, f"命令匹配危险模式: {pattern}"
    return True, "OK"
```

### 8.2 工具安全标记

```python
"""每个工具必须声明安全属性"""

@dataclass
class ToolSafety:
    has_side_effects: bool    # 是否有副作用（写入/删除/发送）
    requires_read_first: bool # 是否需要先读取再修改（Claude Code 的 FileEdit 要求）
    network_access: bool      # 是否需要网络访问
    max_execution_time: int   # 最大执行时间（秒）
    
# Claude Code 的做法：工具默认标记为 "unsafe, writable"
# 除非开发者显式声明为安全
```

## 9. 可扩展性：Hook 系统设计

```python
"""从 Claude Code 学到的 Hook 系统"""

from enum import Enum
from typing import Callable, Any

class HookEvent(Enum):
    SESSION_START = "session_start"
    USER_PROMPT = "user_prompt"
    PRE_TOOL_USE = "pre_tool_use"
    POST_TOOL_USE = "post_tool_use"
    PRE_COMPACT = "pre_compact"
    AGENT_RESPONSE = "agent_response"
    SESSION_END = "session_end"

class HookManager:
    def __init__(self):
        self._hooks: dict[HookEvent, list[Callable]] = {e: [] for e in HookEvent}
    
    def register(self, event: HookEvent, handler: Callable):
        self._hooks[event].append(handler)
    
    async def trigger(self, event: HookEvent, context: dict) -> dict:
        for handler in self._hooks[event]:
            result = await handler(context)
            if result and result.get("abort"):
                return result  # Hook 可以中止操作
        return {"continue": True}

# 使用示例
hooks = HookManager()

# 写文件前自动 lint
async def auto_lint(ctx):
    if ctx["tool"] == "FileWrite" and ctx["file"].endswith((".ts", ".js")):
        os.system(f"npx eslint --fix {ctx['file']}")

# 每次工具调用后运行相关测试
async def auto_test(ctx):
    if ctx["tool"] in ("FileWrite", "FileEdit"):
        os.system(f"npm test -- --related {ctx['file']}")

hooks.register(HookEvent.PRE_TOOL_USE, auto_lint)
hooks.register(HookEvent.POST_TOOL_USE, auto_test)
```


## 10. 项目配置系统：最高杠杆的控制手段

```python
"""项目配置加载器 — 模仿 CLAUDE.md 每轮加载机制"""

from pathlib import Path

class ProjectConfig:
    """
    层级配置加载：
    1. 全局配置 ~/.agent/config.md
    2. 项目根目录 ./AGENT.md
    3. 子目录 ./src/AGENT.md（覆盖上层）
    """
    
    def load(self, working_dir: Path) -> str:
        configs = []
        
        # 全局配置
        global_config = Path.home() / ".agent" / "config.md"
        if global_config.exists():
            configs.append(global_config.read_text())
        
        # 从项目根到当前目录，逐层加载
        for parent in reversed(list(working_dir.parents)):
            config_file = parent / "AGENT.md"
            if config_file.exists():
                configs.append(config_file.read_text())
        
        # 当前目录
        local_config = working_dir / "AGENT.md"
        if local_config.exists():
            configs.append(local_config.read_text())
        
        return "\n---\n".join(configs)
    
    def inject_to_system_prompt(self, base_prompt: str, working_dir: Path) -> str:
        """每轮调用时注入项目配置"""
        project_context = self.load(working_dir)
        if project_context:
            return f"{base_prompt}\n\n## 项目配置\n{project_context}"
        return base_prompt
```

## 11. 评估驱动开发：用 Eval 优化工具

Anthropic 官方推荐的工具优化流程：

```
1. 构建原型工具
   ↓
2. 生成评估任务（基于真实场景，不是玩具示例）
   ↓
3. 运行评估（Agent 循环 + 工具调用 + 结果验证）
   ↓
4. 分析结果（Agent 在哪里卡住？哪些工具调用失败？）
   ↓
5. 让 Agent 自己优化工具（把评估日志喂给 Claude Code）
   ↓
6. 重复 3-5 直到性能达标
   ↓
7. 用留出测试集验证（防止过拟合）
```

**关键洞察：** Anthropic 发现让 Claude Code 分析评估日志并自动优化工具描述，效果甚至超过人类专家手写的工具定义。Claude Sonnet 3.5 在 SWE-bench 上的 SOTA 成绩，就是通过精确优化工具描述实现的。

## 12. 完整项目脚手架

```
my-agent/
├── agent.md                    # 项目配置（每轮加载）
├── src/
│   ├── main.py                 # 入口 + Agent 主循环
│   ├── tools/                  # 工具系统
│   │   ├── __init__.py         # 工具注册表
│   │   ├── base.py             # 工具基类（Schema + 权限 + 执行）
│   │   ├── file_tools.py       # 文件操作工具
│   │   ├── shell_tools.py      # Shell 命令工具
│   │   ├── search_tools.py     # 搜索工具
│   │   └── mcp_tools.py        # MCP 工具桥接
│   ├── permissions/            # 权限系统
│   │   ├── manager.py          # 五级权限管理器
│   │   └── security.py         # 输入验证 + 安全检查
│   ├── context/                # 上下文管理
│   │   ├── manager.py          # 上下文压缩（5种策略）
│   │   ├── memory.py           # 持久化记忆
│   │   └── cache.py            # Prompt Cache 优化
│   ├── coordinator/            # 多 Agent 编排
│   │   ├── swarm.py            # Swarm 模式
│   │   └── tasks.py            # 任务图管理
│   ├── hooks/                  # Hook 系统
│   │   ├── manager.py          # Hook 管理器
│   │   └── builtin.py          # 内置 Hook（lint/test/notify）
│   └── cost/                   # 成本追踪
│       └── tracker.py          # Token 成本监控
├── config/
│   ├── permissions.json        # 权限配置
│   ├── hooks.json              # Hook 配置
│   └── mcp.json                # MCP Server 配置
├── evals/                      # 评估系统
│   ├── tasks/                  # 评估任务
│   ├── run_eval.py             # 评估运行器
│   └── analyze.py              # 结果分析
└── tests/
    ├── test_tools.py
    ├── test_permissions.py
    └── test_context.py
```

## 13. 从原型到生产的检查清单

```
□ Phase 1: 原型（1-2 天）
  □ Agent 主循环能跑通
  □ 3-5 个核心工具可用
  □ 基础权限检查（allow/deny）
  □ 简单的对话历史管理

□ Phase 2: 可用（1 周）
  □ 工具 Schema 验证（Pydantic/Zod）
  □ 五级权限系统
  □ 上下文压缩（至少 Microcompact + Full Compact）
  □ 错误处理与重试
  □ 成本追踪
  □ 基础评估任务

□ Phase 3: 生产级（2-4 周）
  □ Hook 系统（PreToolUse/PostToolUse）
  □ 多 Agent 编排（如果需要）
  □ Prompt Cache 优化
  □ 输入安全验证（参考 23 项检查）
  □ 持久化记忆（跨会话）
  □ 可观测性（日志/指标/追踪）
  □ 完整评估套件 + 留出测试集
  □ CI/CD 集成评估

□ Phase 4: 规模化
  □ 模型路由（按任务复杂度选模型）
  □ 缓存经济学优化（cache_edits）
  □ 团队记忆同步
  □ 组织策略限制
  □ 安全审计
```

## 14. 沙箱隔离：安全的最后防线

> 来源：`sandbox-adapter.ts` 源码直读

权限系统是"问你能不能做"，沙箱是"就算你偷偷做了也做不到"。Claude Code 使用 `@anthropic-ai/sandbox-runtime` 包实现 OS 级别的沙箱隔离：

```
安全纵深防御模型：

用户输入 → [输入验证] → [权限检查] → [YOLO分类器] → [沙箱隔离] → 实际执行
                                                         ↑
                                                    最后防线
                                                即使前面全被绕过
                                                沙箱仍然阻止危险操作
```

Claude Code 沙箱的核心能力：

- **文件系统限制** — `FsReadRestrictionConfig` / `FsWriteRestrictionConfig` 控制可读写路径
- **网络访问限制** — `NetworkRestrictionConfig` + `NetworkHostPattern` 控制可访问的域名
- **违规事件追踪** — `SandboxViolationStore` 记录所有被拦截的操作
- **路径解析规则** — `//path` = 绝对路径，`/path` = 相对于配置文件目录

### 14.1 为你的 Agent 项目实现基础沙箱

```python
"""Agent 沙箱隔离 — 基于 subprocess 的轻量级实现"""

import subprocess
import os
import tempfile
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class SandboxConfig:
    """沙箱配置：定义允许访问的资源"""
    allowed_read_paths: list[str] = field(default_factory=list)
    allowed_write_paths: list[str] = field(default_factory=list)
    allowed_network_hosts: list[str] = field(default_factory=list)
    max_execution_time: int = 30  # 秒
    max_memory_mb: int = 512
    max_file_size_mb: int = 100

@dataclass
class SandboxViolation:
    """违规记录"""
    action: str        # read / write / network / timeout
    target: str        # 被拦截的路径或域名
    timestamp: float
    tool_name: str

class AgentSandbox:
    """
    轻量级 Agent 沙箱
    
    设计思路（学自 Claude Code）：
    1. 命令执行前验证路径访问权限
    2. 使用 subprocess 的资源限制
    3. 记录所有违规事件（用于审计）
    4. 即使权限系统被绕过，沙箱仍然生效
    """
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.violations: list[SandboxViolation] = []
    
    def check_file_access(self, path: str, mode: str = "read") -> bool:
        """检查文件访问是否在沙箱允许范围内"""
        abs_path = str(Path(path).resolve())
        allowed = (
            self.config.allowed_read_paths if mode == "read"
            else self.config.allowed_write_paths
        )
        
        for allowed_path in allowed:
            if abs_path.startswith(str(Path(allowed_path).resolve())):
                return True
        
        # 记录违规
        import time
        self.violations.append(SandboxViolation(
            action=mode, target=abs_path,
            timestamp=time.time(), tool_name="file_access"
        ))
        return False
    
    def execute_sandboxed(self, command: str, cwd: str = ".") -> dict:
        """在沙箱中执行命令"""
        import resource
        
        def set_limits():
            # 限制内存
            mem_bytes = self.config.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            # 限制文件大小
            file_bytes = self.config.max_file_size_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))
            # 禁止创建子进程（防止 fork bomb）
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
        
        try:
            result = subprocess.run(
                command, shell=True, cwd=cwd,
                capture_output=True, text=True,
                timeout=self.config.max_execution_time,
                preexec_fn=set_limits,
                env={
                    **os.environ,
                    "PATH": "/usr/bin:/bin",  # 限制可执行路径
                    "HOME": tempfile.mkdtemp(),  # 隔离 HOME 目录
                }
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "violations": len(self.violations),
            }
        except subprocess.TimeoutExpired:
            import time
            self.violations.append(SandboxViolation(
                action="timeout", target=command,
                timestamp=time.time(), tool_name="bash"
            ))
            return {"error": "执行超时", "violations": len(self.violations)}

# 使用示例
sandbox = AgentSandbox(SandboxConfig(
    allowed_read_paths=["./src", "./docs", "./tests"],
    allowed_write_paths=["./src", "./tests"],
    allowed_network_hosts=["api.anthropic.com", "pypi.org"],
    max_execution_time=30,
))

# 安全执行
result = sandbox.execute_sandboxed("python -m pytest tests/", cwd=".")

# 检查文件访问
if sandbox.check_file_access("/etc/passwd", "read"):
    print("允许读取")
else:
    print("沙箱拦截：不允许读取系统文件")
```

**关键设计原则：** 沙箱是防御纵深的最后一层。即使权限系统被 Prompt 注入绕过，沙箱仍然在 OS 层面阻止危险操作。生产环境建议使用 Docker 容器或 gVisor 等更强的隔离方案。


## 15. 技能系统：可复用的 Agent 工作流

> 来源：`loadSkillsDir.ts` + `commands.ts` 源码直读

Claude Code 把可复用的工作流抽象为"技能"（Skills），而不是硬编码在代码里。技能系统有四层来源，按优先级排列：

```
技能加载优先级（后加载的覆盖先加载的）：

┌─────────────────────────────────────────────┐
│  第 4 层：Plugin Skills（第三方插件技能）      │
│  ├─ 来自已安装的第三方插件                    │
│  └─ 最高优先级，可覆盖内置技能                │
├─────────────────────────────────────────────┤
│  第 3 层：Skill Dir Commands（用户自定义技能） │
│  ├─ 来自 .claude/skills/ 目录                │
│  └─ 用户可以为项目定制专属技能                │
├─────────────────────────────────────────────┤
│  第 2 层：Builtin Plugin Skills（内置插件技能）│
│  ├─ 来自内置插件（如 VS Code 集成）           │
│  └─ 提供 IDE 相关的增强能力                   │
├─────────────────────────────────────────────┤
│  第 1 层：Bundled Skills（打包内置技能）       │
│  ├─ 随 Claude Code 一起发布                   │
│  └─ 基础能力，最低优先级                      │
└─────────────────────────────────────────────┘
```

### 15.1 技能的核心设计

Claude Code 技能系统的几个关键特性：

- **Frontmatter 元数据** — 每个技能文件头部包含 YAML 格式的描述、参数定义、触发条件
- **动态技能发现** — `getDynamicSkills` 在文件操作过程中自动发现并激活相关技能
- **Token 估算优化** — 技能列表展示时只基于 Frontmatter（名称+描述+whenToUse）估算 Token，不加载完整内容
- **参数替换** — `substituteArguments` 支持在技能模板中注入运行时参数
- **Shell 命令执行** — `executeShellCommandsInPrompt` 允许技能内嵌 Shell 命令获取动态上下文

### 15.2 为你的 Agent 项目设计技能系统

```python
"""Agent 技能系统 — 可复用的工作流模板"""

import yaml
import re
import subprocess
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class SkillMetadata:
    """技能元数据（对应 Frontmatter）"""
    name: str
    description: str
    when_to_use: str = ""           # 何时触发此技能
    arguments: list[str] = field(default_factory=list)  # 支持的参数
    file_patterns: list[str] = field(default_factory=list)  # 关联的文件模式
    priority: int = 0               # 优先级（高覆盖低）

@dataclass
class Skill:
    """一个完整的技能"""
    metadata: SkillMetadata
    content: str                    # 技能的完整提示词模板
    source: str                     # 来源层级：bundled / plugin / user / third_party
    file_path: Path | None = None

class SkillManager:
    """
    四层技能管理器（学自 Claude Code）
    
    设计要点：
    1. 技能列表只加载 Frontmatter → 节省 Token
    2. 实际使用时才加载完整内容 → 按需加载
    3. 文件操作后动态发现新技能 → 上下文感知
    4. 支持参数替换和 Shell 命令 → 动态内容
    """
    
    SKILL_SOURCES = [
        ("bundled", "skills/bundled/"),
        ("builtin_plugin", "skills/plugins/builtin/"),
        ("user", ".agent/skills/"),
        ("third_party", "skills/plugins/external/"),
    ]
    
    def __init__(self):
        self.skills: dict[str, Skill] = {}
    
    def load_all(self, project_root: Path):
        """按优先级加载所有技能（后加载覆盖先加载）"""
        for source_name, source_path in self.SKILL_SOURCES:
            skill_dir = project_root / source_path
            if skill_dir.exists():
                for skill_file in skill_dir.glob("*.md"):
                    skill = self._parse_skill(skill_file, source_name)
                    if skill:
                        # 同名技能：高优先级覆盖低优先级
                        self.skills[skill.metadata.name] = skill
    
    def _parse_skill(self, path: Path, source: str) -> Skill | None:
        """解析技能文件：Frontmatter + 内容"""
        text = path.read_text(encoding="utf-8")
        
        # 解析 YAML Frontmatter
        fm_match = re.match(r'^---\n(.+?)\n---\n(.*)$', text, re.DOTALL)
        if not fm_match:
            return None
        
        fm_data = yaml.safe_load(fm_match.group(1))
        content = fm_match.group(2).strip()
        
        metadata = SkillMetadata(
            name=fm_data.get("name", path.stem),
            description=fm_data.get("description", ""),
            when_to_use=fm_data.get("when_to_use", ""),
            arguments=fm_data.get("arguments", []),
            file_patterns=fm_data.get("file_patterns", []),
        )
        
        return Skill(metadata=metadata, content=content,
                     source=source, file_path=path)
    
    def estimate_tokens(self) -> int:
        """只基于 Frontmatter 估算 Token（不加载完整内容）"""
        total = 0
        for skill in self.skills.values():
            # 粗略估算：4 字符 ≈ 1 Token
            meta_text = f"{skill.metadata.name} {skill.metadata.description} {skill.metadata.when_to_use}"
            total += len(meta_text) // 4
        return total
    
    def get_skill_prompt(self, name: str, **kwargs) -> str:
        """获取技能的完整提示词（支持参数替换和 Shell 命令）"""
        skill = self.skills.get(name)
        if not skill:
            return ""
        
        prompt = skill.content
        
        # 参数替换：{{arg_name}} → 实际值
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        # Shell 命令执行：$(command) → 命令输出
        def execute_shell(match):
            cmd = match.group(1)
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True,
                    text=True, timeout=10
                )
                return result.stdout.strip()
            except Exception:
                return f"[命令执行失败: {cmd}]"
        
        prompt = re.sub(r'\$\((.+?)\)', execute_shell, prompt)
        return prompt
    
    def discover_skills_for_file(self, file_path: str) -> list[Skill]:
        """动态技能发现：根据文件路径匹配相关技能"""
        import fnmatch
        matched = []
        for skill in self.skills.values():
            for pattern in skill.metadata.file_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    matched.append(skill)
                    break
        return matched

# 使用示例
manager = SkillManager()
manager.load_all(Path("."))

# 编辑 React 组件后，自动发现相关技能
related = manager.discover_skills_for_file("src/components/Button.tsx")
for skill in related:
    print(f"发现相关技能: {skill.metadata.name} — {skill.metadata.description}")

# 获取技能提示词（带参数替换）
prompt = manager.get_skill_prompt(
    "code-review",
    language="python",
    file_path="src/main.py"
)
```

**技能文件示例** (`.agent/skills/code-review.md`)：

```markdown
---
name: code-review
description: 对指定文件进行代码审查
when_to_use: 当用户要求 review 代码或提交 PR 前
arguments: [language, file_path]
file_patterns: ["src/**/*.py", "src/**/*.ts"]
---

请对 {{file_path}} 进行代码审查，关注以下方面：

1. **安全性** — 是否有注入、泄露、权限问题
2. **性能** — 是否有 N+1 查询、内存泄漏
3. **可维护性** — 命名、结构、注释是否清晰

当前项目使用的 {{language}} 版本：$(python --version 2>&1)
当前 Git 分支：$(git branch --show-current)
```


## 16. IDE 桥接：从终端到编辑器

> 来源：`bridgeMain.ts` 源码直读

Claude Code 不只是一个终端工具，它通过 Bridge 系统与 VS Code 等 IDE 实现双向通信。这个桥接层的工程复杂度远超预期：

```
Bridge 架构概览：

┌──────────────┐     JWT 认证      ┌──────────────┐
│  Claude Code │ ◄──────────────► │   VS Code    │
│  (终端进程)   │   WebSocket      │  (IDE 插件)   │
└──────┬───────┘                  └──────┬───────┘
       │                                 │
       │  ┌─────────────────────────┐    │
       └──┤  Bridge Server          ├────┘
           │  ├─ 多会话管理 (≤32)    │
           │  ├─ 休眠/唤醒检测       │
           │  ├─ 断线重连 + 退避     │
           │  ├─ 命令白名单          │
           │  └─ 可信设备令牌        │
           └─────────────────────────┘
```

### 16.1 关键工程决策

| 特性 | 实现细节 | 设计原因 |
|------|---------|---------|
| JWT 认证 | `jwtUtils.ts` 签发/验证 | 防止未授权进程连接 Bridge |
| 多会话 | 默认最多 32 个并发会话 | 支持多窗口/多项目同时工作 |
| 休眠检测 | `pollSleepDetectionThresholdMs` | 笔记本合盖后恢复时重建连接 |
| 退避策略 | 初始 2s → 上限 2min → 放弃 10min | 避免网络抖动时疯狂重试 |
| 命令白名单 | 只允许 compact/clear/cost/summary 等 | 防止通过 Bridge 执行危险命令 |
| 可信设备 | `trustedDevice.ts` 令牌机制 | 避免每次连接都要求认证 |
| Git Worktree | `createAgentWorktree` | 子 Agent 在独立工作树中操作 |

### 16.2 为你的 Agent 项目实现 IDE 桥接

```python
"""Agent IDE 桥接 — 基于 WebSocket 的双向通信"""

import json
import asyncio
import hashlib
import hmac
import time
from dataclasses import dataclass, field

@dataclass
class BridgeConfig:
    """桥接配置"""
    max_sessions: int = 32
    jwt_secret: str = ""
    reconnect_initial_ms: int = 2000
    reconnect_max_ms: int = 120_000     # 2 分钟上限
    reconnect_give_up_ms: int = 600_000  # 10 分钟放弃
    safe_commands: list[str] = field(default_factory=lambda: [
        "compact", "clear", "cost", "summary", "status", "files"
    ])

class BridgeSession:
    """单个 IDE 会话"""
    
    def __init__(self, session_id: str, websocket):
        self.session_id = session_id
        self.websocket = websocket
        self.created_at = time.time()
        self.last_heartbeat = time.time()
    
    async def send(self, event_type: str, data: dict):
        """发送事件到 IDE"""
        message = json.dumps({
            "type": event_type,
            "session_id": self.session_id,
            "timestamp": time.time(),
            "data": data,
        })
        await self.websocket.send(message)
    
    async def notify_file_updated(self, file_path: str):
        """通知 IDE 文件已更新（触发编辑器刷新）"""
        await self.send("file_updated", {"path": file_path})
    
    async def notify_diagnostic_clear(self, file_path: str):
        """通知 IDE 清除诊断缓存（编辑后 LSP 需要重新检查）"""
        await self.send("diagnostic_clear", {"path": file_path})

class AgentBridge:
    """
    Agent ↔ IDE 桥接服务器
    
    学自 Claude Code 的设计：
    1. JWT 认证 — 防止未授权连接
    2. 命令白名单 — 只允许安全命令通过桥接执行
    3. 退避重连 — 网络不稳定时优雅降级
    4. 休眠检测 — 系统休眠后自动恢复
    """
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.sessions: dict[str, BridgeSession] = {}
        self._reconnect_delay_ms = config.reconnect_initial_ms
    
    def verify_token(self, token: str) -> bool:
        """验证 JWT Token（简化版）"""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return False
            # 实际项目中使用 PyJWT 库验证
            payload = json.loads(
                __import__('base64').b64decode(parts[1] + "==")
            )
            return payload.get("exp", 0) > time.time()
        except Exception:
            return False
    
    def is_safe_command(self, command: str) -> bool:
        """检查命令是否在白名单中"""
        return command.split()[0] in self.config.safe_commands if command else False
    
    async def handle_connection(self, websocket, token: str):
        """处理新的 IDE 连接"""
        # 1. 认证
        if not self.verify_token(token):
            await websocket.close(4001, "认证失败")
            return
        
        # 2. 检查会话数量限制
        if len(self.sessions) >= self.config.max_sessions:
            await websocket.close(4002, f"会话数已达上限 ({self.config.max_sessions})")
            return
        
        # 3. 创建会话
        session_id = hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16]
        session = BridgeSession(session_id, websocket)
        self.sessions[session_id] = session
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self._handle_message(session, data)
        finally:
            del self.sessions[session_id]
    
    async def _handle_message(self, session: BridgeSession, data: dict):
        """处理来自 IDE 的消息"""
        msg_type = data.get("type")
        
        if msg_type == "heartbeat":
            session.last_heartbeat = time.time()
            await session.send("heartbeat_ack", {})
        
        elif msg_type == "command":
            command = data.get("command", "")
            if self.is_safe_command(command):
                # 只执行白名单命令
                result = await self._execute_safe_command(command)
                await session.send("command_result", {"result": result})
            else:
                await session.send("command_error", {
                    "error": f"命令 '{command}' 不在安全白名单中"
                })
    
    def get_reconnect_delay(self) -> int:
        """指数退避重连延迟"""
        delay = self._reconnect_delay_ms
        self._reconnect_delay_ms = min(
            self._reconnect_delay_ms * 2,
            self.config.reconnect_max_ms
        )
        return delay
    
    def reset_reconnect(self):
        """连接成功后重置退避"""
        self._reconnect_delay_ms = self.config.reconnect_initial_ms
    
    def detect_sleep_wake(self, last_poll_time: float, threshold_ms: int = 5000) -> bool:
        """检测系统是否经历了休眠/唤醒"""
        elapsed = (time.time() - last_poll_time) * 1000
        return elapsed > threshold_ms
```


## 17. 文件编辑的 12 项安全检查

> 来源：`FileEditTool.ts` 源码直读

文件编辑是 Agent 最常用也最危险的操作。Claude Code 的 `FileEditTool` 在每次编辑前后执行了 12 项检查，远不只是"写文件"这么简单：

```
文件编辑生命周期：

编辑请求 → [前置检查 6 项] → 执行编辑 → [后置处理 6 项] → 完成

前置检查：                          后置处理：
├─ ① 文件大小限制 (1 GiB)          ├─ ⑦ 条件技能激活
├─ ② 意外修改检测                   ├─ ⑧ VS Code 通知
├─ ③ 团队记忆密钥扫描               ├─ ⑨ LSP 诊断缓存清除
├─ ④ 设置文件编辑验证               ├─ ⑩ 文件历史追踪
├─ ⑤ 引用样式保留                   ├─ ⑪ 相似文件建议
└─ ⑥ 文件存在性检查                 └─ ⑫ 编辑结果验证
```

### 17.1 每项检查的详细说明

| # | 检查项 | 说明 | 失败时行为 |
|---|--------|------|-----------|
| ① | 文件大小限制 | `MAX_EDIT_FILE_SIZE = 1 GiB` | 拒绝编辑，提示文件过大 |
| ② | 意外修改检测 | 编辑前记录文件哈希，执行时对比 | 报错 `FILE_UNEXPECTEDLY_MODIFIED_ERROR` |
| ③ | 密钥扫描 | `checkTeamMemSecrets` 扫描敏感前缀 | 阻止写入团队记忆文件 |
| ④ | 设置文件验证 | `validateInputForSettingsFileEdit` | 阻止修改关键配置文件 |
| ⑤ | 引用样式保留 | `preserveQuoteStyle` 保持单/双引号一致 | 自动修正引用样式 |
| ⑥ | 文件存在性 | 检查目标文件是否存在 | `findSimilarFile` 建议相似文件 |
| ⑦ | 条件技能激活 | `activateConditionalSkillsForPaths` | 编辑后自动加载相关技能 |
| ⑧ | VS Code 通知 | `notifyVscodeFileUpdated` | 触发编辑器刷新文件内容 |
| ⑨ | LSP 缓存清除 | `clearDeliveredDiagnosticsForFile` | 清除旧的诊断信息 |
| ⑩ | 文件历史 | `fileHistoryTrackEdit` | 记录编辑历史（可回滚） |
| ⑪ | 相似文件建议 | 文件不存在时搜索相似路径 | 返回建议路径列表 |
| ⑫ | 编辑验证 | 验证编辑结果是否符合预期 | 报告编辑异常 |

### 17.2 为你的 Agent 项目实现安全文件编辑

```python
"""Agent 安全文件编辑 — 12 项检查的 Python 实现"""

import hashlib
import os
import re
import difflib
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

@dataclass
class EditResult:
    success: bool
    message: str
    file_path: str
    diff: str = ""

class SafeFileEditor:
    """
    安全文件编辑器（学自 Claude Code FileEditTool）
    
    核心原则：
    - 编辑前：验证安全性和一致性
    - 编辑后：通知相关系统并记录历史
    - 失败时：提供可操作的错误信息
    """
    
    MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1 GiB
    SECRET_PATTERNS = [
        r'(?:api[_-]?key|secret|token|password)\s*[=:]\s*["\']?[\w\-]{20,}',
        r'(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}',  # AWS Access Key
        r'sk-[a-zA-Z0-9]{20,}',                    # OpenAI API Key
        r'ghp_[a-zA-Z0-9]{36}',                    # GitHub Token
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_hashes: dict[str, str] = {}  # 文件哈希缓存
        self.edit_history: list[dict] = []
        self.post_edit_hooks: list[Callable] = []
    
    def _hash_file(self, path: Path) -> str:
        """计算文件哈希"""
        if not path.exists():
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()
    
    # ===== 前置检查 =====
    
    def _check_file_size(self, path: Path) -> EditResult | None:
        """① 文件大小限制"""
        if path.exists() and path.stat().st_size > self.MAX_FILE_SIZE:
            return EditResult(False, f"文件超过大小限制 (1 GiB): {path}", str(path))
        return None
    
    def _check_unexpected_modification(self, path: Path) -> EditResult | None:
        """② 意外修改检测"""
        str_path = str(path)
        if str_path in self.file_hashes:
            current_hash = self._hash_file(path)
            if current_hash != self.file_hashes[str_path]:
                return EditResult(
                    False,
                    f"文件在上次读取后被外部修改: {path}\n"
                    f"预期哈希: {self.file_hashes[str_path][:12]}...\n"
                    f"当前哈希: {current_hash[:12]}...\n"
                    f"请重新读取文件后再编辑。",
                    str_path
                )
        return None
    
    def _check_secrets(self, content: str, path: Path) -> EditResult | None:
        """③ 团队记忆密钥扫描"""
        # 只对团队共享文件检查
        if ".agent/team" in str(path) or "CLAUDE.md" in str(path):
            for pattern in self.SECRET_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    return EditResult(
                        False,
                        f"检测到潜在密钥，不能写入共享文件: {path}\n"
                        f"匹配模式: {pattern}\n"
                        f"请移除敏感内容后重试。",
                        str(path)
                    )
        return None
    
    def _check_settings_file(self, path: Path) -> EditResult | None:
        """④ 设置文件编辑验证"""
        protected = [".env", ".env.local", "settings.json", "permissions.json"]
        if path.name in protected:
            return EditResult(
                False,
                f"受保护的设置文件不能直接编辑: {path.name}\n"
                f"请使用专用的配置命令修改此文件。",
                str(path)
            )
        return None
    
    def _find_similar_file(self, path: Path) -> list[str]:
        """⑥⑪ 文件不存在时查找相似文件"""
        if path.exists():
            return []
        
        all_files = [str(p.relative_to(self.project_root))
                     for p in self.project_root.rglob("*") if p.is_file()]
        target = str(path.relative_to(self.project_root))
        
        # 使用 difflib 查找相似路径
        similar = difflib.get_close_matches(target, all_files, n=3, cutoff=0.6)
        return similar
    
    # ===== 核心编辑 =====
    
    def edit_file(self, path: Path, new_content: str) -> EditResult:
        """安全编辑文件（包含所有前置检查和后置处理）"""
        
        # === 前置检查 ===
        for check in [
            self._check_file_size,
            self._check_unexpected_modification,
            self._check_settings_file,
        ]:
            error = check(path)
            if error:
                return error
        
        # ③ 密钥扫描
        secret_error = self._check_secrets(new_content, path)
        if secret_error:
            return secret_error
        
        # ⑥ 文件存在性检查
        if not path.exists():
            similar = self._find_similar_file(path)
            if similar:
                return EditResult(
                    False,
                    f"文件不存在: {path}\n你是否想编辑以下文件？\n"
                    + "\n".join(f"  - {s}" for s in similar),
                    str(path)
                )
        
        # ⑤ 读取旧内容（用于 diff 和引用样式保留）
        old_content = path.read_text(encoding="utf-8") if path.exists() else ""
        
        # 引用样式保留：如果旧文件用单引号，新内容也用单引号
        if old_content and "'" in old_content and '"' not in old_content:
            new_content = new_content.replace('"', "'")
        
        # === 执行编辑 ===
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_content, encoding="utf-8")
        
        # 生成 diff
        diff = "\n".join(difflib.unified_diff(
            old_content.splitlines(), new_content.splitlines(),
            fromfile=f"a/{path}", tofile=f"b/{path}", lineterm=""
        ))
        
        # === 后置处理 ===
        
        # ⑩ 文件历史追踪
        self.edit_history.append({
            "path": str(path),
            "old_hash": self.file_hashes.get(str(path), ""),
            "new_hash": self._hash_file(path),
            "diff_lines": len(diff.splitlines()),
        })
        
        # 更新哈希缓存
        self.file_hashes[str(path)] = self._hash_file(path)
        
        # ⑦⑧⑨ 触发后置 Hook（技能激活、IDE 通知、LSP 清除）
        for hook in self.post_edit_hooks:
            hook(str(path))
        
        return EditResult(True, f"文件编辑成功: {path}", str(path), diff)

# 使用示例
editor = SafeFileEditor(Path("."))

# 注册后置 Hook
editor.post_edit_hooks.append(
    lambda path: print(f"[Hook] 通知 IDE 刷新: {path}")
)
editor.post_edit_hooks.append(
    lambda path: print(f"[Hook] 清除 LSP 诊断缓存: {path}")
)

# 安全编辑
result = editor.edit_file(
    Path("src/main.py"),
    'print("Hello, Agent!")\n'
)
print(f"编辑结果: {result.success} — {result.message}")
```

**核心教训：** 文件编辑工具不只是 `open().write()`。生产级 Agent 需要在编辑前验证安全性和一致性，编辑后通知所有相关系统。Claude Code 的 12 项检查是经过真实用户场景打磨出来的，每一项都对应一个曾经出过的 Bug。


## 17. Claude Code 2026 版本演进

> 🔄 更新于 2026-05-02

Claude Code 从 v2.1.101（第 11 次更新记录）到 v2.1.118 经历了密集迭代，产品形态从终端工具扩展为多平台 Agent 系统。来源：[Claude Code Changelog](https://code.claude.com/docs/en/changelog)、[Releasebot](https://releasebot.io/updates/anthropic/claude-code)

### 17.1 v2.1.101 → v2.1.118 关键变化

| 版本范围 | 核心变化 |
|---------|---------|
| v2.1.105~108 | 持久化配置设置、MCP 连接器增强、权限系统改进 |
| v2.1.109~112 | Hooks 系统增强、PR 工作流改进、可观测性（OTel 事件） |
| v2.1.113~116 | `claude project purge` 命令、Auto Mode 权限卡住红色提示、Windows PowerShell 7 检测 |
| v2.1.117~118 | `--dangerously-skip-permissions` 扩展、OAuth 登录改进、图片粘贴修复、流空闲超时修复 |

### 17.2 Claude Code Desktop

Claude Code 已从纯终端工具扩展为桌面应用，支持：
- **可视化 Diff 审查** — 直接在桌面应用中查看代码变更
- **应用预览** — 内置预览服务器
- **会话管理** — 并行会话、后台任务监控
- **Computer Use（预览）** — Agent 可以操作桌面应用
- **Chrome 扩展（Beta）** — 浏览器集成
- **Scheduled Tasks** — 定时任务执行

来源：[Claude Code Desktop](https://code.claude.com/docs/en/desktop)

### 17.3 Agent Teams 与 Managed Agents

Claude Code 的多 Agent 架构已公开：
- **Forked Subagents** — `CLAUDE_CODE_FORK_SUBAGENT=1` 启用外部构建的分叉子 Agent
- **Agent Teams** — peer-to-peer 邮箱通信架构，多 Agent 并行协作
- **Managed Agents** — Anthropic 托管的 Agent 运行时（公开 Beta）

来源：[Anthropic Engineering - Managed Agents](https://www.anthropic.com/engineering/managed-agents)

### 17.4 架构启示更新

Claude Code 2026 年的演进揭示了 Coding Agent 的发展方向：

```
2025 年 Agent 架构：
├─ 终端 CLI → 单一入口
├─ 单 Agent → 线性执行
└─ 本地运行 → 开发者机器

2026 年 Agent 架构：
├─ 多平台（CLI + Desktop + Web + IDE + Slack）→ 统一 Agent 核心
├─ Agent Teams → 并行协作 + 文件系统通信
├─ 混合运行（本地 + 云端 Ultraplan + 远程会话）→ 弹性计算
├─ 有状态续传 → 会话分叉、断点恢复
└─ 可观测性（OTel 事件）→ 企业级监控
```

### 17.5 对本文架构建议的影响

本文第 6 节的多 Agent 编排模式仍然准确，但需要补充：

1. **文件系统通信仍是核心** — Agent Teams 使用邮箱文件（inbox.jsonl）通信，验证了本文第 6.2 节的设计
2. **有状态续传成为标准** — 会话可以分叉、恢复、远程继续，本文第 5 节的上下文管理需要考虑持久化到远程存储
3. **权限系统持续演进** — `--dangerously-skip-permissions` 的扩展说明安全和便利的平衡仍在调整
4. **可观测性从可选变为必需** — OTel 事件（`claude_code.skill_activated` 等）表明生产级 Agent 必须有结构化追踪


## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Writing Effective Tools for AI Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — Anthropic 官方工具设计指南（必读）
- [Anthropic - How We Built Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) — 多 Agent 系统构建
- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI 完整课程（免费）
- [PromptLayer - Claude Code Agent Loop](https://blog.promptlayer.com/claude-code-behind-the-scenes-of-the-master-agent-loop/) — Agent 主循环解析

### 📺 B站
- [李沐 - 动手学深度学习](https://www.bilibili.com/video/BV1if4y147hS) — AI 工程基础
- [AI Agent 开发实战](https://www.bilibili.com/video/BV1Bm421N7BH) — Agent 开发中文教程

### 📖 参考资料
- [Anthropic - Writing Tools for Agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — 工具设计原则（本文主要参考）
- [Building Production-Grade AI Agents](https://pub.towardsai.net/building-production-grade-ai-agents-in-2025-the-complete-technical-guide-9f02eff84ea2) — 生产级 Agent 技术指南
- [Claude Code 架构深度解析](../17-Coding%20Agent/02-Claude%20Code架构深度解析.md) — 源码泄露分析
- [15 Hard-Earned Lessons to Ship AI Agents](https://medium.com/data-science-collective/beyond-the-prototype-15-hard-earned-lessons-to-ship-production-ready-ai-agents-e58139d80299) — 15 条实战教训
- [Portkey - Scaling Claude Code Agents](https://portkey.ai/blog/claude-code-agents/) — 团队级 Agent 扩展
