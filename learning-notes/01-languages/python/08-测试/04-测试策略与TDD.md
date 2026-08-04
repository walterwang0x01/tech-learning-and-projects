# 测试策略与TDD
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 测试驱动开发（TDD）和测试策略

## 1. TDD 流程

### 1.1 红-绿-重构

```python
# 1. 红：编写失败的测试
def test_add():
    assert add(2, 3) == 5

# 2. 绿：编写最小实现使测试通过
def add(a, b):
    return a + b

# 3. 重构：优化代码
def add(a, b):
    """加法函数"""
    return a + b
```

## 2. 测试金字塔

### 2.1 测试层次

```python
# 单元测试（最多）
def test_user_model():
    user = User(username='test', email='test@example.com')
    assert user.username == 'test'

# 集成测试（中等）
def test_user_service():
    service = UserService()
    user = service.create_user('test', 'test@example.com')
    assert user.id is not None

# 端到端测试（最少）
def test_user_registration_flow():
    # 模拟完整用户注册流程
    pass
```

## 3. 测试策略

### 3.1 测试分类

```python
# 功能测试
def test_user_login():
    user = login('username', 'password')
    assert user.is_authenticated

# 性能测试
def test_query_performance():
    import time
    start = time.time()
    users = get_all_users()
    assert time.time() - start < 1.0

# 安全测试
def test_sql_injection():
    result = search_users("'; DROP TABLE users; --")
    assert 'DROP' not in result
```

### 3.2 测试覆盖率

```python
# pytest-cov
# pytest --cov=myapp --cov-report=html

# 目标覆盖率
# - 单元测试：80%+
# - 关键路径：100%
# - 整体：70%+
```

## 4. BDD 行为驱动开发

### 4.1 Gherkin 语法

```gherkin
Feature: 用户登录
  Scenario: 成功登录
    Given 用户已注册
    When 用户输入正确的用户名和密码
    Then 用户应该成功登录
```

### 4.2 Behave 实现

```python
# features/steps/login.py
from behave import given, when, then

@given('用户已注册')
def step_user_registered(context):
    context.user = create_user('test', 'password')

@when('用户输入正确的用户名和密码')
def step_user_login(context):
    context.result = login('test', 'password')

@then('用户应该成功登录')
def step_login_success(context):
    assert context.result.is_authenticated
```

## 5. 测试数据管理

### 5.1 Fixtures

```python
import pytest

@pytest.fixture
def user():
    return User(username='test', email='test@example.com')

@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.rollback()
    session.close()

def test_user_creation(user, db_session):
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### 5.2 工厂模式

```python
import factory

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

def test_user():
    user = UserFactory()
    assert user.email.endswith('@example.com')
```

## 6. 测试隔离

### 6.1 数据库隔离

```python
@pytest.fixture(autouse=True)
def reset_db():
    # 每个测试前重置数据库
    drop_all_tables()
    create_all_tables()
    yield
    drop_all_tables()
```

### 6.2 Mock 外部依赖

```python
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {'data': 'test'}
    result = fetch_api_data()
    assert result == {'data': 'test'}
```

## 7. 持续测试

### 7.1 自动化测试

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
```

## 8. 总结

测试策略与TDD要点：
- **TDD流程**：红-绿-重构循环
- **测试金字塔**：单元测试、集成测试、端到端测试
- **测试策略**：功能测试、性能测试、安全测试
- **BDD**：行为驱动开发、Gherkin语法
- **测试数据**：Fixtures、工厂模式
- **测试隔离**：数据库隔离、Mock外部依赖
- **持续测试**：CI/CD集成

良好的测试策略保证代码质量。

