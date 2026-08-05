# Agent 成本优化工程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 基于 Claude Code 源码分析（promptCacheBreakDetection.ts、cost-tracker.ts、tools.ts、autoCompact.ts 等）
> 从生产级 Coding Agent 中提炼的成本工程实践

<!-- version-check: Claude Opus 4.8 / Sonnet 5 / Haiku 4.5 当前定价（2026-07），文中架构分析基于 2025-07 历史定价快照，checked 2026-07-10 -->

## 1. 成本优化全景 — Cache Miss = 10x 成本

对 AI Agent 产品来说，**模型推理本身可能不是最贵的部分 — 失败的缓存管理才是**。一次缓存未命中意味着相同 Token 以 10 倍价格重新处理，延迟从毫秒级跳到秒级。

```
成本优化三层模型：
┌──────────────────────────────────────────┐
│  Level 3: 架构级 — 子Agent缓存共享、模型路由、压缩策略  │
├──────────────────────────────────────────┤
│  Level 2: 协议级 — Cache稳定性、工具池排序、cache_edits │
├──────────────────────────────────────────┤
│  Level 1: 运营级 — 成本追踪、异常检测、熔断机制        │
└──────────────────────────────────────────┘
```

**Claude Code 的 250K 浪费 API 调用教训**（autoCompact.ts 注释，2026-03-10）：

```typescript
// "1,279 个会话有 50+ 次连续自动压缩失败（最多 3,272 次），
//  全球每天浪费约 250,000 次 API 调用"
// 修复：
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3;
// 三行代码，每天节省 25 万次 API 调用
```

根因：自动压缩触发 → 失败 → 下一轮继续触发 → 继续失败 → 无限循环。**教训：任何自动化流程都需要熔断机制。**

---

## 2. Prompt Cache 经济学

### 2.1 定价层级（2025 年 7 月，历史快照，用于还原 Claude Code 源码分析时的成本模型）

| 模型 | 标准输入 | 缓存写入 | **缓存读取** | 输出 |
|------|---------|---------|-------------|------|
| Haiku 3.5 | $0.80/M | $1.00/M | **$0.08/M** | $4.00/M |
| Sonnet 4 | $3.00/M | $3.75/M | **$0.30/M** | $15.00/M |
| Opus 4 | $15.00/M | $18.75/M | **$1.50/M** | $75.00/M |

缓存读取只需标准输入价格的 **10%**（现行模型缓存读取折扣已提升至 **90%**，即缓存读取价格仅为标准输入价格的 10%——折扣比例表述不变，但新模型基础价格已大幅下调，见下方"当前定价"）。50K Token 系统提示，10 轮对话缓存命中可节省 $6.75（Opus 4，历史价格）。

<!-- 修复于 2026-07-10: 补充当前（2026-07）实际定价，避免读者误用 2025-07 历史价格做生产成本估算 -->

> 🔄 **当前定价（2026-07，来自 Anthropic 官方定价页）**：Claude 模型线已演进为 **Opus 4.8**（$5/M 输入、$25/M 输出）、**Sonnet 5**（介绍价 $2/M 输入、$10/M 输出，2026-08-31 前；此后 $3/M 输入、$15/M 输出）、**Haiku 4.5**（$1/M 输入、$5/M 输出）。相比本节的 2025-07 历史价格，Opus 系列输出价格从 $75/M 降到 $25/M（降幅 67%），缓存读取折扣统一提升到 90%。本节后续的架构分析（cache_edits、sticky latches、熔断机制等）仍完全适用，只是价格数字为历史快照。

### 2.2 14 种缓存失效向量

`promptCacheBreakDetection.ts` 追踪了 14 种导致 Prompt Cache 失效的情况：

