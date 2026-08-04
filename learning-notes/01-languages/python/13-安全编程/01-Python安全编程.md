# Python安全编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

<!-- version-check: OWASP Top 10 2025, pip-audit 2.9.x, Python 3.14, checked 2026-05-12 -->

## 1. 安全编程概述

Python应用安全涉及多个方面：
- **输入验证**：防止注入攻击
- **认证授权**：用户身份验证和权限控制
- **数据加密**：敏感数据加密存储和传输
- **安全配置**：安全的最佳实践配置

## 2. 输入验证

### 2.1 SQL注入防护

```python
# 危险的做法
query = f"SELECT * FROM users WHERE name = '{username}'"
cursor.execute(query)

# 安全的做法：使用参数化查询
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (username,))

# SQLAlchemy
from sqlalchemy import text
query = text("SELECT * FROM users WHERE name = :name")
result = session.execute(query, {"name": username})
```

### 2.2 命令注入防护

```python
import subprocess
import shlex

# 危险的做法
subprocess.call(f"ls {user_input}", shell=True)

# 安全的做法：使用参数列表
subprocess.call(["ls", user_input])

# 或者使用shlex转义
subprocess.call(["ls", shlex.quote(user_input)])
```

### 2.3 XSS防护

```python
from markupsafe import escape

# 转义用户输入
user_input = "<script>alert('XSS')</script>"
safe_input = escape(user_input)

# Flask自动转义
from flask import render_template_string
template = "Hello {{ name }}"
render_template_string(template, name=user_input)  # 自动转义
```

### 2.4 输入验证

```python
import re
from email.utils import parseaddr

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """验证用户名"""
    if not username or len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

def sanitize_input(user_input):
    """清理用户输入"""
    # 移除危险字符
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        user_input = user_input.replace(char, '')
    return user_input.strip()
```

## 3. 认证和授权

### 3.1 密码哈希

```python
import hashlib
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

# 生成密码哈希
password = "user_password"
hashed = generate_password_hash(password)

# 验证密码
is_valid = check_password_hash(hashed, password)

# 使用bcrypt
import bcrypt

password = b"user_password"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)

# 验证
is_valid = bcrypt.checkpw(password, hashed)
```

### 3.2 JWT认证

```python
import jwt
import datetime

SECRET_KEY = "your-secret-key"

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

### 3.3 会话管理

```python
from flask import session
import secrets

# 设置安全的会话密钥
app.secret_key = secrets.token_hex(32)

# 使用会话
session['user_id'] = user_id
session.permanent = True  # 持久会话

# 清除会话
session.clear()
```

### 3.4 权限控制

```python
from functools import wraps
from flask import abort

def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@require_permission('admin')
def admin_only():
    return "Admin only"
```

## 4. 数据加密

### 4.1 对称加密

```python
from cryptography.fernet import Fernet

# 生成密钥
key = Fernet.generate_key()
cipher = Fernet(key)

# 加密
message = b"secret message"
encrypted = cipher.encrypt(message)

# 解密
decrypted = cipher.decrypt(encrypted)
```

### 4.2 非对称加密

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# 生成密钥对
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# 加密
message = b"secret message"
encrypted = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# 解密
decrypted = private_key.decrypt(
    encrypted,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
```

### 4.3 哈希函数

```python
import hashlib

# SHA256
message = b"message"
hash_obj = hashlib.sha256(message)
hash_hex = hash_obj.hexdigest()

# 加盐哈希
import secrets
salt = secrets.token_bytes(16)
hash_obj = hashlib.sha256(message + salt)
hash_hex = hash_obj.hexdigest()
```

## 5. 安全配置

### 5.1 环境变量

```python
import os
from decouple import config

# 使用环境变量存储敏感信息
SECRET_KEY = config('SECRET_KEY')
DATABASE_URL = config('DATABASE_URL')
API_KEY = config('API_KEY')
```

### 5.2 HTTPS配置

```python
from flask import Flask

app = Flask(__name__)

# 生产环境强制HTTPS
@app.before_request
def force_https():
    if not request.is_secure and app.env == 'production':
        return redirect(request.url.replace('http://', 'https://'), code=301)
```

### 5.3 CORS配置

```python
from flask_cors import CORS

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://example.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 5.4 安全头

```python
from flask import Flask

app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## 6. 文件上传安全

### 6.1 文件类型验证

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    if not allowed_file(file.filename):
        return 'Invalid file type', 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return 'File uploaded', 200
```

### 6.2 文件大小限制

```python
from flask import Flask, request, abort

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

@app.errorhandler(413)
def too_large(e):
    return "File too large", 413
```

## 7. 日志安全

### 7.1 避免记录敏感信息

```python
import logging

def sanitize_log_data(data):
    """清理日志中的敏感信息"""
    sensitive_fields = ['password', 'token', 'api_key', 'secret']
    if isinstance(data, dict):
        sanitized = data.copy()
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***'
        return sanitized
    return data

