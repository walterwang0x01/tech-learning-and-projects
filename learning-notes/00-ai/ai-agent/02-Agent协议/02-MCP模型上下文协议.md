# MCP 模型上下文协议
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. MCP 概述

MCP（Model Context Protocol）是 Anthropic 于 2024 年底提出的开放协议，用于标准化 AI 模型与外部工具、数据源之间的连接。类比为"AI 应用的 USB-C 接口"。

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   MCP Host    │     │  MCP Client  │     │  MCP Server  │
│  (IDE/App)    │────>│  (协议层)     │────>│  (工具/数据)  │
│  Claude Desktop│     │              │     │  GitHub API  │
│  Cursor/Kiro  │     │              │     │  数据库       │
│  自定义应用    │     │              │     │  文件系统     │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 2. 核心概念

### 2.1 三大原语

```python
# 1. Tools（工具）— 模型可调用的函数
@mcp.tool()
def search_database(query: str, limit: int = 10) -> list[dict]:
    """搜索数据库中的记录"""
    return db.search(query, limit=limit)

# 2. Resources（资源）— 模型可读取的数据
@mcp.resource("file://{path}")
def read_file(path: str) -> str:
    """读取文件内容"""
    return Path(path).read_text()

# 3. Prompts（提示模板）— 预定义的交互模板
@mcp.prompt()
def code_review(code: str, language: str) -> str:
    """代码审查提示模板"""
    return f"请审查以下 {language} 代码:\n\n{code}"
```

### 2.2 传输层

> 🔄 更新于 2026-04-16

<!-- version-check: MCP spec 2026-03-26, Streamable HTTP 替代 SSE, checked 2026-04-16 -->

```
stdio            — 本地进程通信（最常用，IDE集成）
Streamable HTTP  — 新一代 HTTP 传输（推荐，替代 SSE）
SSE              — HTTP Server-Sent Events（已废弃，2026-03-26 规范正式移除）
```

> **重要变更**：MCP 2025-03-26 规范引入 Streamable HTTP 传输，使用单一 `/mcp` 端点处理所有双向通信。2026-03-26 规范正式废弃 SSE 传输。认证从 OAuth 2.0 升级到 OAuth 2.1（强制 PKCE + HTTPS）。来源：[MCP Specification Changelog](https://www.mcpserverspot.com/learn/fundamentals/mcp-specification-changelog)

## 3. MCP Server 开发（Python）

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-tools")

@mcp.tool()
def get_weather(city: str) -> str:
    """获取城市天气信息"""
    # 调用天气 API
    response = requests.get(f"https://api.weather.com/{city}")
    data = response.json()
    return f"{city}: {data['temp']}°C, {data['condition']}"

@mcp.tool()
def query_database(sql: str) -> list[dict]:
    """执行 SQL 查询（只读）"""
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("只允许 SELECT 查询")
    return db.execute(sql).fetchall()

@mcp.resource("config://app")
def get_app_config() -> str:
    """获取应用配置"""
    return json.dumps(config, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 4. MCP Server 开发（TypeScript）

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "my-tools", version: "1.0.0" });

server.tool("search_docs", { query: z.string(), limit: z.number().default(5) },
  async ({ query, limit }) => {
    const results = await searchIndex(query, limit);
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

## 5. 配置与使用

```json
// mcp.json（IDE 配置）
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["my_mcp_server.py"],
      "env": { "DATABASE_URL": "postgresql://..." }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_xxx" }
    }
  }
}
```

## 6. MCP 生态

```
官方 Server：
- filesystem    — 文件系统操作
- github        — GitHub API
- postgres      — PostgreSQL 查询
- slack         — Slack 消息
- puppeteer     — 浏览器自动化
- memory        — 知识图谱记忆

社区 Server：1000+ 开源实现
```

## 7. MCP 安全风险评估

> 🔄 更新于 2026-04-20

### 7.1 Gartner 权威预测（2026.04.09）

<!-- version-check: Gartner MCP security prediction, checked 2026-04-20 -->

Gartner 于 2026 年 4 月 9 日发布了针对 MCP 安全风险的正式预测，这是首次有权威分析机构将 MCP 协议安全风险写入正式报告：

```
Gartner 预测数据：
  → 2028 年：25% 的企业 GenAI 应用将每年遭遇至少 5 次轻微安全事件（2025 年为 9%）
  → 2029 年：15% 的企业 GenAI 应用将每年遭遇至少 1 次重大安全事件（2025 年为 3%）

Gartner 高级分析师 Aaron Lord 原话：
  "MCP 优先考虑互操作性、易用性和灵活性，安全性被置于次要位置。
   因此在 agentic AI 缺乏持续监督时，安全错误会不断涌现。"
```

来源：[Gartner Newsroom](https://www.gartner.com/en/newsroom/press-releases/2026-04-09-gartner-predicts-25-percent-of-all-enterprise-gen-ai-applications-will-experience-at-least-five-minor-security-incidents-per-year-by-2028) (Content was rephrased for compliance with licensing restrictions)

### 7.2 MCP STDIO 命令注入漏洞（2026.04.16）

OX Security 于 2026 年 4 月 16 日披露了 MCP 协议中一个系统性的命令注入漏洞，影响范围极广：

```
漏洞概况：
  → 约 1.5 亿次下载、7,000 个公开可访问的服务器、20 万个易受攻击实例
  → 10 个 CVE 被提交，其中 9 个标记为严重级别
  → 根因：MCP 使用 STDIO 作为本地传输时允许执行任意 OS 命令

四类攻击路径：
  1. 未认证命令注入
  2. 绕过加固的命令注入
  3. 通过 prompt injection 修改 MCP 配置的命令注入
  4. 通过网络请求的未认证命令注入

受影响工具：
  LangFlow、GPT Researcher、Windsurf、Claude Code、GitHub Copilot 等

Anthropic 回应：认为这是"预期行为"，拒绝修补
```

来源：[Computing.co.uk](https://www.computing.co.uk/news/2026/security/flaw-in-anthropic-s-mcp-putting-200k-servers-at-risk) / [The Register](https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/) (Content was rephrased for compliance with licensing restrictions)

### 7.3 企业 MCP 安全建议

```
基于 Gartner 预测和 OX Security 漏洞披露的行动建议：

  □ 将 MCP 安全审计纳入企业合规流程
  □ 阻止公网 IP 访问 MCP 服务
  □ 将外部 MCP 配置输入视为不可信数据
  □ 在沙箱中运行 MCP 服务
  □ 监控工具调用行为
  □ 仅使用官方 MCP 目录中的服务器
  □ 建立 MCP 安全监控机制

详细防御方案 → [MCP安全漏洞与Agent供应链攻击](../15-Agent安全与治理/05-MCP安全漏洞与Agent供应链攻击.md)
```
## 🎬 推荐视频资源

- [Anthropic - Model Context Protocol Introduction](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — MCP官方介绍
- [freeCodeCamp - MCP Crash Course](https://www.youtube.com/watch?v=JBqLV4MnN3E) — MCP完整教程
- [AI Jason - MCP Explained](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — MCP协议通俗讲解
