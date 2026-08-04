# RAG + LLM Agent 平台

## 项目简介

基于 RAG（检索增强生成）和 Function Calling 的企业级 AI Agent 平台，支持知识检索、工具调用和流式交互。

## 技术栈

- **LLM**: Amazon Bedrock (Claude), OpenAI API
- **RAG框架**: LlamaIndex
- **向量数据库**: PostgreSQL + pgvector
- **后端**: Python (FastAPI)
- **实时通信**: WebSocket
- **容器化**: Docker, Kubernetes
- **监控**: Prometheus

## 核心功能

### 1. RAG 检索增强生成
- 文档向量化与存储
- 语义检索与相关性排序
- 上下文增强的提示工程

### 2. Function Calling 工具体系
- 30+ 业务工具（订单管理、价格调整等）
- 工具自动选择与调用
- 调用成功率监控（98%+）

### 3. 流式交互
- WebSocket 实时通信
- 首字响应时间 ≤ 1s
- 流式输出优化

### 4. 工程化部署
- Docker 容器化
- Kubernetes 编排
- 灰度发布与回滚

## 项目结构

```
rag-llm-agent-platform/
├── app/
│   ├── api/              # FastAPI 路由
│   ├── core/             # 核心业务逻辑
│   ├── agents/           # AI Agent 实现
│   ├── tools/            # Function Calling 工具
│   ├── rag/              # RAG 检索模块
│   └── models/           # 数据模型
├── tests/                # 单元测试
├── docker/               # Docker 配置
├── k8s/                  # Kubernetes 配置
└── requirements.txt      # Python 依赖
```

## 快速开始

### 前置要求
- Python 3.10+
- PostgreSQL 14+ (with pgvector extension)
- Docker & Docker Compose

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/your-username/rag-llm-agent-platform.git
cd rag-llm-agent-platform
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入 API Keys 和数据库配置
```

4. 启动服务
```bash
docker-compose up -d  # 启动 PostgreSQL
python -m uvicorn app.main:app --reload
```

## 核心实现

### RAG 检索流程
1. 文档预处理与分块
2. 向量化（使用 OpenAI embeddings）
3. 存储到 pgvector
4. 查询时进行语义检索
5. 检索结果作为上下文注入 LLM

### Function Calling 示例
```python
tools = [
    {
        "name": "create_order",
        "description": "创建新订单",
        "parameters": {...}
    },
    {
        "name": "update_price",
        "description": "更新商品价格",
        "parameters": {...}
    }
]
```

### 流式输出
- 使用 Server-Sent Events (SSE) 或 WebSocket
- 逐 token 返回，提升用户体验
- 首字响应时间优化

## 性能指标

- **工具调用成功率**: 98%+
- **日均调用量**: 1,200+ 次
- **首字响应时间**: ≤ 1s
- **订单处理时长**: 从 5 分钟降至 30 秒
- **错误率下降**: 60%+

## 业务价值

- 自动化高频人工操作
- 显著提升处理效率
- 降低操作错误率
- 提升内部满意度（NPS +25%）

## 最佳实践

- Prompt Engineering 优化
- 向量检索策略调优
- 工具调用错误处理
- 监控与告警机制
- 灰度发布策略

## License

MIT License

