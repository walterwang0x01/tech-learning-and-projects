# Kubernetes client-go

> Author: Walter Wang

<!-- version-check: client-go v0.36 (K8s 1.36), Kubernetes 1.36 (2026-04-22), controller-runtime 0.21, checked 2026-05-15 -->

## 1. 为什么要用 client-go

K8s 的所有 Operator、Controller、kubectl、Helm 都是基于 client-go。掌握它是进入云原生开发的必修。

```
client-go 的三种访问模式：
├─ clientset：强类型 API，最常用
├─ dynamic client：弱类型，用于 CRD
└─ informer + lister：带本地缓存和事件监听
```

## 2. 基础连接

```go
package main

import (
    "context"
    "flag"
    "log/slog"
    "path/filepath"

    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    "k8s.io/client-go/tools/clientcmd"
    "k8s.io/client-go/util/homedir"
)

func getClient() (*kubernetes.Clientset, error) {
    // 集群内：自动读取 ServiceAccount
    if cfg, err := rest.InClusterConfig(); err == nil {
        return kubernetes.NewForConfig(cfg)
    }

    // 集群外：kubeconfig
    kubeconfig := filepath.Join(homedir.HomeDir(), ".kube", "config")
    flag.StringVar(&kubeconfig, "kubeconfig", kubeconfig, "path to kubeconfig")
    flag.Parse()

    cfg, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
    if err != nil {
        return nil, err
    }
    return kubernetes.NewForConfig(cfg)
}

func main() {
    client, err := getClient()
    if err != nil {
        slog.Error("get client", "err", err)
        return
    }

    // 列出 default 命名空间的所有 Pod
    pods, err := client.CoreV1().Pods("default").List(context.Background(), metav1.ListOptions{})
    if err != nil {
        slog.Error("list pods", "err", err)
        return
    }

    for _, p := range pods.Items {
        slog.Info("pod", "name", p.Name, "status", p.Status.Phase)
    }
}
```

## 3. CRUD 资源

```go
import (
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/resource"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// 创建 Deployment
func createDeployment(client *kubernetes.Clientset) error {
    deployment := &appsv1.Deployment{
        ObjectMeta: metav1.ObjectMeta{
            Name:      "nginx",
            Namespace: "default",
        },
        Spec: appsv1.DeploymentSpec{
            Replicas: ptr.To(int32(3)),
            Selector: &metav1.LabelSelector{
                MatchLabels: map[string]string{"app": "nginx"},
            },
            Template: corev1.PodTemplateSpec{
                ObjectMeta: metav1.ObjectMeta{
                    Labels: map[string]string{"app": "nginx"},
                },
                Spec: corev1.PodSpec{
                    Containers: []corev1.Container{{
                        Name:  "nginx",
                        Image: "nginx:1.27-alpine",
                        Ports: []corev1.ContainerPort{{ContainerPort: 80}},
                        Resources: corev1.ResourceRequirements{
                            Requests: corev1.ResourceList{
                                corev1.ResourceCPU:    resource.MustParse("100m"),
                                corev1.ResourceMemory: resource.MustParse("128Mi"),
                            },
                            Limits: corev1.ResourceList{
                                corev1.ResourceCPU:    resource.MustParse("500m"),
                                corev1.ResourceMemory: resource.MustParse("512Mi"),
                            },
                        },
                    }},
                },
            },
        },
    }

    _, err := client.AppsV1().Deployments("default").Create(
        context.Background(), deployment, metav1.CreateOptions{},
    )
    return err
}

// Scale Deployment
func scale(client *kubernetes.Clientset, name string, replicas int32) error {
    scale, err := client.AppsV1().Deployments("default").GetScale(context.Background(), name, metav1.GetOptions{})
    if err != nil {
        return err
    }
    scale.Spec.Replicas = replicas
    _, err = client.AppsV1().Deployments("default").UpdateScale(context.Background(), name, scale, metav1.UpdateOptions{})
    return err
}
```

## 4. Informer + Lister：高效的本地缓存

轮询 List/Get 会压垮 API Server，生产上**必须用 Informer**：

```go
import (
    "k8s.io/client-go/informers"
    "k8s.io/client-go/tools/cache"
)

func watchPods(client *kubernetes.Clientset, stopCh <-chan struct{}) {
    factory := informers.NewSharedInformerFactory(client, 30*time.Minute)

    podInformer := factory.Core().V1().Pods()

    podInformer.Informer().AddEventHandler(cache.ResourceEventHandlerFuncs{
        AddFunc: func(obj any) {
            pod := obj.(*corev1.Pod)
            slog.Info("pod added", "name", pod.Name)
        },
        UpdateFunc: func(oldObj, newObj any) {
            newPod := newObj.(*corev1.Pod)
            slog.Info("pod updated", "name", newPod.Name, "phase", newPod.Status.Phase)
        },
        DeleteFunc: func(obj any) {
            pod := obj.(*corev1.Pod)
            slog.Info("pod deleted", "name", pod.Name)
        },
    })

    factory.Start(stopCh)
    factory.WaitForCacheSync(stopCh)

    // 使用本地 Lister 查询（不会打到 API Server）
    lister := podInformer.Lister()
    pods, _ := lister.Pods("default").List(labels.Everything())
    slog.Info("cached pods", "count", len(pods))

    <-stopCh
}
```

