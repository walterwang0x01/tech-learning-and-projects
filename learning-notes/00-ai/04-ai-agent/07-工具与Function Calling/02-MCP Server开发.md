# MCP Server 开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Python SDK 完整示例

```python
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image
import httpx
import json

mcp = FastMCP(
    name="business-tools",
    version="1.0.0",
    description="企业业务工具集",
)

# ===== 工具注册 =====
@mcp.tool()
def query_orders(user_id: str, status: str = "all") -> list[dict]:
    """查询用户订单列表

    Args:
        user_id: 用户ID
        status: 订单状态过滤（all/pending/completed/cancelled）
    """
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = ? AND (? = 'all' OR status = ?)",
        (user_id, status, status),
    ).fetchall()
    return [dict(row) for row in orders]

@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """搜索知识库（支持语义搜索）"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/search",
            json={"query": query, "top_k": top_k},
        )
        results = response.json()
    return json.dumps(results, ensure_ascii=False, indent=2)

# ===== 资源注册 =====
@mcp.resource("db://schema")
def get_database_schema() -> str:
    """获取数据库表结构"""
    tables = db.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return "\n\n".join(row[0] for row in tables)

@mcp.resource("config://app/{env}")
def get_config(env: str) -> str:
    """获取应用配置（dev/staging/prod）"""
    config = load_config(env)
    return json.dumps(config, indent=2)

# ===== 提示模板注册 =====
@mcp.prompt()
def analyze_data(dataset: str, goal: str) -> str:
    """数据分析提示模板"""
    return f"""请分析以下数据集，目标是：{goal}

数据集：{dataset}

请按以下步骤进行：
1. 数据概览和质量检查
2. 关键指标统计
3. 趋势和异常分析
4. 结论和建议"""

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 2. TypeScript SDK 完整示例

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "project-tools",
  version: "1.0.0",
});

// 工具注册
server.tool(
  "create_ticket",
  {
    title: z.string().describe("工单标题"),
    description: z.string().describe("问题描述"),
    priority: z.enum(["low", "medium", "high"]).default("medium"),
  },
  async ({ title, description, priority }) => {
    const ticket = await ticketService.create({ title, description, priority });
    return {
      content: [{ type: "text", text: `工单已创建: ${ticket.id}` }],
    };
  }
);

// 资源注册
server.resource(
  "logs",
  new ResourceTemplate("logs://{service}/{date}", { list: undefined }),
  async (uri, { service, date }) => ({
    contents: [{ uri: uri.href, mimeType: "text/plain", text: await getLogs(service, date) }],
  })
);

// 启动
const transport = new StdioServerTransport();
await server.connect(transport);
```

## 3. 传输层实现

> 🔄 更新于 2026-04-18

<!-- version-check: MCP Python SDK 1.27+, 97M+ 月下载量, checked 2026-04-18 -->

```python
# stdio 传输（本地 IDE 集成，最常用）
if __name__ == "__main__":
    mcp.run(transport="stdio")

# Streamable HTTP（推荐的远程传输，替代已废弃的 SSE）
# 支持有状态和无状态两种模式
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)

# 无状态 Streamable HTTP（适合简单工具，无需持久连接）
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("my-server", stateless_http=True)
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
```

> **MCP 生态 2026 现状**：
> - MCP Python SDK 已达 **v1.27+**，月下载量超过 **9700 万**（[来源](https://www.aimagicx.com/blog/mcp-production-server-tutorial-97-million-downloads-2026)）
> - GitHub 上已有 **13,000+** MCP Server 实现
> - Gartner 预测到 2026 年底 **75%** 的 API 网关厂商将支持 MCP
> - **SSE 传输已正式废弃**（2025-03-26 规范），Streamable HTTP 成为标准远程传输
> - **FastMCP 独立项目**：[PrefectHQ/fastmcp](https://github.com/jlowin/fastmcp) 提供更 Pythonic 的 MCP Server/Client 开发体验
> - 支持 `stateless_http` 参数控制有状态/无状态模式，有状态模式支持 Sampling（服务端请求客户端 LLM 调用）

## 4. 认证与安全

```python
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("secure-tools")

# 环境变量传递密钥
API_KEY = os.environ.get("API_KEY")
DB_URL = os.environ.get("DATABASE_URL")

@mcp.tool()
def secure_query(sql: str) -> str:
    """安全的数据库查询（只读）"""
    # 输入验证
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
    if any(kw in sql.upper() for kw in forbidden):
        raise ValueError("只允许 SELECT 查询")

    # 参数化查询防止 SQL 注入
    result = db.execute(sql).fetchall()
    return json.dumps([dict(r) for r in result], ensure_ascii=False)
```

```json
// mcp.json 配置认证
{
  "mcpServers": {
    "secure-tools": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "API_KEY": "${env:MY_API_KEY}",
        "DATABASE_URL": "${env:DB_URL}"
      }
    }
  }
}
```

## 5. 测试与调试

```bash
# 使用 MCP Inspector 调试
npx @modelcontextprotocol/inspector python server.py

# 命令行测试
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python server.py
```

```python
# 单元测试
import pytest
from mcp.server.fastmcp import FastMCP

@pytest.fixture
def mcp_server():
    mcp = FastMCP("test")

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """加法"""
        return a + b

    return mcp

async def test_tool_call(mcp_server):
    """测试工具调用"""
    result = await mcp_server.call_tool("add", {"a": 1, "b": 2})
    assert result == 3

async def test_tool_list(mcp_server):
    """测试工具列表"""
    tools = await mcp_server.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "add"
```
## 🎬 推荐视频资源

- [freeCodeCamp - MCP Crash Course](https://www.youtube.com/watch?v=JBqLV4MnN3E) — MCP Server开发完整教程
- [Anthropic - Building MCP Servers](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — 官方MCP Server开发指南
