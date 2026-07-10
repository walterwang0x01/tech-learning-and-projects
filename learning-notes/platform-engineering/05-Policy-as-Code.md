# Policy as Code

> Author: Walter Wang

<!-- version-check: OPA 0.71, Kyverno 1.17.2 (2026-04-23，1.13/1.14 已 EOL), Conftest 0.56, Cedar 4.x, checked 2026-07-10 -->

## 1. 为什么要 Policy as Code

```
传统策略管理：
├─ Wiki 写规则（没人看）
├─ Code Review 手动检查（漏网）
├─ 上线后才发现违规（太晚）
└─ 各团队各做一套（不一致）

Policy as Code：
├─ 策略 = 代码（Git 版本化）
├─ CI/CD 自动执行（提前拦截）
├─ 全组织统一（中心化治理）
└─ 审计友好（谁改了什么）
```

## 2. 主流工具

| 工具 | 定位 | 语言 |
|------|------|------|
| **OPA** | 通用策略引擎 | Rego |
| **Kyverno** | K8s 原生 | YAML |
| **Conftest** | 配置文件测试（基于 OPA） | Rego |
| **Checkov** | IaC 安全扫描 | Python 声明式 |
| **tfsec** | Terraform 专用 | 内置规则 |
| **Cedar** | AWS 开源，偏应用授权 | Cedar DSL |
| **Trivy Config** | Trivy 的策略模块 | Rego |

## 3. OPA（Open Policy Agent）

CNCF 毕业项目，通用策略引擎。

### 3.1 Rego 基础

```rego
package example

# 默认值
default allow = false

# 规则：管理员放行
allow {
    input.user.role == "admin"
}

# 规则：用户访问自己的资源
allow {
    input.action == "read"
    input.resource.owner == input.user.id
}
```

### 3.2 作为 K8s Admission Controller

OPA Gatekeeper（OPA + K8s）：

```yaml
# ConstraintTemplate 定义策略逻辑
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items: {type: string}
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels

        violation[{"msg": msg}] {
          required := input.parameters.labels
          provided := input.review.object.metadata.labels
          missing := required[_]
          not provided[missing]
          msg := sprintf("Missing required label: %v", [missing])
        }

---
# Constraint 应用策略
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ns-must-have-team
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: [Namespace]
  parameters:
    labels: [team, env, cost-center]
```

### 3.3 Terraform 策略

```rego
# policy/terraform.rego
package terraform

# 禁止公开 S3 bucket
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    resource.change.after.acl == "public-read"
    msg := sprintf("Public S3 bucket: %v", [resource.address])
}

# 要求所有 EC2 实例有标签
deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_instance"
    required := ["Team", "Environment", "CostCenter"]
    tag := required[_]
    not resource.change.after.tags[tag]
    msg := sprintf("Instance %v missing tag %v", [resource.address, tag])
}
```

```bash
# 检查 Terraform plan
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
opa eval --data policy/ --input plan.json 'data.terraform.deny'
```

## 4. Kyverno：K8s 原生，不用 Rego

很多团队觉得 Rego 学习曲线陡，Kyverno 用 K8s YAML 直接写策略。

```yaml
# 必须有 resources.limits
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resources
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-resources
      match:
        any:
          - resources: {kinds: [Pod]}
      validate:
        message: "CPU and memory limits are required"
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    memory: "?*"
                    cpu: "?*"

---
# 禁止 latest tag
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: no-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-image-tag
      match:
        any:
          - resources: {kinds: [Pod]}
      validate:
        message: "Using 'latest' tag is not allowed"
        pattern:
          spec:
            containers:
              - image: "!*:latest"

---
# 自动给所有 namespace 加默认 NetworkPolicy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: default-deny
spec:
  rules:
    - name: create-default-deny
      match:
        any:
          - resources: {kinds: [Namespace]}
      generate:
        kind: NetworkPolicy
        apiVersion: networking.k8s.io/v1
        name: default-deny
        namespace: "{{request.object.metadata.name}}"
        data:
          spec:
            podSelector: {}
            policyTypes: [Ingress, Egress]
```

Kyverno 和 OPA Gatekeeper 的对比：

```
Kyverno：
├─ YAML 语法，学习门槛低
├─ K8s 原生（只能管 K8s 资源）
├─ 能 generate / mutate 资源
└─ 2026 年 K8s 场景推荐

OPA：
├─ 通用（K8s、Terraform、CI、应用授权）
├─ Rego 学习曲线陡
└─ 跨多个系统统一策略时用
```

