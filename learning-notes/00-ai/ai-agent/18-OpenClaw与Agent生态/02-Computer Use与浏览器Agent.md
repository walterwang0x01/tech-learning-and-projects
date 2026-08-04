# Computer Use 与浏览器 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Computer Use 概念

Computer Use 是指 AI 直接操控计算机界面（鼠标、键盘、屏幕）来完成任务，而非通过 API 调用。代表了从"API Agent"到"GUI Agent"的演进。

```
┌─────────── Agent 交互方式演进 ───────────┐
│                                           │
│  API Agent          GUI Agent             │
│  ├─ 调用 REST API   ├─ 看屏幕截图         │
│  ├─ 执行函数        ├─ 移动鼠标/点击      │
│  ├─ 结构化输入输出   ├─ 键盘输入           │
│  └─ 需要 API 集成   └─ 无需 API，通用性强  │
│                                           │
│  适用：有 API 的服务  适用：任何有 GUI 的应用│
└──────────────────────────────────────────┘
```

## 2. Anthropic Claude Computer Use

Claude 的 Computer Use 能力通过截图理解屏幕内容，生成鼠标/键盘操作指令。

<!-- version-check: computer_20250124 (Claude 4 系列), beta header computer-use-2025-01-24, checked 2026-05-20 -->
<!-- 修复于 2026-05-20: 工具版本 computer_20241022 已是旧版（对应已废弃的 Sonnet 3.7），Claude 4 模型须用 computer_20250124 -->

```python
import anthropic

client = anthropic.Anthropic()

# Computer Use 工具定义（Claude 4 系列）
tools = [
    {
        "type": "computer_20250124",
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1,
    },
    {
        "type": "text_editor_20250124",
        "name": "str_replace_editor",
    },
    {
        "type": "bash_20250124",
        "name": "bash",
    },
]

response = client.beta.messages.create(
    model="claude-sonnet-4-6-20260217",
    max_tokens=4096,
    tools=tools,
    betas=["computer-use-2025-01-24"],  # 必须的 beta header
    messages=[{
        "role": "user",
        "content": "打开浏览器，搜索今天的天气，截图给我看",
    }],
)

# 处理 Computer Use 动作
for block in response.content:
    if block.type == "tool_use":
        if block.name == "computer":
            action = block.input
            # action: {"action": "mouse_move", "coordinate": [960, 540]}
            # action: {"action": "left_click"}
            # action: {"action": "type", "text": "today weather"}
            # action: {"action": "screenshot"}
            # 增强动作（computer_20250124）：scroll、left_click_drag、
            # right_click、double_click、hold_key、wait 等
            execute_computer_action(action)
```

## 3. AWS Nova Act SDK

Nova Act 专注于浏览器自动化，提供高级语义操作接口。

```python
from nova_act import NovaAct

# 基本浏览器操作
with NovaAct(starting_page="https://www.amazon.com") as act:
    # 语义化操作 — 用自然语言描述动作
    act.act("在搜索框中输入 'mechanical keyboard'")
    act.act("点击搜索按钮")
    act.act("按价格从低到高排序")
    act.act("点击第一个商品")

    # 提取信息
    result = act.act("提取商品名称、价格和评分")
    print(result.response)
    # → {"name": "...", "price": "$59.99", "rating": "4.5/5"}

# 复杂工作流
with NovaAct(starting_page="https://github.com") as act:
    act.act("登录账号", credentials={"username": "xxx", "password": "xxx"})
    act.act("进入 my-repo 仓库")
    act.act("创建一个新的 Issue，标题为 'Bug: 登录页面样式错误'")
    act.act("添加 bug 标签")
```

## 4. Playwright MCP / Puppeteer MCP

通过 MCP 协议将浏览器自动化能力暴露给 Agent。

<!-- 修复于 2026-05-20: 官方 Playwright MCP 包是 @playwright/mcp（Microsoft 维护），不是 @anthropic/mcp-playwright -->

```json
// MCP 配置 — Playwright（官方包，Microsoft 维护）
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    }
  }
}
```

```python
# Agent 通过 MCP 调用 Playwright
# 工具自动暴露：navigate, click, fill, screenshot, evaluate 等

# 在 Agent 对话中：
# "打开 https://example.com，填写登录表单并提交"
# Agent 会调用：
#   1. navigate(url="https://example.com/login")
#   2. fill(selector="#username", value="user")
#   3. fill(selector="#password", value="pass")
#   4. click(selector="#submit")
#   5. screenshot()  — 验证结果
```

