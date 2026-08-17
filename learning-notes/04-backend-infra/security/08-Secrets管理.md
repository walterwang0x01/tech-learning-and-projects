# Secrets 管理

> Author: Walter Wang

<!-- 修复于 2026-07-10: Vault 已从 1.21 系列升级到 2.0 主版本线（Community + Enterprise 均已 GA），当前最新 2.0.3（2026-06-17），1.21.x 仍以 1.21.8 维护安全补丁；文中 KV/Dynamic Secrets/Agent Injector 命令语法在 2.0 中保持兼容，无需改代码示例 -->
<!-- version-check: HashiCorp Vault 2.0.3 (2026-06-17, 2.0 主版本 GA 于 2026-04-14；1.21.8 仍在维护), External Secrets Operator 2.4.x, SOPS 3.13, checked 2026-07-10 -->

## 1. Secrets 管理的目标

```
├─ 不提交到 Git
├─ 加密存储
├─ 访问审计
├─ 自动轮换
├─ 短期凭证优于长期
└─ 按需交付（需要时才能拿到）
```

## 2. 常见反模式

```
❌ 写在代码里
const API_KEY = "sk-xxx";

❌ 写在配置文件里提交
config.yml（有 db_password）→ git commit

❌ 写在 CI secrets 但无隔离
所有 workflow 都能读所有 secrets

❌ 环境变量永久不变
API_KEY 设一次用 3 年

❌ K8s Secret 直接 YAML 提交
data:
  password: cGFzc3dvcmQ=   # 只是 base64
```

## 3. 工具地图

| 类别 | 工具 | 场景 |
|------|------|------|
| **云托管** | AWS Secrets Manager / Parameter Store | AWS 生态 |
| **云托管** | Google Secret Manager | GCP |
| **云托管** | Azure Key Vault | Azure |
| **自托管** | HashiCorp Vault | 多云、企业 |
| **自托管** | Infisical | 轻量开源替代 |
| **K8s 集成** | External Secrets Operator | 从云 SM 拉取到 K8s |
| **Git 加密** | SOPS | 加密文件提交到 Git |
| **Git 加密** | Sealed Secrets | K8s 集群私钥解密 |
| **开发者** | 1Password CLI / Doppler | 本地开发共享 |

## 4. HashiCorp Vault

### 4.1 核心概念

```
Vault 的核心能力：
├─ KV：静态 Secrets（API Key、密码）
├─ Dynamic Secrets：按需生成（DB 账号、云凭证）
├─ PKI：证书管理
├─ Transit：加密即服务（应用不碰密钥）
└─ Identity：多身份认证
```

### 4.2 KV 使用

```bash
# 启动开发模式
vault server -dev

# 写
vault kv put secret/myapp db_password=secret123 api_key=sk-xxx

# 读
vault kv get secret/myapp
vault kv get -field=db_password secret/myapp
```

### 4.3 Dynamic Secrets（强大特性）

```bash
# 配置 PostgreSQL dynamic secrets
vault secrets enable database

vault write database/config/mydb \
    plugin_name=postgresql-database-plugin \
    allowed_roles="readonly" \
    connection_url="postgresql://{{username}}:{{password}}@pg:5432/mydb" \
    username="vault_admin" \
    password="xxx"

vault write database/roles/readonly \
    db_name=mydb \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';" \
    default_ttl="1h" \
    max_ttl="24h"

# 应用请求：拿到 1 小时有效的 DB 账号
vault read database/creds/readonly
# 1 小时后账号自动失效，Vault 会清理
```

应用代码几乎没有"DB 密码"这个概念。

### 4.4 Vault 认证

```
├─ Token（默认）
├─ AppRole（服务账号）
├─ Kubernetes（Pod SA Token 换 Vault Token）
├─ AWS / GCP / Azure IAM
├─ OIDC
└─ JWT
```

K8s 示例（Vault Agent Injector）：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp"
        vault.hashicorp.com/agent-inject-secret-config: "secret/myapp"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/myapp" -}}
          DB_PASSWORD={{ .Data.data.db_password }}
          API_KEY={{ .Data.data.api_key }}
          {{- end -}}
    spec:
      serviceAccountName: myapp
      containers:
        - name: myapp
          image: myapp:v1
          # Vault 把 secrets 注入 /vault/secrets/config
