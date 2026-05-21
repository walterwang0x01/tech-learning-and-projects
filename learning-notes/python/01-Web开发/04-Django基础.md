# Django基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Django概述

Django 是一个用 Python 编写的开源 Web 应用框架，采用了 MTV（Model-Template-View）的设计模式。Django 框架诞生于2003年，由劳伦斯出版集团旗下在线新闻网站的内容管理系统（CMS）研发团队开发，以比利时的吉普赛爵士吉他手 Django Reinhardt 来命名。

### 1.1 Django的特点

- **快速开发**：Django 的设计理念是 DRY（Don't Repeat Yourself），减少重复代码
- **功能完备**：内置了用户认证、内容管理、RSS 等常用功能
- **安全可靠**：内置了 SQL 注入、XSS、CSRF 等安全防护
- **可扩展性强**：支持插件和中间件扩展

### 1.2 MTV架构

Django 采用 MTV（Model-Template-View）架构模式：

- **Model（模型）**：负责数据结构和数据库操作
- **Template（模板）**：负责展示数据，即 HTML 页面
- **View（视图）**：负责业务逻辑，处理请求并返回响应

MTV 架构与传统的 MVC 架构对应关系：
- Model = Model（模型）
- Template = View（视图）
- View = Controller（控制器）

## 2. 安装和配置

### 2.1 安装Django

```bash
pip install django
# 或指定版本
pip install django==4.2.0
```

### 2.2 检查Django版本

```bash
django-admin --version
```

### 2.3 Python和Django版本对应关系

| Django版本 | Python版本                                |
| ---------- | ----------------------------------------- |
| 2.0        | 3.4、3.5、3.6、3.7                        |
| 2.1        | 3.5、3.6、3.7                             |
| 2.2        | 3.5、3.6、3.7、3.8                        |
| 3.0        | 3.6、3.7、3.8                             |
| 3.1        | 3.6、3.7、3.8、3.9                        |
| 3.2        | 3.6、3.7、3.8、3.9、3.10                  |
| 4.0        | 3.8、3.9、3.10                            |
| 4.1        | 3.8、3.9、3.10、3.11                      |
| 4.2        | 3.8、3.9、3.10、3.11                      |
| 5.2 (LTS)  | 3.10、3.11、3.12、3.13、3.14              |
| **6.0**    | **3.12、3.13、3.14**                      |

> 🔄 更新于 2026-04-18

<!-- version-check: Django 6.0.6, checked 2026-05-21 -->

### 2.4 Django 版本演进与选择

| 版本 | 发布日期 | 支持状态 | 说明 |
|------|---------|---------|------|
| 5.2 LTS | 2025-04 | LTS 支持至 2028-04 | 最后支持 Python 3.10/3.11 的版本 |
| **6.0** | **2025-12** | **当前稳定版** | 内置后台任务、CSP 支持、模板 Partials |
| 6.1 | 2026-08（预计） | 开发中 | — |

#### Django 6.0 核心新特性

**1. 内置后台任务框架（Background Tasks）**

不再需要为简单的后台任务强制引入 Celery：

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django.contrib.tasks',
]

# 定义后台任务
from django.tasks import task

@task()
def send_welcome_email(user_id):
    """后台发送欢迎邮件"""
    user = User.objects.get(id=user_id)
    # 发送邮件逻辑...

# 在视图中调用
def register(request):
    user = User.objects.create(...)
    send_welcome_email.enqueue(user.id)  # 异步执行
    return redirect('home')
```

**2. 内置 Content Security Policy（CSP）支持**

原生支持 CSP 标准，防护 XSS 等内容注入攻击：

```python
# settings.py
MIDDLEWARE = [
    ...
    'django.middleware.security.ContentSecurityPolicyMiddleware',
]

CONTENT_SECURITY_POLICY = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "'nonce'"],
    "style-src": ["'self'", "'nonce'"],
}
```

**3. 模板 Partials**

支持在模板文件内定义可复用的命名片段：

```html
{% partial "card" %}
  <div class="card">
    <h3>{{ title }}</h3>
    <p>{{ content }}</p>
  </div>
{% endpartial %}

