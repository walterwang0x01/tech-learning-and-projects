# Django 高级特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> Django 框架的高级功能和最佳实践

## 1. Django 中间件

### 1.1 自定义中间件

```python
# middleware.py
class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 请求处理前
        print(f"请求路径: {request.path}")
        
        response = self.get_response(request)
        
        # 响应处理后
        response['X-Custom-Header'] = 'Custom Value'
        return response
```

### 1.2 中间件注册

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'myapp.middleware.CustomMiddleware',
    # ...
]
```

## 2. Django 信号

### 2.1 内置信号

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    print(f"保存前: {instance.username}")

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"新用户创建: {instance.username}")
    else:
        print(f"用户更新: {instance.username}")
```

### 2.2 自定义信号

<!-- 修复于 2026-05-21: providing_args 在 Django 4.0 中已移除 -->

```python
from django.dispatch import Signal

# Django 4.0+ 不再支持 providing_args 参数
order_created = Signal()

# 发送信号
order_created.send(sender=self.__class__, order=order, user=user)

# 接收信号
@receiver(order_created)
def handle_order_created(sender, order, user, **kwargs):
    print(f"订单创建: {order.id} by {user.username}")
```

## 3. Django 缓存

### 3.1 缓存配置

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3.2 缓存使用

```python
from django.core.cache import cache

# 设置缓存
cache.set('key', 'value', timeout=300)

# 获取缓存
value = cache.get('key')

# 删除缓存
cache.delete('key')

# 装饰器缓存
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 缓存15分钟
def my_view(request):
    return HttpResponse("Hello")
```

## 4. Django REST Framework

### 4.1 序列化器

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']
    
    def validate_email(self, value):
        if not value.endswith('@example.com'):
            raise serializers.ValidationError("邮箱格式不正确")
        return value
```

### 4.2 视图集

```python
from rest_framework import viewsets
from rest_framework.decorators import action

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'activated'})
```

## 5. Django 管理后台

### 5.1 自定义Admin

```python
from django.contrib import admin

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'date_joined']
    list_filter = ['is_active', 'date_joined']
    search_fields = ['username', 'email']
    readonly_fields = ['date_joined']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email')
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff')
        }),
    )
```

## 6. Django 任务队列

### 6.1 Celery 集成

```python
# tasks.py
from celery import shared_task

@shared_task
def send_email_task(user_id, message):
    user = User.objects.get(id=user_id)
    send_mail(
        '通知',
        message,
        'from@example.com',
        [user.email],
    )
```

### 6.2 Django 6.0 内置后台任务框架

> 🔄 更新于 2026-04-30

<!-- version-check: Django 6.0.6, django.tasks framework, checked 2026-05-21 -->

Django 6.0 引入了内置的 Tasks 框架（`django.tasks`），无需 Celery 即可处理简单的后台任务。这是 Django 历史上最受期待的功能之一。

```python
# tasks.py — Django 6.0 内置后台任务
from django.tasks import task

@task()
def send_welcome_email(user_id: int):
    """后台发送欢迎邮件"""
    user = User.objects.get(id=user_id)
    send_mail(
        '欢迎加入',
        f'你好 {user.username}，欢迎使用我们的服务！',
        'noreply@example.com',
        [user.email],
    )

@task()
def process_uploaded_file(file_id: int):
    """后台处理上传的文件"""
    file = UploadedFile.objects.get(id=file_id)
    # 耗时的文件处理逻辑
    file.status = 'processed'
    file.save()
```

```python
# views.py — 在视图中调用后台任务
from .tasks import send_welcome_email, process_uploaded_file

def register(request):
    user = User.objects.create_user(...)
    # 将任务加入队列，不阻塞请求
    send_welcome_email.enqueue(user.id)
    return JsonResponse({'status': 'ok'})

def upload(request):
    file = handle_upload(request.FILES['file'])
    # 后台处理文件
    result = process_uploaded_file.enqueue(file.id)
    # 可以通过 result.id 追踪任务状态
    return JsonResponse({'task_id': str(result.id)})
```

```python
# settings.py — 任务后端配置
TASKS = {
    'default': {
        'BACKEND': 'django.tasks.backends.immediate.ImmediateBackend',
        # 开发环境：立即执行（同步）
    }
}

# 生产环境需要配置实际的任务后端（如 django-tasks-database）
# TASKS = {
#     'default': {
#         'BACKEND': 'django_tasks_database.DatabaseBackend',
#     }
# }
# 然后运行 worker：python manage.py db_worker
```

**Django Tasks vs Celery 选型**：

| 特性 | Django Tasks | Celery |
|------|-------------|--------|
| 安装复杂度 | 零依赖（内置） | 需要 Broker（Redis/RabbitMQ） |
| 适用场景 | 简单后台任务 | 复杂工作流、定时任务、分布式 |
| 定时任务 | ❌ 不支持（需第三方扩展） | ✅ Celery Beat |
| 任务重试 | 基础支持 | 完整重试策略 |
| 监控 | ❌ 无内置 UI | ✅ Flower 监控面板 |
| 推荐场景 | 邮件发送、文件处理、简单通知 | 大规模任务、ETL、定时调度 |

> ⚠️ Django Tasks 框架只负责任务定义和入队，不提供 Worker 机制。生产环境需要配置第三方后端（如 `django-tasks-database`）并运行 Worker 进程。

> 来源：[Django Tasks Framework](https://docs.djangoproject.com/en/dev/topics/tasks/)、[Django 6.0 Release Notes](https://docs.djangoproject.com/en/dev/releases/6.0/)

## 7. Django 6.0 CSP 支持

> 🔄 更新于 2026-04-30

Django 6.0 内置了 Content Security Policy（CSP）支持，无需 `django-csp` 第三方库。

```python
# settings.py — Django 6.0 CSP 配置
CONTENT_SECURITY_POLICY = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "https://cdn.example.com"],
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "https:"],
    "connect-src": ["'self'", "https://api.example.com"],
}

# 启用 CSP 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csp.ContentSecurityPolicyMiddleware',  # Django 6.0 新增
    # ...
]
```

> 来源：[Django 6.0 CSP Support](https://docs.djangoproject.com/en/dev/releases/6.0/)

## 8. 总结

Django高级特性要点：
- **中间件**：请求/响应处理、自定义中间件
- **信号**：模型信号、自定义信号
- **缓存**：Redis缓存、视图缓存、装饰器缓存
- **DRF**：序列化器、视图集、权限控制
- **管理后台**：自定义Admin、列表显示、过滤器
- **任务队列**：Celery异步任务

这些特性提高Django应用的性能和可维护性。

