# 安全与合规

> Author: Walter Wang

<!-- version-check: OWASP Top 10 2025, OAuth 2.1 draft-15, Zero Trust, checked 2026-07-09 -->

这个目录覆盖通用的应用安全和基础设施安全，补齐各语言独立目录（Python/13-安全编程、Java、Frontend/09-浏览器与网络/04）之外的体系化安全知识。

## 📁 目录结构

```
security/
├── 01-OWASP-Top10-2025.md         # 2025 版变化、A03/A07/A10 新项解读
├── 02-认证与授权体系.md             # OAuth 2.1 / OIDC / SSO / JWT / SAML
├── 03-密码学基础.md                # 对称/非对称/哈希/MAC/签名，常见误用
├── 04-零信任架构.md                # BeyondCorp、mTLS、Service Mesh 安全
├── 05-供应链安全.md                # SBOM、依赖扫描、Sigstore、Slsa
├── 06-LLM与Agent安全.md            # Prompt Injection、MCP 漏洞、模型滥用
├── 07-容器与K8s安全.md              # 镜像扫描、RBAC、NetworkPolicy、PSP
└── 08-Secrets管理.md               # Vault、SOPS、External Secrets Operator
```

## 🎯 2026 年安全形势

- **AI Agent 供应链攻击爆发**：OX Security、Trend Micro 披露 200K+ 易受攻击 MCP 实例
- **Supply Chain 攻击常态化**：tj-actions/changed-files、Nx、trivy-action 接连被攻破
- **OAuth 2.1 统一标准**：PKCE 强制、Implicit Flow 废弃
- **零信任成为默认**：BeyondCorp 模式主流化，mTLS 和 SPIFFE 普及
- **Sigstore / SLSA**：开源代码签名和供应链等级标准化
- **LLM Output 被当作代码**：Prompt Injection 上升为 OWASP LLM Top 10 第一位

## 🔗 关联内容

- **Python 安全** → [python/13-安全编程/](../python/13-安全编程/)
- **Web 安全** → [frontend/09-浏览器与网络/04-Web安全XSS-CSRF.md](../frontend/09-浏览器与网络/04-Web安全XSS-CSRF.md)
- **Agent 安全** → [ai-agent/15-Agent安全与治理/](../ai-agent/15-Agent安全与治理/)
- **可观测性** → [observability-sre/](../observability-sre/)

## 📚 权威参考

- [OWASP Top 10 2025](https://owasp.org/Top10/)
- [OAuth 2.1 Spec](https://oauth.net/2.1/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [SLSA Framework](https://slsa.dev/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