```
类别 1 — 系统提示变更：模式切换、CLAUDE.md 修改、权限规则变更、特性开关变化
类别 2 — 工具定义变更：MCP 工具增删、Schema 更新、工具排序变化
类别 3 — 上下文变更：消息压缩/截断、消息删除（非 cache_edits）、系统消息注入
类别 4 — 会话状态变更：会话恢复、用户切换、API 端点变更、模型版本切换
```

### 2.3 Sticky Latches 机制

防止频繁模式切换破坏缓存的"粘性锁存"：

```typescript
// 一旦系统提示段被缓存，即使条件变化也不立即更新
class StickyLatch {
  private cachedValue: string;
  private latchedAt: number;
  private minLatchDuration = 300_000; // 5 分钟

  update(newValue: string): string {
    if (Date.now() - this.latchedAt < this.minLatchDuration) {
      return this.cachedValue; // 保持旧值，保护缓存
    }
    this.cachedValue = newValue;
    this.latchedAt = Date.now();
    return newValue;
  }
}
// 源码中 DANGEROUS_uncachedSystemPromptSection() 标记不参与缓存的动态段
```

**设计原则：** 系统提示分为"稳定段"（参与缓存）和"动态段"（标记为 uncached），频繁变化的内容不拖垮整个缓存。

---

## 3. cache_edits 机制 — 长会话不变慢的秘密

传统做法删除旧消息会破坏缓存连续性。Claude Code 的方案：**标记为 "skip" 而非删除**。

```
传统做法：删除 M2,M3 → 缓存前缀从 [M1..M8] 变为 [M1] → 6 条消息缓存失效
cache_edits：标记 M2,M3 为 skip → 缓存前缀仍为 [M1..M8] → 全部命中
```

```typescript
function applyMicrocompact(messages: Message[]): CacheEditMessage[] {
  return messages.map((msg, index) => {
    if (isOldToolResult(msg) && index < messages.length - 10) {
      return { ...msg, content: '', cache_edit: 'skip' }; // 清空内容但保留位置
    }
    return msg;
  });
}
```

**核心洞察：** 清除数百条旧消息后，下一轮响应速度几乎和第一轮一样快。这是 Claude Code 支持数小时长会话的关键。

---

## 4. 工具池排序与缓存稳定性

### 4.1 问题与方案

新增 MCP 工具时，如果混合排序会插入内置工具之间，导致所有下游缓存失效：

```
混合排序：新增 DbQuery 插入 → [AgentTool, BashTool, DbQuery↑, FileEdit...] → 只有 2 个缓存命中
分区排序：新增追加在后 → [AgentTool, BashTool, FileEdit... | DbQuery↑] → 内置全部命中
```

### 4.2 assembleToolPool() 源码

```typescript
// tools.ts — 内置工具作为缓存前缀，MCP 工具追加在后
return uniqBy(
  [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
  'name',
);
// 服务端 claude_code_system_cache_policy 在最后一个内置工具后设置缓存断点
```

```python
# Python 实现
def assemble_tool_pool(builtin_tools, mcp_tools):
    sorted_builtin = sorted(builtin_tools, key=lambda t: t['name'])
    builtin_names = {t['name'] for t in sorted_builtin}
    sorted_mcp = sorted(
        [t for t in mcp_tools if t['name'] not in builtin_names],
        key=lambda t: t['name']
    )
    return sorted_builtin + sorted_mcp  # 内置前缀 + MCP 后缀
```

---

## 5. 模型路由策略

### 5.1 成本对比（历史价格，2025-07 快照）

| 模型 | 输入 | 缓存读取 | 输出 | 适用场景 | 相对成本 |
|------|------|---------|------|---------|---------|
| Haiku 3.5 | $0.80/M | $0.08/M | $4.00/M | 分类、格式化 | 1x |
| Sonnet 4 | $3.00/M | $0.30/M | $15.00/M | 代码编写 | 3.75x |
| Opus 4 | $15.00/M | $1.50/M | $75.00/M | 架构设计 | 18.75x |

