# LangGraph + MCP 智能 Agent Demo

## 项目简介

基于 LangGraph 工作流编排和 MCP（Model Context Protocol）工具调用的智能 Agent 示例项目。展示了生产级 Agent 的核心技术：工作流编排、RAG 检索、MCP 工具集成、记忆管理、人机协作。

## 技术栈

- **Agent 框架**: LangGraph 1.x
- **LLM**: OpenAI GPT-4o / Anthropic Claude（可切换）
- **工具协议**: MCP（Model Context Protocol）
- **RAG**: LangChain + ChromaDB
- **记忆**: LangGraph Checkpointer + Mem0
- **后端**: Python 3.12 + FastAPI
- **可观测性**: LangSmith / LangFuse
- **容器化**: Docker Compose

## 核心功能

### 1. LangGraph 工作流编排
- 图结构定义 Agent 执行流程
- 条件路由（根据意图分发到不同处理节点）
- 检查点与状态持久化（PostgreSQL）
- 人机交互节点（敏感操作审批）

### 2. MCP 工具集成
- 内置 MCP Server（文件系统、数据库查询）
- 外部 MCP Server 接入（GitHub、Slack）
- 工具自动发现与调用
- 工具权限控制与审计

### 3. RAG 知识检索
- 文档加载与智能分块
- 向量化存储（ChromaDB）
- 混合检索（向量 + 关键词）
- 检索结果重排序（Reranker）

### 4. 记忆管理
- 短期记忆：对话上下文（LangGraph State）
- 长期记忆：用户偏好与历史（Mem0）
- 会话隔离与恢复

## 项目结构

```
langgraph-mcp-agent-demo/
├── app/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py            # LangGraph 工作流定义
│   │   ├── nodes.py            # 图节点（路由、检索、工具调用、生成）
│   │   ├── state.py            # Agent 状态定义
│   │   └── prompts.py          # 系统提示词
│   ├── mcp_servers/
│   │   ├── __init__.py
│   │   ├── db_server.py        # 数据库查询 MCP Server
│   │   └── file_server.py      # 文件操作 MCP Server
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── indexer.py          # 文档索引
│   │   ├── retriever.py        # 检索器
│   │   └── reranker.py         # 重排序
│   ├── memory/
│   │   ├── __init__.py
│   │   └── manager.py          # 记忆管理
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # FastAPI 路由
│   │   └── websocket.py        # WebSocket 流式输出
│   ├── config.py               # 配置管理
│   └── main.py                 # 应用入口
├── tests/
│   ├── test_graph.py           # 工作流测试
│   ├── test_mcp.py             # MCP Server 测试
│   ├── test_rag.py             # RAG 测试
│   └── conftest.py             # 测试配置
├── docs/                       # 知识库文档（RAG 数据源）
│   └── sample_docs/
├── docker-compose.yml
├── Dockerfile
├── env.example
├── pyproject.toml
├── Makefile
└── README.md
```

## 快速开始

### 前置要求
- Python 3.12+
- Docker & Docker Compose
- OpenAI API Key 或 Anthropic API Key

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/langgraph-mcp-agent-demo.git
cd langgraph-mcp-agent-demo

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 配置环境变量
cp env.example .env
# 编辑 .env 填入 API Key

# 5. 启动基础设施（ChromaDB + PostgreSQL）
docker-compose up -d

# 6. 索引示例文档
python -m app.rag.indexer

# 7. 启动服务
python -m app.main
```

### 使用方式

```bash
# API 调用
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我查一下项目文档中关于部署的内容", "session_id": "user-001"}'

# WebSocket 流式对话
wscat -c ws://localhost:8000/ws/chat?session_id=user-001

# 运行测试
make test
```

## 架构设计

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────┐
│              LangGraph 工作流                  │
│                                               │
│  ┌──────┐    ┌──────┐    ┌───────────────┐  │
│  │ 路由  │───>│ RAG  │───>│   LLM 生成    │  │
│  │ Node │    │ Node │    │    Node       │  │
│  └──┬───┘    └──────┘    └───────────────┘  │
│     │                                        │
│     ├───>┌──────────┐    ┌───────────────┐  │
│     │    │ MCP 工具  │───>│  结果整合      │  │
│     │    │   Node   │    │    Node       │  │
│     │    └──────────┘    └───────────────┘  │
│     │                                        │
│     └───>┌──────────┐                       │
│          │ 人工审批  │  ← 敏感操作           │
│          │   Node   │                       │
│          └──────────┘                       │
│                                               │
│  ┌─────────────────────────────────────────┐ │
│  │  State: messages + context + memory     │ │
│  │  Checkpointer: PostgreSQL               │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
    │                           │
    ▼                           ▼
┌─────────┐              ┌──────────┐
│ ChromaDB │              │ MCP      │
│ (向量库)  │              │ Servers  │
└─────────┘              └──────────┘
```

## 关键技术点

### LangGraph 工作流
- 使用 `StateGraph` 定义有向图
- 条件边实现意图路由
- `interrupt_before` 实现人机交互
- PostgreSQL Checkpointer 持久化状态

### MCP 集成
- 自定义 MCP Server（数据库查询、文件操作）
- MCP 工具自动注册到 LangGraph 工具节点
- 工具调用结果回注到 Agent 状态

### RAG 检索
- 文档分块策略：RecursiveCharacterTextSplitter
- 混合检索：向量相似度 + BM25 关键词
- Reranker 重排序提升准确率

## License

MIT License