logger.info(f"User data: {sanitize_log_data(user_data)}")
```

## 8. 依赖安全

### 8.1 检查依赖漏洞

```bash
# 使用 pip-audit（推荐，PyPA 官方维护）
pip install pip-audit
pip-audit

# 使用 safety 检查（Safety DB）
pip install safety
safety check

# 使用 uv 内置审计（2026 年推荐）
uv pip audit
```

### 8.2 固定依赖版本

```python
# requirements.txt — 固定版本
Flask==3.1.2
requests==2.32.3
```

## 9. 常见安全漏洞

### 9.1 CSRF防护

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# 在表单中使用
<form method="POST">
    {{ csrf_token() }}
    <!-- 表单内容 -->
</form>
```

### 9.2 路径遍历防护

```python
import os

def safe_path(base_path, user_path):
    """防止路径遍历攻击"""
    # 规范化路径
    full_path = os.path.normpath(os.path.join(base_path, user_path))
    
    # 确保路径在基础目录内
    if not full_path.startswith(os.path.abspath(base_path)):
        raise ValueError("Invalid path")
    
    return full_path
```

### 9.3 反序列化安全

```python
import pickle

# 危险：不要反序列化不可信数据
# data = pickle.loads(untrusted_data)

# 安全：使用JSON
import json
data = json.loads(untrusted_data)
```

## 10. 安全最佳实践

1. **输入验证**：始终验证和清理用户输入
2. **参数化查询**：使用参数化查询防止SQL注入
3. **密码哈希**：使用强密码哈希算法
4. **HTTPS**：生产环境使用HTTPS
5. **最小权限**：遵循最小权限原则
6. **依赖更新**：定期更新依赖包
7. **安全审计**：定期进行安全审计
8. **错误处理**：不要泄露敏感信息

## 11. 总结

Python安全编程需要关注：
- **输入验证**：防止注入攻击
- **认证授权**：用户身份验证和权限控制
- **数据加密**：敏感数据加密
- **安全配置**：安全的最佳实践
- **供应链安全**：依赖审计和版本锁定

遵循安全最佳实践可以保护应用免受常见攻击。

## 12. OWASP Top 10 2025 与 Python 安全

> 🔄 更新于 2026-05-02

