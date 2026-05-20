# Agent OS 生态
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 什么是 Agent OS

Agent OS 为 AI Agent 提供类似操作系统的运行环境：技能管理、任务调度、记忆、通信渠道。

```
传统 OS              Agent OS
┌────────────────┐  ┌────────────────┐
│ 应用程序        │  │ Skills（技能）  │
│ 系统调用        │  │ 工具调用（MCP） │
│ 进程调度        │  │ 任务调度/循环   │
│ 文件系统        │  │ 记忆系统        │
│ 网络/IO         │  │ 渠道/通信       │
│ 硬件抽象        │  │ LLM 抽象        │
└────────────────┘  └────────────────┘
```

## 2. OpenClaw — 全功能个人助手 OS

最成熟的 Agent OS，详见 → [OpenClaw平台详解](./03-OpenClaw平台详解.md)

```
核心：Skills 系统 + 20+ 消息渠道 + Heartbeat 定时 + Memory + Sub-Agents
```

## 3. ZeroClaw — 轻量级 Agent OS

OpenClaw 精简版，保留核心功能，去除平台级开销。

```bash
# 最小配置启动（秒级）
cat > config.yaml << EOF
model: gpt-5-mini  # 修复于 2026-05-20: gpt-4o-mini 已退役，改为 gpt-5-mini
skills: [general-chat, file-manager]
memory:
  type: sqlite
  path: ./data/memory.db
EOF

python -m zeroclaw --config config.yaml
zeroclaw chat "帮我整理下载文件夹"
```

```
设计哲学：启动 < 2s，内存 < 128MB，核心功能，无 Heartbeat
```

## 4. OpenFang — 自主任务 Agent OS

核心理念：给定任务，Agent 持续执行直到输出满足预期（黑盒自主循环）。

```
OpenFang 自主循环：

  输入：任务 + 验收标准
       ↓
  ┌──────────┐
  │ Agent 执行│ ← 读取任务和约束
  └────┬─────┘
       ↓
  ┌──────────┐    ┌──────────┐
  │ 验证输出  │──→│ 满足预期？│── 是 → 完成
  └──────────┘    └────┬─────┘
                       │ 否
                  ┌────┴─────┐
                  │ 分析差距  │
                  │ 自动修正  │ → 回到执行
                  └──────────┘
  退出：全部通过 / 超过 N 次 / 不可恢复错误
```

```python
from openfang import TaskAgent

# 修复于 2026-05-20: gpt-4o → gpt-5.2
agent = TaskAgent(model="gpt-5.2", max_retries=5)

result = agent.run(
    task="创建 Python REST API，包含用户 CRUD",
    acceptance_criteria=[
        "所有端点返回正确 HTTP 状态码",
        "包含输入验证",
        "单元测试全部通过",
        "代码通过 ruff 检查",
    ],
    workspace="./output/api-project",
)
print(result.status)      # "completed" | "failed"
print(result.iterations)  # 执行了几轮
```

```
与 Harness Engineering 的关系：
  Harness Eng. 定义了"自主循环"方法论
  OpenFang 是这个方法论的开源实现
```

## 5. 三大 Agent OS 对比

| 特性 | OpenClaw | ZeroClaw | OpenFang |
|------|----------|----------|----------|
| 定位 | 全功能个人助手 | 轻量级 Agent OS | 自主任务执行 |
| 核心模式 | 对话式交互 | 对话式交互 | 任务驱动循环 |
| Skills 系统 | ✅ 完整 + 市场 | ✅ 基础 | ❌ 任务导向 |
| 消息渠道 | 20+ | CLI/API | CLI/API |
| 记忆系统 | 完整 | 基础键值 | 任务上下文 |
| 自主循环 | ❌ | ❌ | ✅ 核心特性 |
| 启动时间 | 10-30s | < 2s | < 5s |
| 内存占用 | 512MB+ | < 128MB | 256MB |
| 适用场景 | 日常助手 | 嵌入式/边缘 | 代码生成/自动化 |

## 6. Agent OS vs Agent 框架

```
Agent 框架（LangGraph/CrewAI）：构建 Agent 的编程接口 → 类比"编程语言"
Agent OS（OpenClaw/OpenFang）：运行 Agent 的完整环境 → 类比"操作系统"

  ┌─────────────────────────┐
  │      Agent OS            │
  │  ┌───────────────────┐  │
  │  │   Agent 框架       │  │
  │  │  ┌─────────────┐  │  │
  │  │  │   LLM 模型   │  │  │
  │  │  └─────────────┘  │  │
  │  └───────────────────┘  │
  │  + 渠道 + 记忆 + 调度   │
  └─────────────────────────┘
```

## 7. 选型建议

```
├─ 多渠道日常助手（WhatsApp/Slack）→ OpenClaw
├─ 轻量 CLI/API Agent            → ZeroClaw
├─ 自主循环任务执行               → OpenFang
├─ 自定义 Agent 应用              → 用框架自己搭建
└─ 不确定？ → ZeroClaw 开始，按需升级
```
## 🎬 推荐视频资源

### 📖 官方文档
- [OpenClaw GitHub](https://github.com/openclaw/openclaw) — OpenClaw AgentOS
- [OpenFang GitHub](https://github.com/RightNow-AI/openfang) — OpenFang运行时
