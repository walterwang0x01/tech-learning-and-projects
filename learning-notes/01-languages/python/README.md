# Python 技术学习笔记
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> 本目录包含 Python 技术栈的学习笔记，按类别组织

## 📁 目录结构

```
python/
├── 00-Python基础/          # Python 语言基础（共20个文档）
│   ├── Python简介与安装.md          ✅ 已创建
│   ├── Python变量与数据类型.md      ✅ 已创建
│   ├── Python运算符.md              ✅ 已创建
│   ├── Python分支结构.md            ✅ 已创建
│   ├── Python循环结构.md            ✅ 已创建
│   ├── Python数据结构-列表.md       ✅ 已创建
│   ├── Python数据结构-元组.md       ✅ 已创建
│   ├── Python数据结构-字典.md       ✅ 已创建
│   ├── Python数据结构-集合.md       ✅ 已创建
│   ├── Python数据结构-字符串.md     ✅ 已创建
│   ├── Python函数.md                ✅ 已创建
│   ├── Python面向对象编程.md        ✅ 已创建
│   ├── Python异常处理.md            ✅ 已创建
│   ├── Python文件操作.md            ✅ 已创建
│   ├── Python正则表达式.md          ✅ 已创建
│   └── Python高级特性.md            ✅ 已创建
│
├── 01-Web开发/            # Web 开发框架
│   ├── FastAPI快速入门.md            ✅ 已创建
│   ├── FastAPI高级特性.md            ✅ 已创建
│   ├── RESTful API设计最佳实践.md    ✅ 已创建
│   ├── Django基础.md                 ✅ 已创建
│   ├── Django高级特性.md             ✅ 已创建
│   ├── Flask基础.md                  ✅ 已创建
│   ├── Flask高级特性.md               ✅ 已创建
│   ├── WebSocket实时通信.md          ✅ 已创建
│   ├── GraphQL应用开发.md            ✅ 已创建
│   └── API文档生成.md                ✅ 已创建
│
├── 02-数据分析/           # 数据分析与科学计算
│   ├── 数据分析概述.md               ✅ 已创建
│   ├── NumPy应用.md                  ✅ 已创建
│   ├── Pandas应用.md                 ✅ 已创建
│   ├── 数据可视化.md                 ✅ 已创建
│   ├── 数据清洗与预处理.md           ✅ 已创建
│   ├── 特征工程.md                   ✅ 已创建
│   ├── 时间序列分析.md               ✅ 已创建
│   └── 统计分析.md                   ✅ 已创建
│
├── 03-机器学习/           # 机器学习与AI
│   ├── 浅谈机器学习.md               ✅ 已创建
│   ├── RAG检索增强生成.md            ✅ 已创建
│   ├── LangChain框架应用.md          ✅ 已创建
│   ├── AI Agent开发实践.md           ✅ 已创建
│   ├── 大模型微调实践.md             ✅ 已创建
│   ├── 深度学习框架应用.md           ✅ 已创建
│   ├── 模型评估与验证.md             ✅ 已创建
│   ├── 超参数调优.md                 ✅ 已创建
│   └── 模型部署与服务化.md           ✅ 已创建
│
├── 04-并发编程/           # 并发编程
│   ├── Python并发编程.md             ✅ 已创建
│   ├── 线程池与进程池.md             ✅ 已创建
│   ├── 异步编程进阶.md               ✅ 已创建
│   └── 协程深入理解.md               ✅ 已创建
│
├── 05-网络编程/           # 网络编程
│   ├── Python网络编程.md             ✅ 已创建
│   ├── HTTP服务器开发.md             ✅ 已创建
│   ├── gRPC应用开发.md               ✅ 已创建
│   └── 网络协议深入.md               ✅ 已创建
│
├── 06-爬虫/               # 网络爬虫
│   ├── Python爬虫.md                 ✅ 已创建
│   ├── 反爬虫策略与应对.md           ✅ 已创建
│   ├── 分布式爬虫架构.md             ✅ 已创建
│   ├── 数据存储与管理.md             ✅ 已创建
│   └── 爬虫框架深入.md               ✅ 已创建
│
├── 07-数据库操作/         # 数据库操作
│   ├── Python数据库操作.md           ✅ 已创建
│   ├── 数据库连接池与事务管理.md     ✅ 已创建
│   ├── SQLAlchemy高级特性.md        ✅ 已创建
│   ├── 数据库优化.md                 ✅ 已创建
│   └── NoSQL数据库深入.md            ✅ 已创建
│
├── 08-测试/               # 测试
│   ├── Python测试.md                 ✅ 已创建
│   ├── 集成测试与Mock.md             ✅ 已创建
│   ├── 性能测试与压力测试.md         ✅ 已创建
│   └── 测试策略与TDD.md              ✅ 已创建
│
├── 09-工具与规范/         # 开发工具与代码规范
│   ├── Python工具与规范.md           ✅ 已创建
│   ├── 虚拟环境与包管理.md           ✅ 已创建
│   ├── 代码质量工具.md               ✅ 已创建
│   ├── 日志管理.md                   ✅ 已创建
│   └── 配置管理.md                   ✅ 已创建
│
├── 10-设计模式/           # 设计模式
│   ├── Python设计模式.md             ✅ 已创建
│   └── 设计模式实战案例.md           ✅ 已创建
│
├── 11-部署与运维/         # 部署与运维
│   ├── Python部署与运维.md           ✅ 已创建
│   ├── Kubernetes部署实践.md        ✅ 已创建
│   ├── CI_CD实践.md                  ✅ 已创建
│   └── 监控与日志.md                 ✅ 已创建
│
├── 12-性能优化/           # 性能优化
│   ├── Python性能优化.md             ✅ 已创建
│   ├── 性能分析工具.md               ✅ 已创建
│   ├── 内存优化技巧.md               ✅ 已创建
│   └── 缓存策略.md                   ✅ 已创建
│
├── 13-安全编程/           # 安全编程
│   ├── Python安全编程.md             ✅ 已创建
│   ├── 加密与认证.md                 ✅ 已创建
│   └── 常见漏洞防护.md               ✅ 已创建
│
├── 14-算法与数据结构/     # 算法与数据结构
│   ├── Python算法与数据结构.md       ✅ 已创建
│   ├── 经典算法实现.md               ✅ 已创建
│   └── 高级数据结构.md               ✅ 已创建
│
├── 15-消息队列/           # 消息队列
│   ├── Python消息队列.md             ✅ 已创建
│   └── 消息队列高级应用.md           ✅ 已创建
│
└── README.md              # 本文件
```

