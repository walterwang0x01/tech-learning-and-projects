# Kubernetes 概述
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 从 private-notes 提取的技术学习笔记

## Kubernetes 简介

Kubernetes（K8s）是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用程序。

## 应用部署方式演变

1. **传统部署**：直接部署在物理机
2. **虚拟化部署**：虚拟机环境
3. **容器化部署**：Docker 容器

## Kubernetes 核心功能

- **自我修复**：容器崩溃时自动重启
- **弹性伸缩**：根据负载自动调整容器数量
- **服务发现**：自动发现依赖服务
- **负载均衡**：自动实现请求负载均衡
- **版本回退**：支持版本回滚
- **存储编排**：自动创建存储卷

## 核心组件

### Master 节点

- **ApiServer**：资源操作的唯一入口
- **Scheduler**：负责集群资源调度
- **ControllerManager**：维护集群状态
- **Etcd**：存储集群资源对象信息

### Node 节点

- **Kubelet**：维护容器的生命周期
- **KubeProxy**：服务发现和负载均衡
- **Docker**：容器运行时

## 核心概念

- **Pod**：最小的部署单元
- **Service**：服务发现和负载均衡
- **Deployment**：管理 Pod 的副本
- **Namespace**：资源隔离
- **ConfigMap**：配置管理
- **Secret**：敏感信息管理

## 常用命令

```bash
# 查看资源
kubectl get pods
kubectl get services
kubectl get deployments

# 创建资源
kubectl apply -f <yaml-file>

# 删除资源
kubectl delete -f <yaml-file>

# 查看日志
kubectl logs <pod-name>

# 进入容器
kubectl exec -it <pod-name> -- /bin/bash
```

