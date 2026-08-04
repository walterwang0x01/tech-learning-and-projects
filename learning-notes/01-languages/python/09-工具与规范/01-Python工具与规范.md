# Python工具与规范
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 虚拟环境

### 1.1 venv（Python 3.3+）

```bash
# 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate

# Linux/Mac激活
source venv/bin/activate

# 停用虚拟环境
deactivate
```

### 1.2 virtualenv

```bash
# 安装
pip install virtualenv

# 创建虚拟环境
virtualenv venv

# 激活（同上）
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

### 1.3 conda

```bash
# 创建虚拟环境
conda create -n myenv python=3.9

# 激活
conda activate myenv

# 停用
conda deactivate

# 列出环境
conda env list

# 删除环境
conda env remove -n myenv
```

## 2. 包管理

### 2.1 pip

```bash
# 安装包
pip install package_name
pip install package_name==1.0.0
pip install package_name>=1.0.0

# 从requirements.txt安装
pip install -r requirements.txt

# 生成requirements.txt
pip freeze > requirements.txt

# 升级包
pip install --upgrade package_name

# 卸载包
pip uninstall package_name

# 列出已安装的包
pip list

# 显示包信息
pip show package_name
```

### 2.2 pipenv

```bash
# 安装
pip install pipenv

# 创建虚拟环境并安装依赖
pipenv install

# 安装开发依赖
pipenv install --dev

# 激活虚拟环境
pipenv shell

# 运行命令
pipenv run python app.py

# 生成Pipfile.lock
pipenv lock
```

### 2.3 poetry

```bash
# 安装
pip install poetry

# 初始化项目
poetry init

# 安装依赖
poetry install

# 添加依赖
poetry add package_name
poetry add --dev package_name

# 更新依赖
poetry update

# 运行命令
poetry run python app.py
```

## 3. 代码规范

### 3.1 PEP 8

Python官方代码风格指南，主要规则：

```python
# 缩进：使用4个空格
def function():
    pass

# 行长度：每行不超过79字符
long_variable_name = (
    "这是一个很长的字符串"
    "需要换行"
)

# 导入顺序
import os
import sys

from third_party import library
from local_module import function

# 命名规范
# 类名：大驼峰
class MyClass:
    pass

# 函数和变量：小写下划线
def my_function():
    my_variable = 1

# 常量：全大写下划线
MY_CONSTANT = 100
```

### 3.2 代码检查工具

#### pylint

```bash
# 安装
pip install pylint

# 检查代码
pylint module.py

# 生成配置文件
pylint --generate-rcfile > .pylintrc
```

#### flake8

```bash
# 安装
pip install flake8

# 检查代码
flake8 module.py

# 配置文件 .flake8
[flake8]
max-line-length = 88
exclude = .git,__pycache__,venv
```

#### black（代码格式化）

```bash
# 安装
pip install black

# 格式化代码
black module.py

# 检查格式
black --check module.py
```

#### autopep8

```bash
# 安装
pip install autopep8

# 格式化代码
autopep8 --in-place module.py

# 检查格式
autopep8 --diff module.py
```

### 3.3 类型检查

#### mypy

```bash
# 安装
pip install mypy

# 类型检查
mypy module.py

# 配置文件 pyproject.toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
```

#### 类型注解示例

```python
from typing import List, Dict, Optional, Union

def process_data(
    items: List[str],
    config: Dict[str, int],
    optional: Optional[str] = None
) -> Union[str, int]:
    if optional:
        return optional
    return len(items)
```

## 4. 文档工具

### 4.1 Sphinx

```bash
# 安装
pip install sphinx

# 初始化文档
sphinx-quickstart

# 生成文档
make html
```

### 4.2 docstring规范

```python
def function(param1: str, param2: int) -> bool:
    """
    函数简短描述
    
    详细描述函数的功能、参数、返回值等。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
    
    Returns:
        返回值的描述
    
    Raises:
        ValueError: 当参数无效时抛出
    
    Example:
        >>> function('test', 123)
        True
    """
    return True
```

## 5. 开发工具

### 5.1 IPython

```bash
# 安装
pip install ipython

# 使用
ipython
```

### 5.2 Jupyter

```bash
# 安装
pip install jupyter

# 启动
jupyter notebook
jupyter lab
```

### 5.3 调试工具

#### pdb

```python
import pdb

def function():
    pdb.set_trace()  # 设置断点
    # 代码
```

#### ipdb

```bash
pip install ipdb

# 使用
import ipdb
ipdb.set_trace()
```

## 6. 项目管理

### 6.1 项目结构

```
project/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── src/
│   └── package/
│       ├── __init__.py
│       └── module.py
├── tests/
│   ├── __init__.py
│   └── test_module.py
└── docs/
    └── conf.py
```

### 6.2 setup.py

```python
from setuptools import setup, find_packages

setup(
    name='myproject',
    version='0.1.0',
    description='项目描述',
    author='作者',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
    ],
    python_requires='>=3.7',
)
```

### 6.3 .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 测试
.pytest_cache/
.coverage
htmlcov/

# 其他
.DS_Store
*.log
```

## 7. 性能分析

### 7.1 cProfile

```python
import cProfile
import pstats

def function():
    # 代码
    pass

# 性能分析
profiler = cProfile.Profile()
profiler.enable()
function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

### 7.2 line_profiler

```bash
# 安装
pip install line_profiler

# 使用装饰器
@profile
def function():
    pass

# 运行
kernprof -l -v script.py
```

### 7.3 memory_profiler

```bash
# 安装
pip install memory_profiler

# 使用
@profile
def function():
    pass

# 运行
python -m memory_profiler script.py
```

## 8. 日志

### 8.1 logging模块

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# 使用
logger = logging.getLogger(__name__)
logger.info('信息')
logger.warning('警告')
logger.error('错误')
```

### 8.2 日志配置

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## 9. 安全工具

### 9.1 bandit

```bash
# 安装
pip install bandit

# 安全检查
bandit -r src/
```

### 9.2 safety

```bash
# 安装
pip install safety

# 检查依赖漏洞
safety check
```

## 10. 持续集成

### 10.1 GitHub Actions示例

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest flake8 black
      - name: Lint
        run: flake8 .
      - name: Format check
        run: black --check .
      - name: Test
        run: pytest
```

## 11. 最佳实践

1. **使用虚拟环境**：隔离项目依赖
2. **遵循PEP 8**：保持代码风格一致
3. **编写文档**：清晰的文档和注释
4. **编写测试**：确保代码质量
5. **使用类型注解**：提高代码可读性
6. **代码审查**：使用工具检查代码质量
7. **版本控制**：使用Git管理代码
8. **依赖管理**：使用requirements.txt或poetry

## 12. 总结

Python开发工具链：
- **虚拟环境**：venv、virtualenv、conda
- **包管理**：pip、pipenv、poetry
- **代码规范**：pylint、flake8、black
- **类型检查**：mypy
- **测试**：pytest、unittest
- **文档**：Sphinx
- **性能分析**：cProfile、line_profiler

合理使用这些工具可以提高开发效率和代码质量。