OWASP Top 10 在 2025 年发布了新版本，相比 2021 版有重大变化。以下是与 Python 开发者最相关的更新。来源：[Talk Python #545 - OWASP Top 10 2025](https://talkpython.fm/episodes/show/545/owasp-top-10-2025-list-for-python-devs)

### 12.1 2025 版关键变化

| 排名 | 2025 版 | 变化 |
|------|---------|------|
| A01 | Broken Access Control | 保持第一 |
| A02 | Cryptographic Failures | 保持 |
| A03 | **Software Supply Chain Failures** | **新增**（原 A06 拆分+扩展） |
| A04 | Injection | 从 A03 降至 A04 |
| A05 | Insecure Design | 保持 |
| A06 | Security Misconfiguration | 保持 |
| A07 | **Exceptional Condition Handling** | **新增**（替代 XSS 独立项） |
| A08 | Server-Side Request Forgery | 保持 |
| A09 | Security Logging & Monitoring | 保持 |
| A10 | **Unsafe Consumption of APIs** | **新增** |

### 12.2 供应链安全（A03）— Python 重点

供应链攻击已成为 Python 生态最大威胁之一。PyPI 在 2025 年完成了第二次外部安全审计（Trail of Bits），发现 14 个问题（2 个高危）。来源：[PyPI Second Security Audit](https://pydevtools.com/blog/pypi-second-security-audit/)

```python
# 2026 年推荐的 Python 供应链安全实践

# 1. 在 CI 中集成 pip-audit（PyPA 官方工具）
# pyproject.toml
# [tool.pytest.ini_options]
# 添加 pip-audit 作为测试步骤

# 2. 使用 uv 的 --exclude-newer 延迟安装新包
# 避免安装发布不到一周的包，等待社区发现问题
# uv pip compile --exclude-newer "1 week" requirements.in

# 3. 锁定依赖哈希
# uv pip compile --generate-hashes requirements.in -o requirements.txt

# 4. CI 配置示例（GitHub Actions）
# .github/workflows/security.yml
# - name: Audit dependencies
#   run: |
#     pip install pip-audit
#     pip-audit --strict --desc
```

来源：[Python Supply Chain Security Made Easy](https://mkennedy.codes/posts/python-supply-chain-security-made-easy/)

### 12.3 异常条件处理（A07）— Python 常见问题

```python
# ❌ 危险：裸捕获异常后返回默认值
def get_user_balance(user_id):
    try:
        return db.query(f"SELECT balance FROM accounts WHERE id = {user_id}")
    except Exception:
        return 0  # 静默失败，可能掩盖安全问题

# ✅ 安全：明确处理异常类型，记录日志
def get_user_balance(user_id: int) -> Decimal:
    try:
        result = db.execute(
            text("SELECT balance FROM accounts WHERE id = :id"),
            {"id": user_id}
        )
        row = result.fetchone()
        if row is None:
            raise ValueError(f"用户 {user_id} 不存在")
        return row.balance
    except SQLAlchemyError as e:
        logger.error(f"数据库查询失败: user_id={user_id}", exc_info=True)
        raise
```

### 12.4 2026 年 Python 安全工具链

| 工具 | 用途 | 推荐度 |
|------|------|--------|
| **pip-audit** | 依赖漏洞扫描（OSV + PyPI） | ⭐⭐⭐ 必备 |
| **uv** | 包管理 + 哈希锁定 + --exclude-newer | ⭐⭐⭐ 必备 |
| **Ruff** | 安全相关 lint 规则（S 系列） | ⭐⭐⭐ 必备 |
| **Bandit** | Python 静态安全分析 | ⭐⭐ 推荐 |
| **safety** | 依赖漏洞扫描（Safety DB） | ⭐⭐ 补充 |
| **Semgrep** | 自定义安全规则扫描 | ⭐⭐ 大型项目 |
| **Sigstore** | 包签名验证 | ⭐ 前沿 |

## 13. 2026 年 Python 供应链攻击事件

> 🔄 更新于 2026-05-12

2026 年 Q1-Q2 发生了多起严重的 Python 供应链攻击，凸显了依赖安全的紧迫性。

### 13.1 PyTorch Lightning 攻击（2026-04-30）

PyPI 包 `lightning`（PyTorch Lightning，31K+ GitHub Stars）被注入恶意代码，影响版本 2.6.2 和 2.6.3。攻击者在包中隐藏了 `_runtime` 目录，包含下载器和混淆的 JavaScript payload，自动执行凭证窃取。该攻击属于"Mini Shai-Hulud"跨生态系统供应链攻击的一部分，同时影响了 Python（lightning）、Node.js（intercom-client）和 PHP 生态。

**影响**：窃取开发者凭证、API Key，并尝试横向传播到其他包。PyPI 已将该项目隔离。

来源：[The Hacker News](https://thehackernews.com/2026/04/pytorch-lightning-compromised-in-pypi.html)、[Snyk](https://snyk.io/blog/lightning-pypi-compromise-bun-based-credential-stealer/)、[OX Security](https://www.ox.security/blog/lightning-python-package-shai-hulud-supply-chain-attack/)

### 13.2 LiteLLM 攻击（2026-03-24）

`litellm`——几乎所有主流 AI Agent 框架的底层依赖——被注入恶意代码，影响版本 1.82.x。由于 LiteLLM 是 LangChain、CrewAI、AutoGen 等框架的间接依赖，攻击面极广。

来源：[Comet Blog](https://www.comet.com/site/blog/litellm-supply-chain-attack/)、[HeroDevs](https://www.herodevs.com/blog-posts/the-litellm-supply-chain-attack-what-happened-why-it-matters-and-what-to-do-next)

### 13.3 防护建议

```python
# 2026 年 Python 供应链安全加固清单

# 1. 锁定依赖哈希（最重要）
# uv pip compile --generate-hashes requirements.in -o requirements.txt

# 2. 延迟安装新版本（等待社区发现问题）
# uv pip compile --exclude-newer "3 days" requirements.in

# 3. CI 中集成多层审计
# .github/workflows/security.yml
# jobs:
#   audit:
#     steps:
#       - run: pip-audit --strict --desc
#       - run: uv pip audit
#       - run: safety check --full-report

# 4. 监控关键依赖的发布（特别是 AI 相关包）
# 高风险包清单（2026 年已被攻击或尝试攻击）：
#   - lightning (PyTorch Lightning)
#   - litellm
#   - langchain-*
#   - openai
#   - anthropic

# 5. 使用 Sigstore 验证包签名（如果可用）
# pip install --require-hashes --verify-signatures -r requirements.txt
```

### 13.4 2026 年 Python CVE 统计

截至 2026-05-12，CPython 本身有 9 个 CVE，Python 生态（含第三方包）有 21 个 CVE，平均 CVSS 评分 5.8。值得关注的高危 CVE：

| CVE | 影响 | CVSS | 描述 |
|-----|------|------|------|
| CVE-2026-5752 | Cohere Terrarium | 9.3 | 沙箱逃逸，任意代码执行 |
| CVE-2026-41140 | Poetry | — | tar 解压路径遍历（Python 3.10.0-3.10.12） |
| CVE-2026-21531 | Azure SDK for Python | — | 远程代码执行 |

来源：[stack.watch Python CVEs 2026](https://stack.watch/product/python/)、[The Hacker News](https://thehackernews.com/search/label/Python)

