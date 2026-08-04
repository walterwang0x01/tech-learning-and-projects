# Kubernetes 部署实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 使用 Kubernetes 部署 Python 应用

## 1. Kubernetes 基础

### 1.1 核心概念

- **Pod**：最小部署单元
- **Deployment**：管理Pod的副本
- **Service**：暴露应用服务
- **ConfigMap**：配置管理
- **Secret**：敏感信息管理

## 2. Dockerfile 优化

### 2.1 多阶段构建

```dockerfile
# 构建阶段
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2 优化镜像

```dockerfile
# 使用非root用户
RUN useradd -m -u 1000 appuser
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1
```

## 3. Deployment 配置

### 3.1 基础 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
  labels:
    app: python-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: python-app
  template:
    metadata:
      labels:
        app: python-app
    spec:
      containers:
      - name: app
        image: python-app:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 4. Service 配置

### 4.1 ClusterIP Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-app-service
spec:
  selector:
    app: python-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### 4.2 LoadBalancer Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-app-lb
spec:
  selector:
    app: python-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 5. ConfigMap 和 Secret

### 5.1 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.env: "production"
  log.level: "info"
```

### 5.2 Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  url: <base64-encoded-value>
  password: <base64-encoded-value>
```

## 6. 水平扩缩容

### 6.1 HPA 配置

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: python-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: python-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 7. 滚动更新

### 7.1 更新策略

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### 7.2 更新命令

```bash
# 更新镜像
kubectl set image deployment/python-app app=python-app:2.0.0

# 查看更新状态
kubectl rollout status deployment/python-app

# 回滚
kubectl rollout undo deployment/python-app
```

## 8. 监控和日志

### 8.1 Prometheus 监控

```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-app-metrics
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: python-app
  ports:
  - port: 8000
```

### 8.2 日志收集

```python
# 使用结构化日志
import logging
import json

logger = logging.getLogger(__name__)

def log_request(request):
    logger.info(json.dumps({
        "method": request.method,
        "path": request.path,
        "status": 200
    }))
```

## 9. 最佳实践

### 9.1 资源限制

- 设置requests和limits
- 避免资源竞争
- 监控资源使用

### 9.2 健康检查

- 实现liveness和readiness探针
- 设置合理的超时时间
- 处理优雅关闭

### 9.3 安全

- 使用非root用户
- 限制容器权限
- 使用Secret管理敏感信息

## 10. 总结

Kubernetes部署要点：
- **Deployment**：管理应用副本
- **Service**：暴露服务
- **ConfigMap/Secret**：配置管理
- **HPA**：自动扩缩容
- **滚动更新**：零停机更新
- **监控日志**：可观测性
- **安全**：最佳安全实践

Kubernetes提供了强大的容器编排能力。

