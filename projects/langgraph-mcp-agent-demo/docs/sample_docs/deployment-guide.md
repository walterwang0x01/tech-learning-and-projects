# 部署指南
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
## Docker 部署

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+

### 部署步骤

1. 构建镜像：`docker build -t my-app .`
2. 启动服务：`docker-compose up -d`
3. 检查状态：`docker-compose ps`

## Kubernetes 部署

### 配置文件
- Deployment: `k8s/deployment.yaml`
- Service: `k8s/service.yaml`
- ConfigMap: `k8s/configmap.yaml`

### 部署命令
```bash
kubectl apply -f k8s/
kubectl get pods -n my-app
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接 | - |
| REDIS_URL | Redis 连接 | - |
| LOG_LEVEL | 日志级别 | INFO |

## 监控

- 健康检查：`GET /health`
- 指标端点：`GET /metrics`
- 日志：stdout JSON 格式
