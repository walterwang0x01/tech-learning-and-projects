# 集成测试与 Mock
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 学习如何进行集成测试和使用 Mock 对象

## 1. 集成测试概述

集成测试验证多个组件协同工作：
- API 端点测试
- 数据库集成测试
- 外部服务集成测试
- 端到端测试

## 2. FastAPI 集成测试

### 2.1 TestClient 使用

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_users():
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_user():
    response = client.post(
        "/api/users/",
        json={"username": "test", "email": "test@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "test"
```

### 2.2 数据库集成测试

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# 测试数据库
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_user_integration(client):
    response = client.post(
        "/api/users/",
        json={"username": "test", "email": "test@example.com"}
    )
    assert response.status_code == 201
    
    # 验证数据库
    response = client.get("/api/users/")
    assert len(response.json()) == 1
```

## 3. Mock 对象

### 3.1 unittest.mock

```python
from unittest.mock import Mock, MagicMock, patch

# 创建Mock对象
mock_obj = Mock()
mock_obj.method.return_value = 42
assert mock_obj.method() == 42

# 验证调用
mock_obj.method.assert_called_once()
```

### 3.2 装饰器方式

```python
from unittest.mock import patch

@patch('module.external_api')
def test_function(mock_api):
    mock_api.get_data.return_value = {"data": "test"}
    result = function_under_test()
    assert result == "test"
    mock_api.get_data.assert_called_once()
```

### 3.3 上下文管理器

```python
with patch('module.external_service') as mock_service:
    mock_service.call.return_value = "mocked"
    result = function_that_uses_service()
    assert result == "mocked"
```

## 4. pytest-mock

### 4.1 使用 fixture

```python
import pytest

def test_with_mock(mocker):
    mock_func = mocker.patch('module.external_function')
    mock_func.return_value = "mocked"
    
    result = function_under_test()
    assert result == "mocked"
    mock_func.assert_called_once()
```

### 4.2 Mock 外部API

```python
import requests
from unittest.mock import patch

@patch('requests.get')
def test_api_call(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    response = requests.get("https://api.example.com/data")
    assert response.json()["status"] == "ok"
```

## 5. 数据库 Mock

### 5.1 使用内存数据库

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

### 5.2 Mock 数据库操作

```python
from unittest.mock import Mock, patch

@patch('app.database.get_db')
def test_user_creation(mock_get_db):
    mock_db = Mock()
    mock_get_db.return_value = mock_db
    
    create_user("test", "test@example.com")
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

## 6. 异步测试

### 6.1 pytest-asyncio

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == "expected"

@pytest.mark.asyncio
async def test_async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/users/")
        assert response.status_code == 200
```

## 7. 测试覆盖率

### 7.1 pytest-cov

```bash
# 安装
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看覆盖率
pytest --cov=app --cov-report=term-missing
```

### 7.2 覆盖率配置

```ini
# pytest.ini
[tool:pytest]
addopts = --cov=app --cov-report=html --cov-report=term
```

## 8. 测试最佳实践

### 8.1 测试组织

```
tests/
├── __init__.py
├── conftest.py          # 共享fixtures
├── test_api/
│   ├── test_users.py
│   └── test_orders.py
├── test_models/
│   └── test_user.py
└── test_utils/
    └── test_helpers.py
```

### 8.2 Fixture 共享

```python
# conftest.py
import pytest
from app.database import get_db

@pytest.fixture
def test_db():
    # 测试数据库配置
    pass

@pytest.fixture
def test_client(test_db):
    # 测试客户端
    pass
```

## 9. 总结

集成测试和Mock要点：
- **集成测试**：验证组件协同工作
- **TestClient**：API端点测试
- **Mock对象**：隔离外部依赖
- **数据库测试**：使用测试数据库
- **异步测试**：pytest-asyncio
- **覆盖率**：pytest-cov监控
- **最佳实践**：组织测试结构

良好的测试实践确保代码质量。

