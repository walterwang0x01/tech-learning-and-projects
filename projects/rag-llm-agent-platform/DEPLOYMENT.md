# RAG LLM Agent 平台部署指南

## 本地开发环境

### 前置要求
- Python 3.10+
- PostgreSQL 14+ (with pgvector extension)
- Docker & Docker Compose

### 启动步骤

1. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，填入 API Keys
```

2. **启动 PostgreSQL**
```bash
docker-compose up -d postgres
```

3. **初始化数据库**
```bash
# 等待 PostgreSQL 就绪
docker exec rag-postgres psql -U postgres -d rag_db -f /docker-entrypoint-initdb.d/init.sql
```

4. **安装依赖**
```bash
pip install -r requirements.txt
```

5. **启动服务**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **验证服务**
```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 测试聊天（需要配置 API Keys）
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "stream": false
  }'
```

## Docker 部署

### 构建镜像
```bash
docker build -t rag-agent-platform:1.0.0 -f Dockerfile .
```

### 运行容器
```bash
docker run -d \
  --name rag-agent \
  -p 8000:8000 \
  --env-file .env \
  --link rag-postgres:postgres \
  rag-agent-platform:1.0.0
```

## Kubernetes 部署

### 创建 Secrets
```bash
# 数据库凭据
kubectl create secret generic rag-db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=postgres

# LLM API Keys
kubectl create secret generic llm-credentials \
  --from-literal=openai-api-key=your_key \
  --from-literal=aws-access-key-id=your_key \
  --from-literal=aws-secret-access-key=your_secret
```

### 部署服务
```bash
# 部署 PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# 部署 RAG Agent
kubectl apply -f k8s/rag-agent-deployment.yaml
```

## 向量数据导入

### 导入文档
```python
from app.rag.vector_store import VectorStore
from app.llm.llm_client import LLMClient

# 初始化
vector_store = VectorStore()
llm_client = LLMClient()

# 文档向量化并存储
documents = ["文档内容1", "文档内容2"]
for doc in documents:
    embedding = await llm_client.get_embedding(doc)
    await vector_store.insert_vector(doc, embedding)
```

## WebSocket 流式聊天

### 客户端示例
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    message: "你好",
    conversation_id: null
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chunk') {
    console.log(data.content);
  } else if (data.type === 'done') {
    console.log('完成');
  }
};
```

## 性能优化

### 向量检索优化
- 使用 IVFFlat 索引加速相似度搜索
- 调整 `lists` 参数平衡精度和速度
- 缓存常用查询的向量结果

### LLM 调用优化
- 使用流式输出减少首字响应时间
- 实现请求队列和限流
- 缓存常见问题的回答

### 数据库优化
```sql
-- 创建向量索引
CREATE INDEX documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 分析表统计信息
ANALYZE documents;
```

## 监控和日志

### 健康检查
- Health: `http://localhost:8000/api/v1/health`
- Readiness: `http://localhost:8000/api/v1/ready`

### 日志配置
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
```

## 故障排查

### 常见问题

1. **pgvector 扩展未安装**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **API Key 配置错误**
   - 检查 `.env` 文件
   - 验证环境变量是否正确加载

3. **向量维度不匹配**
   - 确保使用相同的 embedding 模型
   - 检查向量维度配置（默认 1536）

4. **WebSocket 连接失败**
   - 检查防火墙设置
   - 验证 CORS 配置