{# 在同一模板或其他模板中复用 #}
{% render_partial "card" title="Hello" content="World" %}
```

**4. 现代化 Email API**

采用 Python 现代 `email` 库替代旧实现。

#### 版本选择建议

- **新项目**：直接使用 Django 6.0
- **保守升级**：Django 5.2 LTS（支持至 2028-04）
- **迁移路径**：5.x → 5.2 LTS → 6.0

> ⚠️ Django 5.1 已于 2025-12-31 EOL，不再接收安全补丁

> 来源：[Django 6.0 Release Notes](https://docs.djangoproject.com/en/stable/releases/6.0/)、[InfoQ 报道](https://www.infoq.com/news/2026/01/django-6-release/)

## 3. 创建Django项目

### 3.1 创建项目

```bash
django-admin startproject myproject
```

### 3.2 项目结构

创建项目后，会生成以下文件结构：

```
myproject/
├── manage.py              # Django项目管理脚本
└── myproject/             # 项目配置目录
    ├── __init__.py
    ├── settings.py        # 项目配置文件
    ├── urls.py            # URL路由配置
    ├── asgi.py            # ASGI配置（异步支持）
    └── wsgi.py            # WSGI配置（Web服务器接口）
```

### 3.3 重要文件说明

- **manage.py**：Django 项目的管理脚本，用于执行各种管理命令
- **settings.py**：项目的配置文件，包含数据库、应用、中间件等配置
- **urls.py**：URL 路由配置文件，定义 URL 与视图函数的映射关系
- **wsgi.py**：WSGI 兼容的 Web 服务器入口

### 3.4 运行开发服务器

```bash
python manage.py runserver
# 指定端口
python manage.py runserver 8080
# 指定IP和端口
python manage.py runserver 0.0.0.0:8000
```

## 4. 创建Django应用

### 4.1 创建应用

一个 Django 项目可以包含多个应用，每个应用负责特定的功能模块。

```bash
python manage.py startapp myapp
```

### 4.2 应用结构

创建应用后，会生成以下文件结构：

```
myapp/
├── __init__.py
├── admin.py          # 管理后台配置
├── apps.py           # 应用配置
├── models.py         # 数据模型（Model）
├── views.py          # 视图函数（View）
├── tests.py          # 测试文件
└── migrations/       # 数据库迁移文件
    └── __init__.py
```

### 4.3 注册应用

创建应用后，需要在 `settings.py` 中注册应用：

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # 注册应用
]
```

## 5. 视图（View）

### 5.1 基本视图函数

视图函数接收 HTTP 请求，返回 HTTP 响应。

```python
from django.http import HttpResponse

def index(request):
    return HttpResponse('<h1>Hello, Django!</h1>')
```

### 5.2 动态视图

```python
from django.http import HttpResponse
from random import sample

def show_fruits(request):
    fruits = ['Apple', 'Orange', 'Banana', 'Grape', 'Mango']
    selected = sample(fruits, 3)
    content = '<h3>今天推荐的水果：</h3><ul>'
    for fruit in selected:
        content += f'<li>{fruit}</li>'
    content += '</ul>'
    return HttpResponse(content)
```

### 5.3 URL配置

在项目的 `urls.py` 中配置 URL 路由：

```python
from django.contrib import admin
from django.urls import path
from myapp.views import index, show_fruits

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('fruits/', show_fruits),
]
```

## 6. 模板（Template）

### 6.1 创建模板目录

在项目根目录下创建 `templates` 文件夹。

### 6.2 配置模板路径

在 `settings.py` 中配置模板路径：

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 6.3 创建模板文件

创建 `templates/index.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>首页</title>
</head>
<body>
    <h1>今天推荐的水果：</h1>
    <hr>
    <ul>
        {% for fruit in fruits %}
        <li>{{ fruit }}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

### 6.4 渲染模板

使用 `render` 函数渲染模板：

```python
from django.shortcuts import render
from random import sample

def show_fruits(request):
    fruits = ['Apple', 'Orange', 'Banana', 'Grape', 'Mango']
    selected = sample(fruits, 3)
    return render(request, 'index.html', {'fruits': selected})
```

### 6.5 Django模板语法

#### 变量

```html
{{ variable }}
```

#### 标签

```html
{% if condition %}
    <!-- 内容 -->
{% endif %}

{% for item in items %}
    <!-- 内容 -->
{% endfor %}
```

#### 过滤器

```html
{{ name|upper }}
{{ date|date:"Y-m-d" }}
{{ text|truncatewords:10 }}
```

## 7. 模型（Model）

### 7.1 定义模型

在 `models.py` 中定义数据模型：

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.title
```

### 7.2 常用字段类型

- `CharField`：字符串字段
- `TextField`：大文本字段
- `IntegerField`：整数字段
- `FloatField`：浮点数字段
- `BooleanField`：布尔字段
- `DateField`：日期字段
- `DateTimeField`：日期时间字段
- `EmailField`：邮箱字段
- `URLField`：URL字段
- `ForeignKey`：外键字段
- `ManyToManyField`：多对多字段

### 7.3 数据库迁移

创建迁移文件：

```bash
python manage.py makemigrations
```

执行迁移：

```bash
python manage.py migrate
```

## 8. 管理后台

### 8.1 创建超级用户

```bash
python manage.py createsuperuser
```

### 8.2 注册模型

在 `admin.py` 中注册模型：

```python
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date']
    list_filter = ['pub_date']
    search_fields = ['title', 'content']
```

### 8.3 访问管理后台

启动服务器后，访问 `http://127.0.0.1:8000/admin/` 即可进入管理后台。

## 9. 静态文件

### 9.1 配置静态文件

在 `settings.py` 中配置静态文件：

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

### 9.2 使用静态文件

在模板中使用静态文件：

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

## 10. 表单处理

### 10.1 创建表单

```python
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='姓名')
    email = forms.EmailField(label='邮箱')
    message = forms.CharField(widget=forms.Textarea, label='留言')
```

### 10.2 处理表单

```python
from django.shortcuts import render, redirect
from .forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # 处理表单数据
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
```

## 11. 常用命令

```bash
# 创建项目
django-admin startproject projectname

# 创建应用
python manage.py startapp appname

# 运行开发服务器
python manage.py runserver

# 创建数据库迁移
python manage.py makemigrations

# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic

# 进入Django shell
python manage.py shell
```

## 12. 项目配置

### 12.1 语言和时区

在 `settings.py` 中配置：

```python
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True
```

### 12.2 数据库配置

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## 13. 最佳实践

1. **使用虚拟环境**：为每个项目创建独立的虚拟环境
2. **版本控制**：使用 Git 管理代码，添加 `.gitignore` 文件
3. **环境变量**：使用 `python-decouple` 或 `django-environ` 管理敏感配置
4. **代码规范**：遵循 PEP 8 代码规范
5. **测试**：编写单元测试和集成测试

## 14. 总结

Django 是一个功能强大的 Web 框架，采用 MTV 架构模式，提供了完整的 Web 开发解决方案。掌握 Django 的基础知识，包括项目创建、应用开发、模型定义、视图编写、模板使用等，是进行 Django Web 开发的基础。

## 15. 参考资源

- [Django 官方文档](https://docs.djangoproject.com/)
- [Django 中文文档](https://docs.djangoproject.com/zh-hans/)
- [Django 最佳实践](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
## 🎬 推荐视频资源

- [freeCodeCamp - Django Web Framework](https://www.youtube.com/watch?v=F5mRW0jo-U4) — Django完整课程
- [Corey Schafer - Django Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTtoQCKZ03TU5fNfx2UY6U4p) — Django系统教程系列
- [Dennis Ivy - Django Crash Course](https://www.youtube.com/watch?v=PtQiiknWUcI) — Django快速入门
### 📺 B站（Bilibili）
- [黑马程序员 - Django教程](https://www.bilibili.com/video/BV1vK4y1o7jH) — Django完整中文教程
- [刘江的Django教程](https://www.bilibili.com/video/BV1pE411q7Nj) — Django实战教程

### 🌐 其他平台
- [Django官方中文文档](https://docs.djangoproject.com/zh-hans/) — 官方中文文档