## 5. Web 浏览 Agent 平台

```python
# Browserbase — 云端浏览器基础设施
from browserbase import BrowserBase

bb = BrowserBase(api_key="xxx")
session = bb.create_session()

# 提供给 Agent 使用的浏览器实例
browser_url = session.connect_url
# Agent 通过 CDP 协议控制浏览器

# Steel — 专为 AI Agent 设计的浏览器 API
from steel import Steel

steel = Steel(api_key="xxx")
session = steel.sessions.create()

# 自动处理：验证码、Cookie、指纹
page = session.navigate("https://example.com")
content = page.extract("提取所有产品信息")
```

## 6. GUI Agent vs API Agent

| 维度 | GUI Agent | API Agent |
|------|-----------|-----------|
| 交互方式 | 屏幕截图 + 鼠标键盘 | 函数调用 + 结构化数据 |
| 通用性 | 高（任何有界面的应用） | 低（需要 API 集成） |
| 速度 | 慢（截图+推理+操作） | 快（直接调用） |
| 准确性 | 中（依赖视觉理解） | 高（结构化输入输出） |
| 成本 | 高（多模态推理） | 低（文本推理） |
| 稳定性 | 低（UI 变化会影响） | 高（API 契约稳定） |
| 适用场景 | 无 API 的遗留系统 | 有 API 的现代服务 |

```
选择策略：
├─ 有 API → 优先用 API Agent（快、准、省）
├─ 无 API + 简单操作 → Playwright/Puppeteer MCP
├─ 无 API + 复杂操作 → Claude Computer Use / Nova Act
└─ 批量数据采集 → 专用爬虫 + API Agent
```

## 7. 典型用例

```
表单填写：自动填写报销单、申请表
数据提取：从网页抓取结构化数据
测试自动化：UI 回归测试、跨浏览器测试
流程自动化：操作无 API 的内部系统
竞品监控：定期检查竞品网站变化
```

## 8. 安全考虑

```
安全风险：
├─ 凭证泄露：Agent 操作时可能暴露密码
├─ 越权操作：Agent 可能执行未授权的操作
├─ 数据泄露：屏幕截图可能包含敏感信息
├─ 注入攻击：恶意网页可能误导 Agent
└─ 资源滥用：无限制的浏览器操作消耗资源

防护措施：
├─ 沙箱环境：在隔离环境中运行浏览器
├─ 权限控制：限制可访问的 URL 白名单
├─ 截图脱敏：自动遮盖敏感信息区域
├─ 操作审计：记录所有浏览器操作日志
├─ 人工确认：关键操作前请求人工审批
└─ 超时控制：设置操作超时，防止无限循环
```

> 更新于 2026-07-09

### Claude Computer Use 2025-11-24 与 OpenClaw 浏览器对比

| 能力 | Claude `computer_20251124` | OpenClaw `browser` 工具 |
| ---- | -------------------------- | ----------------------- |
| 驱动方式 | 应用层实现 screenshot/click/type 循环 | Gateway CDP 托管 |
| zoom 局部放大 | ✅ `enable_zoom: true` | ❌（可用 Playwright skill 补） |
| 模型绑定 | Anthropic 模型族 | 模型无关（OpenAI/Claude/本地均可） |
| 渠道触达 | 需自建 UI/API | 20+ 消息渠道原生 |
| SDK 入口 | `client.beta.messages.create`（非 Agent SDK） | `openclaw browser` CLI / agent tool |

**面试/架构常考点**：Agent SDK 不含 Computer Use；二者可组合——OpenClaw 做渠道编排 + 消息触达，Claude Computer Use 做高精度桌面操作。

> 来源：[Claude Computer Use 文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)、[Computer Use 最佳实践](https://claude.com/blog/best-practices-for-computer-and-browser-use-with-claude)、[OpenClaw Browser CLI](https://docs.openclaw.ai/cli/browser)

## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Computer Use Demo](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Computer Use官方演示
- [Google - Gemini Computer Use](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Gemini Computer Use介绍

### 📖 官方文档
- [Anthropic Computer Use](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) — Claude Computer Use文档
- [Google Computer Use](https://ai.google.dev/gemini-api/docs/computer-use) — Gemini Computer Use文档