Opus 输出价格是 Haiku 的 **18.75 倍**（历史价格下的倍数）。简单任务用 Opus = 用跑车送外卖——这个类比至今仍成立。

> 🔄 **当前定价（2026-07）**：Haiku 4.5 $1/$5、Sonnet 5 $2/$10（介绍价，8 月底后 $3/$15）、Opus 4.8 $5/$25（单位均为每 M Token）。Opus 相对 Haiku 输出价格倍数从 18.75x 收窄到 **5x**，说明"简单任务用小模型"的分级路由策略收益比例在变化，但架构模式本身（按任务复杂度路由）依然是正确的成本优化方向。

### 5.2 路由实现

```python
from enum import Enum

class TaskComplexity(Enum):
    SIMPLE = "simple"      # 格式化、重命名、简单查询 → Haiku
    STANDARD = "standard"  # 代码编写、Bug 修复 → Sonnet
    COMPLEX = "complex"    # 架构设计、多文件重构 → Opus

MODEL_MAP = {
    TaskComplexity.SIMPLE: "claude-3-5-haiku-20241022",
    TaskComplexity.STANDARD: "claude-sonnet-4-6-20260217",
    TaskComplexity.COMPLEX: "claude-opus-4-20250918",
}

def classify_task(user_input: str) -> TaskComplexity:
    simple_patterns = ["rename", "format", "what is", "list"]
    complex_patterns = ["refactor", "architect", "security audit", "redesign"]
    input_lower = user_input.lower()
    if any(p in input_lower for p in simple_patterns):
        return TaskComplexity.SIMPLE
    if any(p in input_lower for p in complex_patterns):
        return TaskComplexity.COMPLEX
    return TaskComplexity.STANDARD
```

Claude Code 中的多层路由：主对话用 Sonnet/Opus，YOLO 分类器用轻量模型，Advisor 模型单独追踪，Fast 模式用 `speed: 'fast'` 标记。

---

## 6. 上下文压缩的成本影响

### 6.1 五种策略对比

| 策略 | 触发方式 | 缓存影响 | 成本节省 | 信息损失 |
|------|---------|---------|---------|---------|
| **Microcompact** | 持续运行 | ✅ 无（cache_edits） | ⭐⭐⭐⭐⭐ | 低 |
| Context Collapse | 上下文 >70% | ⚠️ 部分失效 | ⭐⭐⭐⭐ | 中 |
| Session Memory | 主动触发 | ✅ 无（写入文件） | ⭐⭐⭐ | 低 |
| Full Compact | /compact 命令 | ❌ 完全失效 | ⭐⭐ | 高 |
| PTL Truncation | 最后手段 | ❌ 完全失效 | ⭐ | 极高 |

### 6.2 为什么 Microcompact 成本最优

1. **持续运行** — 不等上下文溢出才触发
2. **不破坏缓存** — 使用 cache_edits 标记删除
3. **低信息损失** — 只清除旧工具调用结果，保留决策
4. **零额外 API 调用** — 纯本地操作，不需要 LLM 做摘要

Full Compact 的隐藏成本：摘要生成（一次完整 LLM 调用）+ 缓存重建（全量输入价格）。100K Token 历史的 Full Compact 额外成本约 $0.45（Sonnet），而 Microcompact 额外成本 = $0。

---

## 7. 子 Agent 成本优化

### 7.1 Fork = 字节级副本 = 共享缓存 = 近零边际成本

```
传统方案（3 个独立 Worker）：
  每个 Worker: [System+Tools 30K] + [Task 2K] = 32K × 标准价格
  总成本 = 3 × 32K × $3/M = $0.288

Fork 方案（3 个 Fork Worker）：
  每个 Worker: [30K 缓存命中] + [20K 缓存命中] + [2K 新增]
  总成本 = 3 × (50K×$0.3/M + 2K×$3/M) = $0.063

  节省 78%
```

原理：Prompt Cache 基于前缀字节匹配。Fork 创建父上下文的字节级副本，前缀完全相同，直接命中父缓存。