## 参考资料

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Kubernetes 中文文档](https://kubernetes.io/zh-cn/docs/)



## Kubernetes 版本演进（2025-2026）

<!-- version-check: Kubernetes 1.36 Haru (April 2026), checked 2026-05-04 -->

> 🔄 更新于 2026-04-27

### K8s 1.33 "Octarine"（2025-04-23）

**毕业为稳定（Stable）的关键特性**：
- **Sidecar Containers**：原生支持 `initContainers` 设置 `restartPolicy: Always`，随 Pod 全生命周期运行
- **`--subresource` flag**：kubectl get/patch/edit/replace 支持操作 status、scale 等子资源

**Beta 特性**：
- **In-place Pod Vertical Scaling**：运行中调整 Pod 的 CPU/内存，无需重启
- **nftables**：kube-proxy 支持 nftables 后端（替代 iptables）

**Alpha 特性**：
- **Pod Generation Tracking**：Pod 新增 `metadata.generation` 字段，追踪 spec 变更
- **OCI Image Volumes**：将容器镜像直接挂载为 Volume
- **Service Account Token 增强**：自定义 kubelet token audience 和 account name

> 来源：[Kubernetes 1.33 – What's new?](https://sysdig.com/blog/kubernetes-1-33-whats-new/)

### K8s 1.34 "Of Wind & Will"（2025-08-27）

58 个 KEP，是近期最大的版本之一。

**核心新特性**：
- **DRA（Dynamic Resource Allocation）增强**：结构化参数让硬件驱动以标准化格式描述设备能力
- **Pod-level Resources**：Pod 级别资源配额（而非仅容器级别）
- **Per-container Restart Policy**：同一 Pod 内不同容器可设置不同重启策略
- **EnvFiles**（Alpha）：从运行时生成的文件加载环境变量

```yaml
# K8s 1.34：Per-container Restart Policy 示例
apiVersion: v1
kind: Pod
spec:
  restartPolicy: OnFailure
  restartPolicyRules:
    - exitCode: 1
      action: FailContainer
```

```yaml
# K8s 1.34：EnvFiles 示例 — init 容器生成配置，主容器自动加载
apiVersion: v1
kind: Pod
spec:
  initContainers:
    - name: generate-config
      image: busybox:1.36
      command: ["sh", "-c", "echo 'EPOCHS=25' > /config/runtime.env"]
      volumeMounts:
        - name: config
          mountPath: /config
  containers:
    - name: trainer
      image: python:3.12-slim
      envFromFile:
        - path: runtime.env
          volumeName: config
  volumes:
    - name: config
      emptyDir: {}
```

> 来源：[Kubernetes v1.34 Release](https://www.perfectscale.io/blog/kubernetes-v1-34-release)

### 版本选择建议（2026）

| 环境 | 推荐版本 | 说明 |
|------|---------|------|
| 生产环境 | 1.33.x | 稳定，云厂商已全面支持 |
| 测试/预发布 | 1.34.x | 评估新特性（DRA、Pod-level Resources） |
| 新集群 | 1.33+ | 享受 Sidecar Containers 和 In-place Scaling |

> 注意：K8s 1.35 已在开发中，预计 2025-12 发布。

### K8s 1.35 "Ironclad"（2025-12-10）

**毕业为稳定（Stable）的关键特性**：
- **In-place Pod Vertical Scaling**：运行中调整 Pod 的 CPU/内存，无需重启（从 1.33 beta 毕业）
- **nftables kube-proxy**：nftables 后端正式稳定，替代 iptables

**Beta 特性**：
- **Pod-level Resources**：Pod 级别资源配额进入 beta
- **OCI Image Volumes**：将容器镜像直接挂载为 Volume 进入 beta

> 来源：[Kubernetes 1.35 Preview](https://jacar.es/en/kubernetes-1-35-preview/)

### K8s 1.36 "ハル (Haru)"（2026-04-22）

> 🔄 更新于 2026-05-04

2026 年首个 K8s 版本，包含 70 个增强特性（18 个 Stable、25 个 Beta、25 个 Alpha）。主题名 "ハル" 在日语中意为"春天"、"晴朗"和"遥远"。

**毕业为稳定（GA）的关键特性**：
- **User Namespaces**：Pod 内用户命名空间隔离正式 GA，增强容器安全性
- **Fine-grained Kubelet API Authorization**：细粒度 kubelet API 授权，替代过于宽泛的 `nodes/proxy` 权限
- **Mutating Admission Policies**：变更准入策略 GA
- **DRA 相关 4 个增强**：Dynamic Resource Allocation 全面 GA，GPU/TPU/NIC 等硬件资源标准化分配

**Beta 特性**：
- **Resource Health Status**：报告已分配设备的健康状态（GPU 故障检测）
- **Mutable Pod Resources for Suspended Jobs**：暂停的 Job 可修改资源请求
- **Tiered Memory Protection with Memory QoS**：分层内存保护

**Alpha 特性**：
- **AI Gateway Working Group**：Kubernetes 正式成立 AI Gateway 工作组
- **Agent Sandbox**：在 K8s 上运行 AI Agent 的沙箱环境

```yaml
# K8s 1.36：User Namespaces 示例（GA）
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  hostUsers: false  # 启用用户命名空间隔离
  containers:
    - name: app
      image: myapp:latest
      securityContext:
        runAsNonRoot: true
```

> 来源：[Kubernetes v1.36: ハル (Haru)](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release) | [K8s 1.36 Features](https://cloudraft.io/blog/kubernetes-v1-36-haru-features-upgrade-guide)

### 版本选择建议（2026 更新）

| 环境 | 推荐版本 | 说明 |
|------|---------|------|
| 生产环境 | 1.34.x / 1.35.x | 稳定，云厂商已全面支持 |
| 测试/预发布 | 1.36.x | 评估 User Namespaces GA、DRA GA |
| AI/ML 工作负载 | 1.36.x | DRA GA + AI Gateway + Agent Sandbox |
| 新集群 | 1.35+ | 享受 In-place Scaling GA 和 nftables |