## 📚 内容说明

### Python 基础部分

**Python 语言特性**
- **Python简介与安装**：Python历史、优缺点、环境安装
- **Python变量与数据类型**：变量命名、基本数据类型、类型转换
- **Python运算符**：算术运算符、比较运算符、逻辑运算符、赋值运算符
- **Python分支结构**：if-elif-else、match-case、嵌套分支
- **Python循环结构**：for-in循环、while循环、break和continue、嵌套循环
- **Python数据结构-列表**：列表创建、索引切片、列表方法、列表推导式
- **Python数据结构-元组**：元组创建、元组操作、元组与列表的区别
- **Python数据结构-字典**：字典创建、字典操作、字典方法、字典推导式
- **Python数据结构-集合**：集合创建、集合运算、集合方法
- **Python数据结构-字符串**：字符串操作、字符串方法、字符串格式化
- **Python函数**：函数定义、参数类型、Lambda函数、装饰器、递归
- **Python面向对象编程**：类与对象、继承与多态、特殊方法、属性装饰器
- **Python异常处理**：try-except-finally、异常类型、自定义异常
- **Python文件操作**：文件读写、上下文管理器、CSV/Excel/JSON处理
- **Python正则表达式**：re模块、Pattern和Matcher、正则语法
- **Python高级特性**：生成器、迭代器、上下文管理器、装饰器进阶

### Web 开发部分

- **FastAPI快速入门**：FastAPI框架使用、API开发、异步支持
- **FastAPI高级特性**：依赖注入、中间件、WebSocket、文件处理、数据库集成、缓存、限流
- **RESTful API设计最佳实践**：REST原则、HTTP状态码、版本控制、认证授权、限流、错误处理
- **Django基础**：Django框架、模型、视图、模板
- **Django高级特性**：中间件、信号、缓存、DRF、管理后台、Celery任务队列
- **Flask基础**：Flask框架、路由、模板、蓝图
- **Flask高级特性**：蓝图、应用工厂、扩展（SQLAlchemy、Migrate、Login）、上下文、错误处理、测试、部署
- **WebSocket实时通信**：FastAPI WebSocket、Flask-SocketIO、Django Channels、aiohttp WebSocket、客户端实现
- **GraphQL应用开发**：Graphene框架、Schema定义、查询和变更、FastAPI集成、订阅、数据加载器
- **API文档生成**：FastAPI自动文档（Swagger UI、ReDoc）、Django DRF文档、Flask文档（Flask-RESTX、Flask-APIDoc）、OpenAPI规范、Sphinx文档、文档最佳实践