### 7.2 Worker 工具集限制

```typescript
// coordinatorMode.ts — Worker 工具集受限
const ASYNC_AGENT_ALLOWED_TOOLS = [
  'BashTool', 'FileReadTool', 'FileEditTool',
  'FileWriteTool', 'GlobTool', 'GrepTool',
  // 没有 AgentTool（不能再生成子 Agent）
  // 没有 TeamCreateTool（不能管理团队）
];
// 更少工具 = 更短工具定义 = 更少输入 Token = 更低成本
```

---

## 8. 成本追踪系统

### 8.1 cost-tracker.ts 追踪维度

```
Token 追踪：输入Token、输出Token、缓存读取、缓存写入、按模型分类
请求追踪：Web搜索次数、API调用次数、工具调用次数
会话追踪：成本持久化、会话恢复时恢复成本状态、历史查询
性能追踪：FPS指标、代码行变更、Advisor模型用量
导出：OpenTelemetry 集成（getCostCounter / getTokenCounter）
```

### 8.2 Python 实现

```python
from dataclasses import dataclass, field
from typing import Dict
import json, time
from pathlib import Path

@dataclass
class ModelUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0

@dataclass
class CostTracker:
    session_id: str
    start_time: float = field(default_factory=time.time)
    usage_by_model: Dict[str, ModelUsage] = field(default_factory=dict)
    api_calls: int = 0
    
    PRICING = {
        "claude-sonnet-4": {"input": 3.0, "output": 15.0, "cache_read": 0.3, "cache_write": 3.75},
        "claude-opus-4": {"input": 15.0, "output": 75.0, "cache_read": 1.5, "cache_write": 18.75},
        "claude-3-5-haiku": {"input": 0.8, "output": 4.0, "cache_read": 0.08, "cache_write": 1.0},
    }
    
    def record_usage(self, model: str, usage: dict):
        if model not in self.usage_by_model:
            self.usage_by_model[model] = ModelUsage()
        mu = self.usage_by_model[model]
        mu.input_tokens += usage.get("input_tokens", 0)
        mu.output_tokens += usage.get("output_tokens", 0)
        mu.cache_read_tokens += usage.get("cache_read_input_tokens", 0)
        mu.cache_creation_tokens += usage.get("cache_creation_input_tokens", 0)
        self.api_calls += 1
    
    def get_total_cost(self) -> float:
        total = 0.0
        for model, usage in self.usage_by_model.items():
            p = self.PRICING.get(model, self.PRICING["claude-sonnet-4"])
            total += usage.input_tokens * p["input"] / 1_000_000
            total += usage.output_tokens * p["output"] / 1_000_000
            total += usage.cache_read_tokens * p["cache_read"] / 1_000_000
            total += usage.cache_creation_tokens * p["cache_write"] / 1_000_000
        return total
    
    def get_cache_hit_rate(self) -> float:
        total = sum(u.input_tokens + u.cache_read_tokens for u in self.usage_by_model.values())
        cached = sum(u.cache_read_tokens for u in self.usage_by_model.values())
        return cached / total if total > 0 else 0.0
    
    def save(self, output_dir=".agent/sessions"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / f"{self.session_id}.json").write_text(json.dumps({
            "session_id": self.session_id, "total_cost": self.get_total_cost(),
            "cache_hit_rate": self.get_cache_hit_rate(), "api_calls": self.api_calls,
            "usage_by_model": {m: vars(u) for m, u in self.usage_by_model.items()},
        }, indent=2))
```

---

## 9. 成本异常检测与熔断

### 9.1 熔断模式

```typescript
// autoCompact.ts — 经典熔断
const MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3;
let consecutiveFailures = 0;

async function autoCompact(messages) {
  if (consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
    console.warn('Auto-compact disabled. Use /compact to manually trigger.');
    return messages;
  }
  try {
    const result = await performCompaction(messages);
    consecutiveFailures = 0;
    return result;
  } catch {
    consecutiveFailures++;
    return messages;
  }
}
```

