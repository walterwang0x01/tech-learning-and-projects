# IaC 基础设施即代码

> Author: Walter Wang

<!-- version-check: Terraform 1.15.7, OpenTofu 1.12.3, Pulumi 3.249.0, Crossplane 2.3, checked 2026-07-10 -->
<!-- 修复于 2026-05-31: Crossplane 2.x → 2.3（2.2 季度发布后续到 2.3），补充 v2 升级路径 -->
<!-- 修复于 2026-07-10: Terraform 1.11 → 1.15.7、OpenTofu 1.11 → 1.12.3、Pulumi 3.150 → 3.249.0（均为常规迭代升级，正文命令/HCL 语法示例无需改动） -->

## 1. 为什么 IaC

```
手动点云控制台的问题：
├─ 不可审计（谁改了什么）
├─ 不可重建（灾难恢复慢）
├─ 容易漂移（dev 和 prod 不一致）
├─ 知识在少数人头脑里
└─ 权限难管理（谁能点生产）

IaC：
├─ Git 版本化
├─ 代码审查
├─ 自动化执行
└─ 多环境一致
```

## 2. 工具对比

| 工具 | 语言 | 2026 状态 |
|------|------|-----------|
| **Terraform** | HCL | 主流，2023 年 BUSL 许可引发社区不满 |
| **OpenTofu** | HCL | Linux Foundation 接管的 Terraform Fork，开源 |
| **Pulumi** | Python/TS/Go/C# | 编程语言优势 |
| **Crossplane** | K8s YAML | K8s 原生，控制器模式 |
| **AWS CDK** | TS/Python/Java | AWS 专用 |
| **CloudFormation** | YAML/JSON | AWS 原生，功能弱 |

**2026 年建议**：
- **新项目推荐 OpenTofu**（开源保障 + Terraform 兼容）
- **多云 + 编程习惯** → Pulumi
- **K8s 为中心** → Crossplane
- **AWS Only** → CDK 或 CloudFormation

## 3. Terraform / OpenTofu 基础

### 3.1 项目结构

```
infra/
├── main.tf                 # 主配置
├── variables.tf            # 变量定义
├── outputs.tf              # 输出
├── providers.tf            # Provider 配置
├── terraform.tfvars        # 变量值（勿提交密钥）
├── backend.tf              # 状态后端
├── modules/                # 可复用模块
│   ├── vpc/
│   └── eks/
└── environments/
    ├── dev/
    ├── staging/
    └── production/
```

### 3.2 基本语法

```hcl
# providers.tf
terraform {
  required_version = ">= 1.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
}

# variables.tf
variable "region" {
  type    = string
  default = "us-east-1"
}

variable "instance_count" {
  type    = number
  default = 2
}

# main.tf
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "main"
    Env  = terraform.workspace
  }
}

resource "aws_subnet" "private" {
  count             = var.instance_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}

data "aws_availability_zones" "available" {
  state = "available"
}

# outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}
```

### 3.3 工作流

```bash
# 初始化（下载 provider、配置 backend）
terraform init
# 或 OpenTofu
tofu init

# 格式化代码
terraform fmt -recursive

# 静态检查
terraform validate

# 预览变更（必看！）
terraform plan -out=tfplan

# 应用
terraform apply tfplan

# 销毁
terraform destroy
```

## 4. 模块化

```hcl
# modules/eks-cluster/main.tf
variable "name" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

resource "aws_eks_cluster" "this" {
  name     = var.name
  role_arn = aws_iam_role.eks.arn
  version  = "1.34"

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

output "cluster_endpoint" {
  value = aws_eks_cluster.this.endpoint
}

# 使用
module "eks_prod" {
  source     = "./modules/eks-cluster"
  name       = "prod"
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id
}
```

## 5. 状态管理

```
State 文件包含所有真实资源信息
  ├─ 绝不能提交到 Git（含 secret）
  ├─ 本地文件只适合学习
  └─ 生产必须用 Remote Backend

推荐 Backend：
├─ S3 + DynamoDB 锁（AWS）
├─ GCS + GCS Locking（GCP）
├─ Azure Storage + Lease
└─ Terraform Cloud / Terraform Enterprise（托管）

OpenTofu：
└─ 新支持 state encryption，就地加密
```

## 6. Workspace vs 目录分环境

```
方案 A：Workspace
  terraform workspace new dev
  terraform workspace new prod
  优点：代码 DRY
  缺点：所有环境共用 state 后端，隔离弱

方案 B（推荐）：环境目录
  environments/
  ├── dev/ (独立 backend + 独立 state)
  ├── staging/
  └── production/
  优点：强隔离、权限清晰
```

## 7. Pulumi：用编程语言写 IaC

```python
import pulumi
import pulumi_aws as aws

vpc = aws.ec2.Vpc("main",
    cidr_block="10.0.0.0/16",
    tags={"Name": "main"},
)

# 循环创建多子网（普通语言能力）
subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
subnets = [
    aws.ec2.Subnet(f"private-{i}",
        vpc_id=vpc.id,
        cidr_block=cidr,
        availability_zone=f"us-east-1{chr(ord('a') + i)}",
    )
    for i, cidr in enumerate(subnet_cidrs)
]

pulumi.export("vpc_id", vpc.id)
```

