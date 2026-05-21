# Flask 高级特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> Flask 框架的高级功能和扩展应用

## 1. Flask 蓝图（Blueprint）

### 1.1 创建蓝图

```python
# blueprints/api.py
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/users')
def get_users():
    return {'users': []}

@api_bp.route('/users/<int:user_id>')
def get_user(user_id):
    return {'user_id': user_id}
```

### 1.2 注册蓝图

```python
# app.py
from flask import Flask
from blueprints.api import api_bp

app = Flask(__name__)
app.register_blueprint(api_bp)
```

## 2. Flask 应用工厂

### 2.1 工厂模式

```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(f'app.config.{config_name}')
    
    db.init_app(app)
    
    from app.blueprints import api_bp
    app.register_blueprint(api_bp)
    
    return app
```

## 3. Flask 扩展

### 3.1 Flask-SQLAlchemy

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
```

### 3.2 Flask-Migrate

```python
from flask_migrate import Migrate

migrate = Migrate(app, db)

# 命令行
# flask db init
# flask db migrate -m "Initial migration"
# flask db upgrade
```

### 3.3 Flask-Login

```python
from flask_login import LoginManager, login_user, logout_user, login_required

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and user.check_password(request.form['password']):
        login_user(user)
        return redirect(url_for('index'))
    return 'Invalid credentials'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
```

## 4. Flask 上下文

### 4.1 应用上下文

```python
from flask import current_app, g

@app.before_request
def before_request():
    g.db = get_db_connection()

@app.route('/')
def index():
    db = g.db
    # 使用数据库连接
    return 'Hello'
```

## 5. Flask 错误处理

### 5.1 错误处理器

```python
@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {'error': 'Internal error'}, 500
```

## 6. Flask 测试

### 6.1 单元测试

```python
import unittest
from app import create_app, db

class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```

## 7. Flask 部署

### 7.1 Gunicorn 配置

```python
# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
timeout = 120
```

```bash
gunicorn -c gunicorn_config.py app:app
```

## 8. 总结

Flask高级特性要点：
- **蓝图**：模块化应用、URL前缀
- **应用工厂**：配置管理、扩展初始化
- **扩展**：SQLAlchemy、Migrate、Login
- **上下文**：应用上下文、请求上下文
- **错误处理**：自定义错误处理器
- **测试**：单元测试、测试客户端
- **部署**：Gunicorn、WSGI服务器

这些特性使Flask应用更加模块化和可维护。

## 9. Flask 3.1.x 版本演进

<!-- version-check: Flask 3.1.3, checked 2026-05-21 -->

> 🔄 更新于 2026-05-21

<!-- 修复于 2026-05-21: Flask 3.1.2 → 3.1.3 -->
Flask 3.1.3 是当前稳定版（2026-04）。来源：[A Year In Review: Flask in 2025](https://blog.miguelgrinberg.com/post/a-year-in-review-flask-in-2025)

### 9.1 Flask 3.1.x 新特性

- **密钥轮换**：`SECRET_KEY_FALLBACKS` 支持平滑轮换密钥，旧 session 仍可验证
- **Partitioned Cookie（CHIPS）**：支持 Chrome 的第三方 Cookie 分区策略
- **资源限制**：`MAX_FORM_MEMORY_SIZE` 控制表单内存上限
- **Python 版本**：要求 Python ≥ 3.9，不再支持 3.8
- **依赖要求**：Werkzeug ≥ 3.x

### 9.2 异步视图支持

Flask 3.x 支持 `async` 视图函数（需安装 `asgiref`）：

```python
@app.route('/async-data')
async def async_data():
    # 异步操作
    data = await fetch_from_api()
    return {'data': data}
```

### 9.3 2026 年 Flask 生态建议

| 场景 | 推荐方案 |
|------|---------|
| 新 API 项目 | FastAPI（原生异步、自动文档） |
| 轻量级 Web 应用 | Flask 3.1.x |
| 全栈 Web 应用 | Django 6.0 |
| 已有 Flask 项目 | 继续使用 Flask 3.1.x，无需迁移 |

Flask 在 2026 年保持稳定但迭代缓慢，新项目如需高性能异步 API 建议优先考虑 FastAPI。