### 9.2 通用成本熔断器

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # 正常
    OPEN = "open"           # 熔断
    HALF_OPEN = "half_open" # 试探恢复

class CostCircuitBreaker:
    def __init__(self, max_failures=3, max_session_cost=10.0, recovery_timeout=300):
        self.max_failures = max_failures
        self.max_session_cost = max_session_cost
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.session_cost = 0.0
        self.last_failure = 0.0
    
    def can_proceed(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True  # HALF_OPEN: 允许一次试探
    
    def record_success(self, cost: float):
        self.session_cost += cost
        self.failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
        if self.session_cost >= self.max_session_cost:
            self.state = CircuitState.OPEN
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.max_failures:
            self.state = CircuitState.OPEN
```

### 9.3 告警矩阵

| 异常类型 | 检测方式 | 级别 | 自动响应 |
|---------|---------|------|---------|
| 连续压缩失败 | 计数器 ≥ 3 | 🟡 | 停止自动压缩 |
| 单次成本超限 | 预估 > $1 | 🔴 | 熔断，要求确认 |
| 会话成本超限 | 累计 > $10 | 🔴 | 熔断，建议新建会话 |
| 缓存命中率骤降 | >50% 降到 <10% | 🟡 | 告警，检查配置 |
| API 调用频率异常 | >10 次/分钟 | 🟡 | 限流，检查循环 |

---

## 10. 生产成本优化检查清单

```
□ Prompt Cache
  □ 系统提示分稳定段/动态段，动态段标记 uncached
  □ 工具定义分区排序（内置前缀 + MCP 后缀）
  □ 实现 sticky latches 防频繁模式切换
  □ 验证缓存命中率 > 60%

□ 上下文管理
  □ 启用 Microcompact（持续运行 + cache_edits）
  □ 配置 Context Collapse 阈值（70%）和 Full Compact 阈值（85%）
  □ 使用 cache_edits 标记删除而非真删除

□ 模型路由
  □ 简单任务 → Haiku，标准 → Sonnet，复杂 → Opus
  □ 分类器准确率定期审查

□ 子 Agent
  □ Fork 模式共享父缓存
  □ Worker 工具集最小化
  □ 子 Agent 成本独立追踪

□ 熔断与监控
  □ 自动压缩失败熔断（MAX_FAILURES = 3）
  □ 单次/会话成本上限
  □ 缓存命中率骤降告警
  □ OpenTelemetry 成本指标导出
```

---

## 🎬 推荐视频资源

### 🌐 YouTube
- [Matthew Berman - Claude Code Leak Analysis](https://www.youtube.com/watch?v=hkhDdcM5V94) — 包含成本优化相关的架构分析
- [AI Engineer - LLM Cost Optimization](https://www.youtube.com/results?search_query=llm+cost+optimization+engineering) — LLM 成本优化工程实践

### 📺 B站
- [Claude Code 源码泄露分析](https://www.bilibili.com/video/BV1Bm421N7BH) — 中文架构分析，包含缓存经济学部分

### 📖 参考资料
- [Anthropic Pricing](https://www.anthropic.com/pricing) — Claude 模型最新定价
- [Anthropic Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — Prompt Cache 官方文档
- [alex000kim - Claude Code Source Analysis](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) — 源码分析（成本相关发现）
- [PromptLayer - Claude Code Agent Loop](https://blog.promptlayer.com/claude-code-behind-the-scenes-of-the-master-agent-loop/) — Agent 主循环与成本控制
- [Claude Code Camp - Agent Teams](https://www.claudecodecamp.com/p/claude-code-agent-teams-how-they-work-under-the-hood) — 多 Agent 缓存共享机制
- [GitHub Archive](https://github.com/walterwang0x01/claude-code) — 源码存档（教育研究用途）