优势：
- 用 Python/TS 的类型系统
- 普通的 IDE 补全、测试、循环
- 复杂逻辑比 HCL 清晰

## 8. Crossplane：K8s 原生 IaC

把云资源作为 K8s 自定义资源管理：

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPC
metadata:
  name: main
spec:
  forProvider:
    cidrBlock: 10.0.0.0/16
    region: us-east-1
    tags:
      Name: main
  providerConfigRef:
    name: aws-config
```

`kubectl apply` 就创建了 AWS VPC。配合 Argo CD 实现 "一个 GitOps 管所有基础设施"。

## 9. 测试 IaC

```bash
# Terraform Test（1.6+ 内置）
terraform test

# Terratest（Go）
import "github.com/gruntwork-io/terratest/modules/terraform"

func TestVPC(t *testing.T) {
    opts := &terraform.Options{TerraformDir: "./modules/vpc"}
    defer terraform.Destroy(t, opts)
    terraform.InitAndApply(t, opts)
    vpcID := terraform.Output(t, opts, "vpc_id")
    assert.NotEmpty(t, vpcID)
}

# Checkov（静态安全扫描）
checkov -d infra/

# TFLint
tflint --recursive
```

## 10. 生产最佳实践

```
命名与标签：
├─ 所有资源必带 Owner、Env、CostCenter 标签
├─ 模块名清晰（不要叫 stuff、temp）
└─ 变量名和文档对齐

权限：
├─ 各环境独立 AWS 账号
├─ CI 用 OIDC + IAM Role（不要长期 Key）
└─ Least Privilege：生产 apply 权限只给 CI 的专用角色

State：
├─ 加密 + 版本化 + 访问审计
├─ Lock 机制避免并发 apply
└─ 重要操作前备份 state

审批：
├─ PR 触发 plan 并在评论里展示
├─ Merge to main 才能 apply
└─ 生产 apply 需要人工确认（Atlantis、Spacelift、env0）
```

## 11. 反模式

```
❌ 手动改云资源（Drift）
   → plan 时大量意外变更

❌ state 里存密钥
   → 泄露即高危

❌ 单体仓库 + 单个 state
   → 变更影响全部，apply 超慢
   → 按"爆炸半径"拆分

❌ 用 terraform apply -auto-approve 在生产
   → 没有人类审核的机会

❌ 模块写死 provider version
   → 升级困难；建议用 `~>` 约束

❌ 改了 Terraform 后不更新文档
   → 新人看不懂
```

## 12. 2026 年 IaC 生态变化

```
├─ HashiCorp 被 IBM 收购（2024 宣布，2025 完成）
├─ OpenTofu 社区快速成熟
├─ Stackery / Pulumi AI：AI 辅助生成 IaC
├─ Terramate / Terragrunt：大型 monorepo 编排
└─ Platform Engineering 中 IaC 通常封装到 Crossplane / Backstage 后面
    业务团队不直接写 Terraform
```

### 12.1 Crossplane v2 与最新版本动态

> 🔄 更新于 2026-05-31

Crossplane 已在 2025-10-28 升级为 CNCF **Graduated** 项目，并发布了 2.0 大版本。2026 年持续迭代到 **v2.3**（v2.2 为季度发布，后续递进到 v2.3）。

来源：[Announcing Crossplane 2.0](https://blog.crossplane.io/announcing-crossplane-2-0/)、[Crossplane v2.2 发布说明](https://blog.crossplane.io/crossplane-v2-2-more-capable-more-reliable-more-observable/)、[CNCF Crossplane](https://www.cncf.io/projects/crossplane/)

Crossplane v2 的核心变化：

```
Crossplane v2 关键能力
├─ Namespaced 资源（XR/MR 可放在 namespace 里，不再强制 cluster-scoped）
├─ 可组合任意 Kubernetes 资源（不限于云资源）
├─ 新的运维工作流（Operations）
└─ 与大多数 v1 配置向后兼容
```

升级路径有严格约束（官方明确要求逐版本递进）：

```
只能从 v1.20（最后一个 v1.x 版本）升级到 v2.0
  v1.19 → v1.20 → v2.0 → v2.1 → v2.2 → v2.3
  （每次只跨一个 minor，并用该 minor 的最新 patch）

注意：v1 的 cluster-scoped XR/MR 暂无自动迁移工具
  升级后存量 v1 资源继续按原样工作
  新资源可直接用 v2 的 namespaced 风格
```

来源：[Upgrade to Crossplane v2](https://docs.crossplane.io/master/guides/upgrade-to-crossplane-v2/)

第 8 节的 `kubectl apply` 创建云资源示例在 v2 中仍然有效；v2 额外允许把这些 Managed Resource 放进具体 namespace 做多租户隔离。

## 📖 参考资料

- [Terraform 官方文档](https://developer.hashicorp.com/terraform)
- [OpenTofu](https://opentofu.org/)
- [Pulumi Docs](https://www.pulumi.com/docs/)
- [Crossplane Docs](https://docs.crossplane.io/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Checkov 规则库](https://www.checkov.io/)
