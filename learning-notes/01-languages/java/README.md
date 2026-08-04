# Java 技术学习笔记
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> 本目录包含 Java 技术栈的学习笔记，按类别组织

## 📁 目录结构

```
java/
├── 00-Java基础/          # Java 语言基础
│   ├── Java新特性8-17.md
│   ├── JVM内存模型与垃圾回收.md
│   ├── Java并发编程.md
│   ├── Java集合框架.md
│   ├── Java反射与注解.md
│   ├── Java异常处理.md
│   ├── Java泛型.md
│   ├── Java枚举.md
│   ├── Java IO与NIO.md
│   ├── Java字符串.md
│   ├── Java包装类与自动装箱拆箱.md
│   ├── Java内部类.md
│   └── Java正则表达式.md
│
├── 01-框架/              # Spring 生态框架
│   ├── Spring基础01.md
│   ├── Spring基础02.md
│   ├── Spring基础03.md
│   ├── SpringBoot基础.md
│   ├── spring高级50讲.md
│   ├── SpringMVC基础01.md
│   ├── SpringMVC基础02.md
│   ├── SpringCloud01.md
│   ├── SpringCloud02.md
│   ├── MyBatisPlus.md
│   ├── 微服务保护-Sentinel.md
│   ├── 分布式事务.md
│   ├── spring-boot-best-practices.md
│   └── microservices-patterns.md
│
├── 02-中间件/            # 中间件技术
│   ├── RabbitMQ.md
│   ├── RabbitMQ高级篇.md
│   ├── Elasticsearch基础.md
│   ├── Elasticsearch进阶.md
│   ├── Elasticsearch高级.md
│   ├── Nginx简介.md
│   ├── Nginx常用配置.md
│   ├── Caffeine缓存.md
│   ├── Redis分布式缓存.md
│   ├── 多级缓存.md
│   └── kafka-event-driven-architecture.md
│
├── 03-容器化/            # 容器化与编排
│   ├── Docker实用篇.md
│   ├── docker-basics.md
│   ├── Kubernetes第1天.md
│   ├── Kubernetes第2天.md
│   ├── Kubernetes第3天.md
│   ├── Kubernetes第4天.md
│   ├── Kubernetes第5天.md
│   └── kubernetes-overview.md
│
├── 04-设计模式/          # 设计模式
│   ├── 设计模式.md
│   └── design-patterns-summary.md
│
├── 05-网络编程/          # 网络编程
│   ├── Netty01-nio.md
│   ├── Netty02-入门.md
│   ├── Netty03-进阶.md
│   ├── Netty04-优化与源码.md
│   └── gRPC-Java.md
│
├── 06-构建工具/          # 构建工具
│   ├── Maven基础.md
│   ├── Maven高级.md
│   └── Gradle基础.md
│
├── 07-数据库/            # 数据库
│   ├── MySQL基础.md
│   ├── MySQL中级.md
│   └── MySQL高级.md
│
├── 08-部署与运维/        # 部署与运维
│   ├── Nacos安装指南.md
│   ├── Nacos集群搭建.md
│   ├── RabbitMQ部署指南.md
│   ├── Elasticsearch安装指南.md
│   ├── CentOS7安装Docker.md
│   ├── Sentinel规则持久化.md
│   ├── Seata部署和集成.md
│   ├── Redis集群部署.md
│   ├── Canal安装配置.md
│   └── OpenResty安装配置.md
│
├── 09-源码分析/          # 源码分析
│   ├── Nacos源码分析.md
│   └── Sentinel源码分析.md
│
├── 10-工具与测试/        # 工具与测试
│   └── Jmeter快速入门.md
│
└── 11-面试准备/          # 面试准备
    └── 微服务常见面试题.md
```

## 📚 内容分类

### 00-Java基础

**Java 语言特性**
- **Java新特性8-17**：Lambda表达式、Stream API、新特性总结
- **JVM内存模型与垃圾回收**：JVM内存结构、对象创建、垃圾回收算法、垃圾收集器、JVM调优
- **Java并发编程**：线程基础、线程同步、线程池、并发集合、原子类、CAS、锁机制、并发工具类
- **Java集合框架**：List、Set、Map、Queue等集合类的使用和原理
- **Java反射与注解**：反射机制、Class类、注解定义和使用、注解处理器
- **Java异常处理**：异常分类、try-catch-finally、自定义异常、异常处理最佳实践
- **Java泛型**：泛型类、泛型方法、类型通配符、类型擦除、泛型应用
- **Java枚举**：枚举定义、枚举方法、枚举与switch、EnumSet、EnumMap、枚举单例
- **Java IO与NIO**：字节流、字符流、对象流、NIO Buffer、Channel、Selector、NIO.2
- **Java字符串**：String不可变性、字符串常量池、StringBuilder、StringBuffer、字符串操作
- **Java包装类与自动装箱拆箱**：包装类使用、自动装箱拆箱、缓存机制、类型转换
- **Java内部类**：成员内部类、静态内部类、局部内部类、匿名内部类
- **Java正则表达式**：Pattern、Matcher、正则语法、常用示例

### 01-框架

**Spring 框架系列**
- **Spring基础**：IOC、DI、AOP、事务管理等核心概念
- **Spring高级**：容器与Bean、生命周期、后处理器等高级特性
- **Spring Boot**：快速开发、自动配置、整合其他技术
- **SpringMVC**：Web开发、请求响应、REST风格、SSM整合
- **Spring Cloud**：微服务架构、服务发现、配置中心、网关等

**ORM 框架**
- **MyBatis Plus**：MyBatis 增强工具，简化开发

