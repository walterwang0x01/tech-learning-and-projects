# CrewAI 多 Agent 协作 Demo

## 项目简介

基于 CrewAI 框架的多 Agent 协作示例项目，展示角色化 Agent 团队协作完成「技术博客内容创作流水线」。四个专业 Agent（研究员、作家、编辑、SEO 优化师）按顺序协作，从主题研究到最终发布，完整演示多 Agent 系统的核心模式。

## 技术栈

- **多 Agent 框架**: CrewAI 0.86+
- **LLM**: OpenAI GPT-4o / Anthropic Claude（可切换）
- **工具集成**: CrewAI Tools + MCP 工具协议
- **记忆系统**: CrewAI Memory + Mem0 长期记忆
- **后端**: Python 3.12 + FastAPI
- **缓存**: Redis
- **搜索**: Serper API（Google 搜索）

## 核心功能

### 1. 多 Agent 角色协作
- **高级研究员**: 深度调研主题，收集权威资料与最新动态
- **技术作家**: 基于研究成果撰写高质量技术文章
- **内容编辑**: 审校文章质量，优化结构与表达
- **SEO 优化师**: 关键词优化、元数据生成、搜索引擎友好化

### 2. 执行流程
- **顺序执行**: 研究 → 写作 → 编辑 → SEO 优化（默认）
- **层级执行**: Manager Agent 统一调度，动态分配任务

### 3. MCP 工具集成
- SerperDevTool（网络搜索）
- ScrapeWebsiteTool（网页抓取）
- 自定义工具（文件保存、字数统计、关键词密度分析）

### 4. 记忆系统
- 短期记忆：任务上下文传递
- 长期记忆：Mem0 存储历史创作偏好
- 实体记忆：识别并记忆关键实体信息

## 项目结构

```
crewai-multi-agent-demo/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── researcher.py       # 高级研究员 Agent
│   │   ├── writer.py           # 技术作家 Agent
│   │   ├── editor.py           # 内容编辑 Agent
│   │   └── seo_optimizer.py    # SEO 优化师 Agent
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── content_tasks.py    # 内容创作任务定义
│   ├── crews/
│   │   ├── __init__.py
│   │   └── content_crew.py     # Crew 组装与执行
│   ├── tools/
│   │   ├── __init__.py
│   │   └── custom_tools.py     # 自定义工具
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # FastAPI 路由
│   ├── config.py               # 配置管理
│   └── main.py                 # 应用入口（API + CLI）
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # 测试配置
│   ├── test_tools.py           # 工具测试
│   └── test_crew.py            # Crew 组装测试
├── output/                     # 生成文章输出目录
│   └── .gitkeep
├── docker-compose.yml
├── env.example
├── pyproject.toml
├── Makefile
└── README.md
```

## 快速开始

### 前置要求
- Python 3.12+
- Docker & Docker Compose（Redis 缓存）
- OpenAI API Key 或 Anthropic API Key
- Serper API Key（网络搜索，可选）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/crewai-multi-agent-demo.git
cd crewai-multi-agent-demo

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 配置环境变量
cp env.example .env
# 编辑 .env 填入 API Key

# 5. 启动 Redis（缓存）
docker-compose up -d

# 6. 运行内容创作流水线
python -m app.main --topic "AI Agent 技术趋势"
```

## 架构设计

```
用户输入主题
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  CrewAI Content Crew                  │
│                                                       │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐ │
│  │  高级研究员  │───>│  技术作家   │───>│  内容编辑   │ │
│  │ Researcher │    │  Writer    │    │  Editor    │ │
│  └─────┬──────┘    └─────┬──────┘    └─────┬──────┘ │
│        │                 │                 │         │
│   SerperDev         FileWrite          纯 LLM       │
│   WebScrape          Tool             推理审校       │
│        │                 │                 │         │
│        ▼                 ▼                 ▼         │
│  ┌─────────────────────────────────────────────────┐ │
│  │              任务上下文传递 (Context)              │ │
│  └─────────────────────────────────────────────────┘ │
│                         │                             │
│                         ▼                             │
│                  ┌────────────┐                       │
│                  │ SEO 优化师  │                       │
│                  │ Optimizer  │                       │
│                  └─────┬──────┘                       │
│                        │                              │
│                   SerperDev                           │
│                   关键词分析                            │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Memory: 短期记忆 + 长期记忆 (Mem0) + 实体记忆   │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌──────────┐    ┌──────────┐
│  output/  │    │  Redis   │
│ 文章文件   │    │  缓存    │
└──────────┘    └──────────┘
```

## 使用示例

### CLI 模式

```bash
# 基本用法
python -m app.main --topic "AI Agent 技术趋势"

# 指定执行模式
python -m app.main --topic "RAG 最佳实践" --process hierarchical
```

### API 模式

```bash
# 启动 API 服务
make run

# 创建内容
curl -X POST http://localhost:8000/api/create-content \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI Agent 技术趋势"}'

# 健康检查
curl http://localhost:8000/api/health
```

### API 响应示例

```json
{
  "topic": "AI Agent 技术趋势",
  "status": "completed",
  "article": "# AI Agent 技术趋势\n\n...",
  "metadata": {
    "word_count": 2500,
    "process": "sequential",
    "agents": ["researcher", "writer", "editor", "seo_optimizer"]
  }
}
```

## License

MIT License