> 更新于 2026-07-10
>
> **Kyverno 版本纠偏**：文档标注的 1.13 已 EOL（2025-11-10 停止支持）。当前处于活跃支持期的是 **1.15 / 1.16 / 1.17**（三个 minor 同时在维），**1.17.2（2026-04-23）为最新版**；1.14 也已于 2026-02-02 EOL。生产集群若还在 1.13/1.14，应尽快规划升级路径（[Kyverno EOL 日期](https://eosl.date/eol/product/kyverno/)）。
>
> Kyverno 1.12+ 起策略类型已收敛为稳定版：`ValidatingPolicy`、`MutatingPolicy`、`GeneratingPolicy`、`DeletingPolicy`（按计划自动清理资源，如定时清理已完成 Job 的 Pod）、`ImageValidatingPolicy`（校验镜像签名，配合 Cosign/Notary），迁移旧版 `ClusterPolicy` 时建议对照新的稳定策略类型文档。

## 5. Conftest：配置文件通用检查

```bash
# 检查 Dockerfile
conftest test --policy policy/ Dockerfile

# 检查 K8s YAML
conftest test --policy policy/ k8s-manifests/

# 检查 Helm Chart（先 render）
helm template my-chart | conftest test --policy policy/ -
```

```rego
# policy/dockerfile.rego
package main

deny[msg] {
    input[i].Cmd == "user"
    val := input[i].Value[0]
    val == "root"
    msg := "Container running as root"
}

deny[msg] {
    input[i].Cmd == "from"
    val := input[i].Value[0]
    contains(val, ":latest")
    msg := "Using :latest tag"
}
```

## 6. Checkov / tfsec：IaC 安全扫描

Checkov 是开箱即用的扫描器（已有几百条规则）：

```bash
pip install checkov
checkov -d terraform/
checkov -f main.tf
checkov -d kubernetes/ --framework kubernetes
checkov --framework github_actions -d .github/workflows/
```

典型输出：
```
FAILED for resource: aws_s3_bucket.data
Check: CKV_AWS_19: "Ensure the S3 bucket has access logging enabled"
```

## 7. 策略实施阶段

```
阶段 1：Warn Only
  策略违反只警告不阻止
  收集数据，了解当前违反情况

阶段 2：Audit
  违规项在 Portal 的 Scorecard 里显示
  负责人定期清理

阶段 3：Enforce
  新资源必须符合，老资源给迁移期

阶段 4：持续演进
  基于事故和审计新增策略
  定期回顾，淘汰无效策略
```

## 8. 策略分类（参考 CIS）

```
安全类：
├─ 不允许 privileged 容器
├─ 必须非 root 用户
├─ 镜像必须签名
├─ Secret 不在环境变量
└─ 网络策略必须存在

成本类：
├─ 必须有 resources.limits
├─ 必须有 CostCenter 标签
├─ 禁用超大实例类型
└─ S3 必须启用 Lifecycle

合规类：
├─ 必须有 Owner 标签
├─ 必须部署在指定 Region
├─ PII 字段必须加密
└─ 所有资源必须有审计日志

质量类：
├─ 必须有 Liveness / Readiness Probe
├─ 不允许 latest tag
├─ 必须有 Health 端点
└─ API 必须有 OpenAPI spec
```

## 9. 应用层授权：OPA / Cedar / OpenFGA

业务应用里的复杂权限：

### OPA 示例

```rego
# 用户能否编辑文档
package documents.edit

default allow = false

allow {
    input.user.role == "admin"
}

allow {
    input.user.id == input.document.owner
}

allow {
    input.user.id == input.document.editors[_]
}

allow {
    input.user.groups[_] == input.document.group_editors[_]
}
```

```python
# 应用调用
resp = requests.post("http://opa:8181/v1/data/documents/edit/allow",
    json={"input": {
        "user": {"id": "alice", "role": "user", "groups": ["team-a"]},
        "document": {"id": 1, "owner": "bob", "editors": ["alice"]},
    }},
)
can_edit = resp.json()["result"]
```

### Cedar（AWS 开源）

```cedar
permit (
    principal == User::"alice",
    action in [Action::"read", Action::"edit"],
    resource
)
when {
    resource in Group::"team-a"
};

forbid (
    principal,
    action == Action::"delete",
    resource is Document
)
unless {
    principal == resource.owner
};
```

### OpenFGA（Google Zanzibar）

关系型授权模型，复杂 SaaS 推荐：

```
define user
define group
  relations
    define member: [user]

define document
  relations
    define owner: [user]
    define editor: [user, group#member]
    define viewer: [user, group#member] or editor or owner
```

## 10. 生产检查清单

```
☐ K8s 有 Admission Controller（Kyverno / Gatekeeper）
☐ 生产 namespace 强制 Restricted PSA
☐ 所有 IaC 走 Checkov / tfsec 扫描
☐ 关键策略在 CI 硬门禁
☐ 策略有 Owner（Platform 团队）
☐ 违规有 Dashboard（Scorecard）
☐ 新策略先 Warn 再 Enforce
☐ 应用授权用 OPA / Cedar / OpenFGA 集中
☐ 策略本身纳入版本控制和 Code Review
☐ 例外规则有审批流程
```

## 11. 反模式

```
❌ 策略太严格一上来
   → 大量误报，被团队反感后废弃

❌ 策略在 Wiki / PPT
   → 无法自动执行

❌ 每个策略一个工具
   → OPA / Kyverno / Checkov 混用太乱
   ✅ 选一个主力，其他补充

❌ 策略无 Owner
   → 过时、无维护

❌ 不监控策略本身
   → 策略挂了没人知道
```

## 📖 参考资料

- [OPA 文档](https://www.openpolicyagent.org/docs)
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)
- [Kyverno](https://kyverno.io/docs/)
- [Conftest](https://www.conftest.dev/)
- [Checkov](https://www.checkov.io/)
- [Cedar](https://www.cedarpolicy.com/)
- [OpenFGA](https://openfga.dev/)