```

## 5. External Secrets Operator（推荐）

让 K8s Secret 自动从云 SM / Vault 拉取：

```bash
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace
```

```yaml
# SecretStore：配置后端
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
# ExternalSecret：从 SM 同步到 K8s Secret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: myapp-secrets    # 生成的 K8s Secret 名
    creationPolicy: Owner
  data:
    - secretKey: db-password
      remoteRef:
        key: prod/myapp/db
        property: password
    - secretKey: api-key
      remoteRef:
        key: prod/myapp/api
        property: apiKey
```

应用用 K8s Secret 一样用，但源头是 AWS Secrets Manager。

## 6. SOPS：加密文件进 Git

适合小团队、简单场景：

```bash
# 安装
brew install sops

# 用 AWS KMS 加密
sops --kms 'arn:aws:kms:us-east-1:xxx:key/yyy' -e -i secrets.yaml

# 或用 age（轻量对称密钥）
age-keygen -o key.txt
sops --age=age1xxx -e -i secrets.yaml

# 加密后文件：
#   db_password: ENC[AES256_GCM,data:xxx,iv:yyy,tag:zzz]
# 可以安全提交到 Git

# 解密（需要 KMS 权限或 age key）
sops -d secrets.yaml
```

**Argo CD Plugin** 或 **sops-operator** 可以在 K8s 自动解密。

## 7. Sealed Secrets（Bitnami）

```bash
# 本地用 kubeseal 加密，只能集群私钥解
echo -n "mypassword" | kubectl create secret generic mysecret \
    --dry-run=client --from-file=password=/dev/stdin -o yaml | \
    kubeseal -o yaml > sealed-secret.yaml

# 加密后：
# apiVersion: bitnami.com/v1alpha1
# kind: SealedSecret
# spec:
#   encryptedData:
#     password: AgB+xxx...    # 只有集群能解

# 可以安全提交 Git
```

## 8. 开发环境 Secrets

```
避免开发者本地硬编码：
├─ 1Password CLI：op run --env-file=.env.tpl -- ./app
├─ Doppler：doppler run -- ./app
├─ direnv + .envrc（配合密钥管理器）
└─ VSCode：在 devcontainer 里注入
```

```bash
# 1Password 示例
cat .env.tpl
# DATABASE_URL=op://Engineering/mydb/url
# API_KEY=op://Engineering/openai/key

op run --env-file=.env.tpl -- python app.py
```

## 9. 轮换策略

```
静态 Secrets：
├─ 数据库密码：每 90 天轮换
├─ API Key：每 180 天
├─ TLS 证书：Let's Encrypt 每 60-90 天自动
└─ OAuth Secret：客户端每 180-365 天

Dynamic Secrets：
└─ Vault 生成的天然短期（1-24 小时）

工具：
├─ Vault 自带 TTL 和轮换
├─ AWS Secrets Manager 支持 Rotation Lambda
└─ cert-manager 自动轮证书
```

## 10. 密钥泄漏应急流程

```
0. 发现泄漏（监控 / Bug Bounty / GitGuardian）
1. 立即吊销（不是改密码，是吊销）
2. 检查访问日志（谁在什么时候用过）
3. 按攻击假设：查受影响的数据 / 系统
4. 从 Git 历史清理（BFG Repo-Cleaner / git filter-repo）
5. 通知合规团队（GDPR 72h 内）
6. Postmortem：怎么泄漏的，流程哪里出问题
7. 更新防御（Pre-commit hook、CI gitleaks）
```

## 11. CI/CD 中的 Secrets

```
GitHub Actions 最佳实践：
├─ 用 Environment Secrets + approval
├─ PR 流水线不传 Secrets（Fork 可以看环境变量）
├─ 用 OIDC 换云凭证（避免长期 Key）
├─ 最小权限原则
└─ 定期轮换 Token

# OIDC 换 AWS 凭证
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::xxx:role/github-actions
    aws-region: us-east-1
# 没有 AWS_ACCESS_KEY_ID / SECRET
```

## 12. 生产检查清单

```
☐ Secrets 不进 Git（GitLeaks / TruffleHog 扫描）
☐ Pre-commit hook 拦截
☐ 所有 Secrets 在中心化系统（Vault / 云 SM）
☐ K8s 用 External Secrets Operator 或 Vault Injector
☐ etcd Encryption at Rest 启用
☐ 数据库用 Dynamic Secrets
☐ 定期轮换 + 监控过期
☐ 应用打印日志时不输出 Secrets
☐ CI 用 OIDC + IAM Role
☐ 应急流程演练过
```

## 📖 参考资料

- [HashiCorp Vault](https://www.vaultproject.io/docs)
- [External Secrets Operator](https://external-secrets.io/)
- [SOPS](https://github.com/getsops/sops)
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