### 数据分析部分

- **数据分析概述**：数据分析流程、相关库介绍
- **NumPy应用**：数组操作、数学运算、数组索引
- **Pandas应用**：DataFrame操作、数据清洗、数据分析
- **数据可视化**：Matplotlib、Seaborn等可视化库
- **数据清洗与预处理**：缺失值处理、重复数据、异常值、数据标准化、特征工程、编码分类变量
- **特征工程**：特征选择、特征变换、特征创建、特征编码、相关性分析、特征重要性
- **时间序列分析**：时间序列数据处理、趋势分析、季节性分析、平稳性检验、ARIMA模型、Prophet模型、LSTM预测、异常检测
- **统计分析**：描述性统计（均值、中位数、标准差、分位数、偏度、峰度）、假设检验（t检验、卡方检验、ANOVA）、相关性分析（皮尔逊、斯皮尔曼）、回归分析、分布检验

### 机器学习部分

- **浅谈机器学习**：机器学习概述、算法分类、模型训练、AI发展史
- **RAG检索增强生成**：RAG实现、向量化、检索策略、LlamaIndex应用
- **LangChain框架应用**：LangChain核心概念、链和代理、数据连接、RAG实现
- **AI Agent开发实践**：Agent架构设计、ReAct Agent、Plan-and-Execute、记忆系统、工具系统
- **大模型微调实践**：LoRA微调、QLoRA微调、全量微调、数据准备、模型评估
- **深度学习框架应用**：TensorFlow基础、PyTorch基础、CNN实现、RNN/LSTM、迁移学习、模型保存加载
- **模型评估与验证**：评估指标（准确率、精确率、召回率、F1、ROC/AUC、MSE、MAE、R²）、交叉验证（K折、分层K折、留一法）、学习曲线、验证曲线
- **超参数调优**：网格搜索（GridSearchCV）、随机搜索（RandomizedSearchCV）、贝叶斯优化（Optuna）、参数重要性分析、早停策略、Keras Tuner
- **模型部署与服务化**：FastAPI模型服务、模型版本管理、TensorFlow Serving、TorchServe、MLflow模型服务、模型监控（性能监控、A/B测试）、批量预测

### 并发编程部分

- **Python并发编程**：多线程、多进程、异步编程（asyncio）基础
- **线程池与进程池**：ThreadPoolExecutor、ProcessPoolExecutor、性能对比、最佳实践
- **异步编程进阶**：异步上下文管理器、异步迭代器、异步队列、信号量和锁、超时和取消
- **协程深入理解**：生成器协程、async/await、协程调度、协程通信（异步队列、异步锁）、协程与线程、协程模式（生产者-消费者）

### 网络编程部分

- **Python网络编程**：Socket编程、HTTP客户端、WebSocket、FTP/SMTP
- **HTTP服务器开发**：http.server、Flask RESTful API、FastAPI、aiohttp异步服务器、Tornado、WebSocket服务器
- **gRPC应用开发**：Protocol Buffers、gRPC服务定义、服务端实现、客户端调用、流式传输
- **网络协议深入**：TCP/UDP编程、HTTP/HTTPS协议、DNS查询、网络扫描（端口扫描）

### 爬虫部分

- **Python爬虫**：requests、BeautifulSoup、Scrapy、Selenium基础
- **反爬虫策略与应对**：User-Agent检测、IP限制、Cookie和Session、JavaScript渲染、验证码处理、请求频率控制
- **分布式爬虫架构**：分布式架构设计、Redis队列管理、Celery分布式任务、Scrapy-Redis、数据去重、布隆过滤器
- **数据存储与管理**：文件存储（JSON、CSV）、数据库存储（SQLite、MongoDB）、数据去重、增量爬取、数据清洗、数据验证
- **爬虫框架深入**：Scrapy深入（项目结构、Pipeline、中间件）、分布式爬虫（Scrapy-Redis）、Selenium高级（无头浏览器、等待策略、反检测）、Playwright应用、数据解析技巧（XPath、CSS选择器）