**Informer 的价值**：
- 本地缓存，List 操作不打 API Server
- 事件驱动：Add / Update / Delete 回调
- 断线自动重连，处理 ResourceVersion 同步

## 5. controller-runtime：写 Operator 的框架

client-go 太底层，生产中的 Operator 用 [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime) + Kubebuilder。

```bash
# 初始化
kubebuilder init --domain example.com --repo github.com/myorg/myop

# 创建 CRD
kubebuilder create api --group apps --version v1 --kind MyApp
```

生成的 Reconciler 骨架：

```go
// api/v1/myapp_types.go
type MyAppSpec struct {
    Replicas int32  `json:"replicas"`
    Image    string `json:"image"`
}

type MyAppStatus struct {
    AvailableReplicas int32  `json:"availableReplicas"`
    Conditions        []metav1.Condition `json:"conditions,omitempty"`
}

// internal/controller/myapp_controller.go
type MyAppReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

// +kubebuilder:rbac:groups=apps.example.com,resources=myapps,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=apps,resources=deployments,verbs=get;list;watch;create;update;patch

func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var app appsv1.MyApp
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }

    // 1. 保证对应 Deployment 存在
    dep := buildDeployment(&app)
    if err := ctrl.SetControllerReference(&app, dep, r.Scheme); err != nil {
        return ctrl.Result{}, err
    }

    if err := r.Patch(ctx, dep, client.Apply, client.ForceOwnership, client.FieldOwner("myapp-controller")); err != nil {
        return ctrl.Result{}, err
    }

    // 2. 更新 status
    var existing appsv1.Deployment
    _ = r.Get(ctx, client.ObjectKeyFromObject(dep), &existing)
    app.Status.AvailableReplicas = existing.Status.AvailableReplicas
    if err := r.Status().Update(ctx, &app); err != nil {
        return ctrl.Result{}, err
    }

    return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}

func (r *MyAppReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&appsv1.MyApp{}).
        Owns(&appsv1.Deployment{}).  // 关注 owned Deployments 的变化
        Complete(r)
}
```

## 6. Reconciler 黄金法则

```
1. Reconcile 必须幂等
   多次执行相同输入应该得到相同结果

2. 不要假设顺序
   事件可能合并、重排、丢失

3. 基于 spec 推导 desired state，对比 actual state
   不要在 Reconciler 外维护状态

4. 所有修改通过 Patch/Apply
   避免 Update 的 conflict 风暴

5. 把 Status 和 Spec 分开更新
   Status 是观测结果，Spec 是用户意图

6. 用 OwnerReference 让 GC 自动清理子资源
   父删 → 子删

7. 不在 Reconcile 里 sleep/长操作
   用 RequeueAfter 让 K8s 调度
```

## 7. Server-Side Apply（2026 推荐）

传统 Update 在多控制器场景下容易 conflict：

```go
// ✅ Server-Side Apply（推荐）
patch := client.Apply
r.Patch(ctx, dep, patch, client.ForceOwnership, client.FieldOwner("myapp-controller"))
```

K8s 会按字段级别记录"谁管哪个字段"，冲突自动处理。

## 8. 测试 Operator

```go
// internal/controller/suite_test.go
// 使用 envtest 启动真实的 API Server 和 etcd
var testEnv = &envtest.Environment{
    CRDDirectoryPaths: []string{filepath.Join("..", "..", "config", "crd", "bases")},
}

func TestMain(m *testing.M) {
    cfg, _ := testEnv.Start()
    k8sClient, _ := client.New(cfg, client.Options{Scheme: scheme.Scheme})

    // ...

    testEnv.Stop()
}

func TestReconcile(t *testing.T) {
    ctx := context.Background()

    app := &appsv1.MyApp{
        ObjectMeta: metav1.ObjectMeta{Name: "test", Namespace: "default"},
        Spec:       appsv1.MyAppSpec{Replicas: 2, Image: "nginx"},
    }
    require.NoError(t, k8sClient.Create(ctx, app))

    // 等待 Reconciler 创建 Deployment
    require.Eventually(t, func() bool {
        var dep appsv1.Deployment
        err := k8sClient.Get(ctx, client.ObjectKey{Name: "test", Namespace: "default"}, &dep)
        return err == nil && *dep.Spec.Replicas == 2
    }, 10*time.Second, 100*time.Millisecond)
}
```

