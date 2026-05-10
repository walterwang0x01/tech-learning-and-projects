# Kubernetes client-go

> Author: Walter Wang

<!-- version-check: client-go v0.31, Kubernetes 1.33, controller-runtime 0.20, checked 2026-05-10 -->

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

## 9. 生产检查清单

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