### 数据库操作部分

- **Python数据库操作**：SQLAlchemy ORM、MongoDB、Redis基础
- **数据库连接池与事务管理**：连接池配置、会话管理、事务处理、批量操作、异步操作、数据库迁移、原生SQL
- **SQLAlchemy高级特性**：关系映射（一对多、多对多）、查询优化（预加载、延迟加载）、复杂查询（子查询、组合条件）、事件监听、混合属性
- **数据库优化**：索引优化（单列索引、复合索引、唯一索引）、查询优化（避免N+1、预加载、批量操作）、连接池优化、查询缓存（结果缓存、Redis缓存）、分页优化（游标分页）、数据库分区
- **NoSQL数据库深入**：MongoDB深入（聚合管道、索引优化、事务处理）、Redis深入（数据结构应用、发布订阅、Redis Streams）、Cassandra应用、Elasticsearch应用

### 测试部分

- **Python测试**：unittest、pytest基础、断言、Fixture
- **集成测试与Mock**：API集成测试、数据库集成测试、Mock对象、pytest-mock、异步测试、测试覆盖率
- **性能测试与压力测试**：Locust压力测试、pytest-benchmark基准测试、Apache Bench、响应时间分析、吞吐量测试
- **测试策略与TDD**：TDD流程（红-绿-重构）、测试金字塔（单元测试、集成测试、端到端测试）、测试策略（功能测试、性能测试、安全测试）、BDD行为驱动开发、测试数据管理（Fixtures、工厂模式）、测试隔离、持续测试

### 工具与规范部分

- **Python工具与规范**：代码规范（PEP 8）、类型检查、代码质量工具
- **虚拟环境与包管理**：venv、virtualenv、conda、pip、Poetry、pipenv、依赖管理、文档工具
- **代码质量工具**：Black格式化、autopep8、Flake8代码检查、Pylint、mypy类型检查、Radon复杂度分析、Bandit安全扫描、Coverage.py覆盖率、pre-commit集成
- **日志管理**：基础日志、日志级别、日志配置、日志轮转（大小轮转、时间轮转）、结构化日志（JSON格式）、日志上下文、多模块日志
- **配置管理**：环境变量（python-dotenv、.env文件）、Pydantic配置（Settings类、嵌套配置）、Django配置（多环境配置）、Flask配置（配置类）、配置文件（YAML、JSON、TOML）、配置验证、配置热重载

### 设计模式部分

- **Python设计模式**：创建型模式、结构型模式、行为型模式、Python特有模式
- **设计模式实战案例**：观察者模式（事件系统）、策略模式（支付系统）、装饰器模式、适配器模式、责任链模式、模板方法、状态模式、命令模式、外观模式、代理模式

### 部署与运维部分

- **Python部署与运维**：Gunicorn/uWSGI部署、Nginx配置、Docker部署、进程管理、监控
- **Kubernetes部署实践**：Deployment配置、Service、ConfigMap/Secret、HPA自动扩缩容、滚动更新、监控日志
- **CI/CD实践**：GitHub Actions工作流、Python项目CI、Docker构建推送、自动部署、多环境测试、代码质量检查
- **监控与日志**：应用监控（Prometheus、健康检查）、日志聚合（ELK Stack、结构化日志）、错误追踪（Sentry）、性能监控（APM、慢查询监控）、资源监控、告警系统

### 性能优化部分

- **Python性能优化**：算法优化、代码优化、内存优化、并发优化
- **性能分析工具**：cProfile、line_profiler、memory_profiler、py-spy实时分析
- **内存优化技巧**：memory_profiler内存分析、tracemalloc跟踪、生成器节省内存、__slots__减少对象内存、及时释放大对象、数据结构优化（array、deque）
- **缓存策略**：内存缓存（lru_cache、cachetools）、Redis缓存（基础使用、缓存模式）、缓存失效（主动失效、缓存预热）、分布式缓存（一致性哈希）、缓存穿透防护（布隆过滤器）、缓存雪崩防护（随机TTL、多级缓存）