## 9. K8s 1.36 与 client-go 演进（2026-05 更新）

> 🔄 更新于 2026-05-15
>
> Kubernetes 1.36 "ハル (Haru)" 已于 **2026-04-22** 发布（来源：[K8s 1.36 Release Blog](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)）。对应的 `client-go v0.36` 与 `controller-runtime v0.21` 在 4 月底相继 cut。

### 9.1 Declarative Validation GA — Webhook 的退场

K8s 1.36 让 `ValidatingAdmissionPolicy`（CEL 表达式）GA，不再需要部署 Validating Webhook 来做简单策略校验。对 Operator 开发者意味着：

- 简单的 schema 校验直接写 `ValidatingAdmissionPolicy`，不写 Go 代码
- Webhook 只用于复杂业务逻辑（依赖外部系统、复杂跨字段验证）
- Operator Controller 数量减少，运维成本下降

```yaml
# 用 CEL 表达式替代 Webhook 做"必须有 owner 标签"校验
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-owner-label
spec:
  matchConstraints:
    resourceRules:
    - apiGroups:   ["apps"]
      apiVersions: ["v1"]
      operations:  ["CREATE","UPDATE"]
      resources:   ["deployments"]
  validations:
  - expression: "has(object.metadata.labels.owner)"
    message: "Deployment 必须有 owner 标签"
```

### 9.2 PSI Metrics GA + Workload-Aware Preemption

- **PSI（Pressure Stall Information）Metrics GA**：Kubelet 暴露 CPU/内存/IO 压力指标，调度器和 HPA 可以利用更精确的资源压力数据
- **Workload-Aware Preemption**：抢占将 PodGroup 视为整体（如 AI 训练任务），避免拆散并发训练

对 Operator 的影响：写 AI 训练 Operator 时优先用 PodGroup + Volcano/Kueue 集成，让 1.36 抢占器识别整体语义。

### 9.3 Fine-Grained Kubelet API Authorization GA

Kubelet 的子资源（exec、log、metrics）现在可以独立授权。Operator 申请 RBAC 时可以更精确：

```yaml
# 旧：一次给 pods/exec 全开
# 新：拆成读 log 和执行命令
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["pods/exec"]
  verbs: ["create"]
  resourceNames: ["debug-*"]  # 只允许操作 debug-* 命名的 Pod
```

### 9.4 client-go 0.36 关键变化

| 项目 | 变化 | 影响 |
| ---- | ---- | ---- |
| `apimachinery` | CEL `expressions` 字段稳定 | 可在 Go 代码中通过 client-go 创建 ValidatingAdmissionPolicy |
| `tools/cache` | Informer EventHandler 增加 `OnAddWithOptions` | 支持 namespace/label 过滤的初始 sync |
| `rest` | gRPC streaming watch 实验支持 | 大集群 watch 性能优化 |
| Server-Side Apply | 默认推荐 fieldOwner=`<operator-name>/v<version>` | 字段冲突可追溯到具体版本 |

升级建议：

```bash
# 升级 client-go 与 controller-runtime
go get k8s.io/client-go@v0.36.0
go get sigs.k8s.io/controller-runtime@v0.21.0

# 重新生成 CRD（使用 controller-gen v0.18+）
controller-gen crd paths=./api/... output:crd:dir=./config/crd
```

来源：[K8s 1.36 Declarative Validation GA](https://kubernetes.io/blog/2026/05/05/kubernetes-v1-36-declarative-validation-ga/)、[K8s 1.36 Release Notes](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)、[ScaleOps K8s 1.36 摘要](https://scaleops.com/blog/kubernetes-1-36/)

## 10. 生产检查清单

```
Operator 上线前：
☐ Reconcile 幂等，多次执行结果一致
☐ 所有修改走 Server-Side Apply
☐ RBAC 权限最小化（kubebuilder 会自动生成）
☐ Leader Election 启用（多副本时只有一个工作）
☐ Prometheus 指标暴露（controller-runtime 自带）
☐ Finalizer 处理（防止子资源泄漏）
☐ Webhook 做 CRD 默认值 + 校验
☐ 资源 requests/limits 明确
☐ 使用 envtest 做单元测试
☐ 完整 e2e 测试（kind + 真实 CRD）
```

## 📖 参考资料

- [client-go 仓库](https://github.com/kubernetes/client-go)
- [Kubebuilder 文档](https://book.kubebuilder.io/)
- [controller-runtime](https://pkg.go.dev/sigs.k8s.io/controller-runtime)
- [Operator Patterns](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)
- [OperatorHub](https://operatorhub.io/)
