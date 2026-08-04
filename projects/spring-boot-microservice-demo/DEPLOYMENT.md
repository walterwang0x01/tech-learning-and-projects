# 部署指南

## 本地开发环境

### 前置要求
- JDK 17+
- Maven 3.8+
- Docker & Docker Compose

### 启动步骤

1. **启动基础设施**
```bash
docker-compose up -d
```

2. **等待服务就绪**
```bash
# 检查 PostgreSQL
docker exec microservice-postgres pg_isready

# 检查 Kafka
docker exec microservice-kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

3. **构建并启动服务**
```bash
# 构建所有模块
mvn clean install

# 启动用户服务
cd user-service
mvn spring-boot:run
```

4. **验证服务**
```bash
# 健康检查
curl http://localhost:8081/actuator/health

# 创建用户
curl -X POST http://localhost:8081/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

## Docker 部署

### 构建镜像
```bash
docker build -t user-service:1.0.0 -f Dockerfile .
```

### 运行容器
```bash
docker run -d \
  --name user-service \
  -p 8081:8081 \
  -e SPRING_DATASOURCE_URL=jdbc:postgresql://host.docker.internal:5432/microservice_db \
  -e SPRING_DATASOURCE_USERNAME=postgres \
  -e SPRING_DATASOURCE_PASSWORD=postgres \
  user-service:1.0.0
```

## Kubernetes 部署

### 创建 Secret
```bash
kubectl create secret generic db-credentials \
  --from-literal=url=jdbc:postgresql://postgres:5432/microservice_db \
  --from-literal=username=postgres \
  --from-literal=password=postgres
```

### 部署服务
```bash
# 部署 PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# 部署 Kafka
kubectl apply -f k8s/kafka-deployment.yaml

# 部署用户服务
kubectl apply -f k8s/user-service-deployment.yaml
```

### 检查部署状态
```bash
kubectl get pods
kubectl get services
kubectl logs -f deployment/user-service
```

## 监控和日志

### Prometheus 指标
访问 `http://localhost:8081/actuator/prometheus` 查看指标

### 健康检查
- Liveness: `http://localhost:8081/actuator/health/liveness`
- Readiness: `http://localhost:8081/actuator/health/readiness`

## 性能调优

### JVM 参数
```bash
java -Xms512m -Xmx1g \
     -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -jar user-service.jar
```

### 数据库连接池
在 `application.yml` 中配置：
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
```

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查 PostgreSQL 是否运行
   - 验证连接字符串和凭据

2. **Kafka 连接失败**
   - 检查 Kafka 服务状态
   - 验证 bootstrap-servers 配置

3. **端口冲突**
   - 修改 `application.yml` 中的端口配置