**微服务高级**
- **微服务保护**：Sentinel 限流、熔断、降级
- **分布式事务**：Seata、TCC、Saga 等解决方案

**最佳实践**
- **Spring Boot 最佳实践**：统一异常处理、响应格式、全链路追踪等
- **微服务架构模式**：服务拆分、通信、服务发现等

### 02-中间件

**消息队列**
- **RabbitMQ**：消息队列、异步通信、事件驱动架构
- **RabbitMQ高级篇**：消息可靠性、延迟消息、死信队列等
- **Kafka**：事件驱动架构、高吞吐量消息系统

**搜索引擎**
- **Elasticsearch**：分布式搜索引擎、倒排索引、全文检索（基础、进阶、高级）

**Web 服务器**
- **Nginx**：反向代理、负载均衡、静态资源服务

**缓存**
- **Caffeine**：高性能本地缓存框架
- **Redis分布式缓存**：Redis持久化、集群、哨兵等
- **多级缓存**：JVM进程缓存、Redis缓存、Nginx缓存等多级缓存架构

### 03-容器化

**容器技术**
- **Docker**：容器化部署、镜像构建、Docker Compose

**容器编排**
- **Kubernetes**：容器编排、Pod、Service、Deployment 等核心概念

### 04-设计模式

- **设计模式**：23 种设计模式详解（创建型、结构型、行为型）
- **设计模式总结**：设计模式分类和总结

### 05-网络编程

**NIO 框架**
- **Netty**：NIO 基础、入门、进阶、优化与源码分析

**RPC 框架**
- **gRPC**：高性能 RPC 框架、Protobuf、HTTP/2

### 06-构建工具

**Maven**
- **Maven基础**：Maven概念、安装配置、坐标、依赖管理
- **Maven高级**：分模块开发、聚合工程、继承、私服

**Gradle**
- **Gradle基础**：Gradle 构建工具基础

### 07-数据库

**MySQL**
- **MySQL基础**：SQL分类、DDL、DML、DQL、DCL
- **MySQL中级**：约束、多表查询、事务等
- **MySQL高级**：存储引擎、索引、SQL优化、锁等

### 08-部署与运维

**服务注册与配置**
- **Nacos**：Nacos安装指南、Nacos集群搭建

**消息队列**
- **RabbitMQ部署指南**：单机部署、集群部署

**搜索引擎**
- **Elasticsearch安装指南**：Docker部署、Kibana配置

**容器化**
- **CentOS7安装Docker**：Docker CE安装、配置

**微服务组件**
- **Sentinel规则持久化**：Sentinel与Nacos集成
- **Seata部署和集成**：分布式事务解决方案部署

**缓存**
- **Redis集群部署**：Redis主从、分片集群
- **Canal安装配置**：MySQL binlog同步工具
- **OpenResty安装配置**：基于Nginx的Web平台

### 09-源码分析

**微服务组件源码**
- **Nacos源码分析**：服务注册、服务发现、配置管理源码解析
- **Sentinel源码分析**：限流、熔断、降级源码解析

### 10-工具与测试

**性能测试**
- **Jmeter快速入门**：性能测试工具使用

### 11-面试准备

**面试题**
- **微服务常见面试题**：Spring Cloud、Nacos、Sentinel等面试题

## 🎯 学习路径建议

### 基础阶段
1. **Java基础**：
   - Java新特性（Lambda、Stream等）
   - JVM内存模型与垃圾回收
   - Java并发编程（线程、线程池、锁等）
   - Java集合框架（List、Set、Map等）
   - Java反射与注解
   - Java异常处理（try-catch、自定义异常等）
   - Java泛型（类型参数、通配符等）
   - Java枚举（枚举定义、使用等）
   - Java IO与NIO（文件操作、网络编程等）
   - Java字符串（String、StringBuilder、StringBuffer等）
   - Java包装类与自动装箱拆箱（Integer、Double等包装类）
   - Java内部类（成员内部类、静态内部类、局部内部类、匿名内部类）
   - Java正则表达式（Pattern、Matcher、正则语法）
2. **构建工具**：Maven 基础 → Maven 高级
3. **数据库**：MySQL 基础 → MySQL 中级 → MySQL 高级
4. **Spring 框架**：Spring 基础 → Spring Boot → SpringMVC → Spring 高级
5. **ORM 框架**：MyBatis Plus
6. **设计模式**：23 种设计模式

### 进阶阶段
1. **微服务**：Spring Cloud → 微服务保护 → 分布式事务
2. **中间件**：
   - 消息队列（RabbitMQ → RabbitMQ 高级篇）
   - 搜索引擎（Elasticsearch 基础 → 进阶 → 高级）
   - 缓存（Caffeine → Redis → 多级缓存）
   - Web 服务器（Nginx）
3. **容器化**：Docker → Kubernetes

### 高级阶段
1. **网络编程**：Netty（NIO → 入门 → 进阶 → 优化）→ gRPC
2. **源码分析**：Nacos源码、Sentinel源码
3. **性能优化**：多级缓存、分布式缓存、消息队列高级特性
4. **架构设计**：微服务架构模式、分布式系统设计
5. **部署运维**：各种中间件的部署和集群搭建
6. **工具使用**：Jmeter性能测试
7. **面试准备**：微服务常见面试题

## 📖 使用说明

1. **按需阅读**：根据学习阶段选择相应类别的内容
2. **实践应用**：结合项目实践应用所学知识
3. **持续更新**：根据学习进度更新内容

## 📝 注意事项

- 这些是个人学习笔记，仅供参考
- 部分内容可能不够深入，建议结合官方文档学习
- 代码示例仅作参考，实际使用时需要根据场景调整