### 安全编程部分

- **Python安全编程**：输入验证、安全配置、常见漏洞防护
- **加密与认证**：密码加密（bcrypt、passlib）、JWT认证、OAuth2、常见漏洞防护
- **常见漏洞防护**：SQL注入防护、XSS防护、CSRF防护、命令注入防护、文件上传安全、敏感信息保护、输入验证

### 算法与数据结构部分

- **Python算法与数据结构**：数据结构实现、排序算法、搜索算法、动态规划、图算法
- **经典算法实现**：快速排序、归并排序、堆排序、二分搜索、DFS/BFS、动态规划（斐波那契、LCS、背包问题）、图算法（Dijkstra、拓扑排序）、字符串算法（KMP）、贪心算法、回溯算法（N皇后）
- **高级数据结构**：堆（heapq模块、堆排序、优先队列）、树（二叉树、二叉搜索树、遍历算法）、图（邻接表、DFS、BFS、Dijkstra算法）、字典树（Trie实现、前缀匹配）、并查集（路径压缩、按秩合并）、线段树（区间查询、单点更新）

### 消息队列部分

- **Python消息队列**：RabbitMQ、Kafka、Redis队列、Celery分布式任务基础
- **消息队列高级应用**：RabbitMQ高级特性（消息确认、持久化、公平分发、发布订阅、路由模式、主题模式）、Kafka高级应用（生产者配置、消费者组、分区副本）、Redis消息队列（列表队列、发布订阅、Stream）、Celery高级用法（任务路由、定时任务）、消息幂等性、死信队列、消息重试、顺序保证、监控告警

## 🎯 学习路径

1. **Python基础**：
   - 从Python简介开始，了解语言特性
   - 掌握变量、数据类型、运算符
   - 学习分支和循环结构
   - 深入理解数据结构（列表、字典、集合、字符串）
   - 掌握函数和面向对象编程
   - 学习异常处理和文件操作
   - 了解高级特性（生成器、装饰器等）

2. **Web开发**：
   - FastAPI快速开发API
   - Django全栈开发
   - Flask轻量级Web框架

3. **数据分析**：
   - NumPy和Pandas数据处理
   - 数据可视化

4. **机器学习**：
   - 机器学习基础
   - RAG等AI应用

5. **并发编程**：
   - 多线程处理I/O密集型任务
   - 多进程处理CPU密集型任务
   - 异步编程提高并发性能

6. **网络编程**：
   - Socket底层网络通信
   - HTTP客户端开发
   - WebSocket实时通信

7. **爬虫开发**：
   - requests和BeautifulSoup基础爬虫
   - Scrapy专业爬虫框架
   - Selenium处理JavaScript渲染

8. **数据库操作**：
   - SQLAlchemy ORM框架
   - MongoDB NoSQL数据库
   - Redis缓存数据库

9. **测试**：
   - unittest和pytest测试框架
   - Mock和Stub测试技巧
   - 测试覆盖率分析

10. **工具与规范**：
    - 虚拟环境管理
    - 包管理和依赖管理
    - 代码规范和类型检查

11. **设计模式**：
    - 创建型模式（单例、工厂、建造者）
    - 结构型模式（适配器、装饰器、代理）
    - 行为型模式（观察者、策略、命令）

12. **部署与运维**：
    - Gunicorn/uWSGI部署
    - Nginx反向代理配置
    - Docker容器化部署
    - 进程管理和监控

13. **性能优化**：
    - 算法和数据结构优化
    - 代码优化技巧
    - 内存优化
    - 性能分析工具

14. **安全编程**：
    - 输入验证和清理
    - 认证和授权
    - 数据加密
    - 安全最佳实践

15. **算法与数据结构**：
    - 常用数据结构实现
    - 排序和搜索算法
    - 动态规划和贪心算法
    - 图算法

16. **消息队列**：
    - RabbitMQ消息代理
    - Kafka流处理
    - Redis队列
    - Celery异步任务

## 📖 使用说明

- 所有笔记都是从个人学习过程中整理的技术内容
- 已移除所有敏感信息（密码、Token、密钥等）
- 包含代码示例和最佳实践
- 适合系统学习和面试准备

## 🔗 相关资源

- [Python 官方文档](https://docs.python.org/zh-cn/3/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pandas 文档](https://pandas.pydata.org/)

