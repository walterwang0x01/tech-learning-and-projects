# MySQL高级
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 事务

### 1.1 事务的ACID特性

- **原子性(Atomicity)**: 事务是一个不可分割的工作单位，事务中的操作要么都发生，要么都不发生
- **一致性(Consistency)**: 事务前后数据的完整性必须保持一致
- **隔离性(Isolation)**: 多个用户并发访问数据库时，数据库为每一个用户开启的事务，不能被其他事务的操作数据所干扰，多个并发事务之间要相互隔离
- **持久性(Durability)**: 一个事务一旦被提交，它对数据库中数据的改变就是永久性的，接下来即使数据库发生故障也不应该对其有任何影响

### 1.2 事务隔离级别

MySQL支持四种事务隔离级别：

1. **读未提交(Read Uncommitted)**: 最低的隔离级别，允许读取尚未提交的数据变更，可能会导致脏读、幻读或不可重复读
2. **读已提交(Read Committed)**: 允许读取并发事务已经提交的数据，可以阻止脏读，但是幻读或不可重复读仍有可能发生
3. **可重复读(Repeatable Read)**: 对同一字段的多次读取结果都是一致的，除非数据是被本身事务自己所修改，可以阻止脏读和不可重复读，但幻读仍有可能发生（MySQL默认隔离级别）
4. **可串行化(Serializable)**: 最高的隔离级别，完全服从ACID的隔离级别，所有的事务依次逐个执行，这样事务之间就完全不可能产生干扰，可以防止脏读、不可重复读以及幻读

查看当前事务隔离级别：
```sql
SELECT @@transaction_isolation;
```

设置事务隔离级别：
```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### 1.3 MVCC (Multi-Version Concurrency Control)

MVCC是一种基于多版本的并发控制协议，只有在InnoDB引擎下存在。

**MVCC的实现原理：**
- 通过undo log保存事务发生之前的数据版本
- 通过ReadView判断当前事务可以看到哪个版本的数据
- 通过版本链实现多版本并发控制

**MVCC解决的问题：**
- 读写冲突：通过多版本控制，读操作不需要加锁，提高了并发性能
- 写写冲突：通过行锁和版本控制，保证数据的一致性

## 2. 锁机制

### 2.1 锁的分类

MySQL中的锁，按照锁的粒度分，分为以下三类：

- **全局锁**: 锁定数据库中的所有表
- **表级锁**: 每次操作锁住整张表
- **行级锁**: 每次操作锁住对应的行数据

### 2.2 行级锁

InnoDB的行锁是实现在索引上的，而不是锁在物理行记录上。如果访问没有命中索引，也无法使用行锁，将要退化为表锁。

**行锁的类型：**
- **记录锁(Record Lock)**: 锁定单行记录
- **间隙锁(Gap Lock)**: 锁定索引记录之间的间隙
- **临键锁(Next-Key Lock)**: 记录锁和间隙锁的组合，锁定一个范围，并且锁定记录本身

**查看锁信息：**
```sql
-- 查看当前锁等待情况
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;
SELECT * FROM information_schema.INNODB_TRX;
```

### 2.3 死锁

**死锁产生的条件：**
1. 互斥条件：资源不能被多个事务同时使用
2. 请求与保持条件：一个事务因请求资源而阻塞时，对已获得的资源保持不放
3. 不剥夺条件：事务已获得的资源，在未使用完之前，不能强行剥夺
4. 循环等待条件：若干事务之间形成一种头尾相接的循环等待资源关系

**死锁的处理：**
- MySQL会自动检测死锁，并回滚其中一个事务
- 可以通过设置`innodb_lock_wait_timeout`来控制等待锁的超时时间

**避免死锁的方法：**
1. 尽量按相同的顺序访问表
2. 尽量使用索引，减少锁的范围
3. 尽量缩短事务的执行时间
4. 避免大事务，将大事务拆分为小事务

## 3. 日志系统

### 3.1 redo log (重做日志)

**作用：**
- 确保事务的持久性
- 防止在发生故障的时间点，尚有脏页未写入磁盘
- 在重启mysql服务的时候，根据redo log进行重做，从而达到事务的持久性

**特点：**
- 循环写入，大小固定
- 顺序写入，性能高
- 在事务提交时写入，保证持久性

### 3.2 undo log (回滚日志)

**作用：**
- 保存了事务发生之前的数据的一个版本
- 可以用于回滚
- 可以提供多版本并发控制下的读(MVCC)，也即非锁定读

**特点：**
- 逻辑日志，记录的是SQL语句的反向操作
- 用于事务回滚和MVCC

### 3.3 binlog (二进制日志)

**作用：**
- 用于复制，在主从复制中，从库利用主库上的binlog进行重播，实现主从同步
- 用于数据库的基于时间点的还原

**特点：**
- 记录所有对数据库的修改操作
- 可以用于数据恢复和主从复制
- 有三种格式：STATEMENT、ROW、MIXED

**binlog相关配置：**
```sql
-- 查看binlog是否开启
SHOW VARIABLES LIKE 'log_bin';

-- 查看binlog格式
SHOW VARIABLES LIKE 'binlog_format';

-- 查看binlog文件列表
SHOW BINARY LOGS;

-- 查看当前正在使用的binlog文件
SHOW MASTER STATUS;
```

## 4. 主从复制

### 4.1 主从复制原理

1. 主库将变更写入binlog
2. 从库的IO线程连接主库，请求binlog
3. 主库的dump线程读取binlog，发送给从库
4. 从库的IO线程接收binlog，写入relay log
5. 从库的SQL线程读取relay log，执行SQL，实现数据同步

### 4.2 主从复制配置

**主库配置：**
```ini
[mysqld]
server-id=1
log-bin=mysql-bin
binlog-format=ROW
```

**从库配置：**
```ini
[mysqld]
server-id=2
relay-log=mysql-relay-bin
read-only=1
```

**从库连接主库：**
```sql
CHANGE MASTER TO
  MASTER_HOST='主库IP',
  MASTER_USER='repl',
  MASTER_PASSWORD='password',
  MASTER_LOG_FILE='mysql-bin.000001',
  MASTER_LOG_POS=154;

START SLAVE;
```

## 5. 性能优化

### 5.1 基本原则

1. 让MySQL回归存储的基本职能：MySQL数据库只用于数据的存储，不进行数据的复杂计算，不承载业务逻辑
2. 查询数据时，尽量单表查询，减少跨库查询和多表关联
3. 杜绝大事务、大SQL、大批量、大字段等一系列性能杀手

### 5.2 索引优化

**索引设计原则：**
1. 创建索引的列并不一定是select操作中要查询的列，最适合做索引的列是出现在where子句中经常用作筛选条件或连表子句中作为表连接条件的列
2. 具有唯一性的列，索引效果好；重复值较多的列，索引效果差
3. 如果为字符串类型创建索引，最好指定一个前缀长度，创建短索引
4. 创建一个包含N列的复合索引（多列索引）时，相当于是创建了N个索引，此时应该利用最左前缀进行匹配
5. 不要过度使用索引。索引并不是越多越好，索引需要占用额外的存储空间而且会影响写操作的性能

### 5.3 SQL优化

**优化方法：**
1. 使用慢查询日志定位低效率的SQL语句
2. 通过explain了解SQL的执行计划
3. 通过show profiles和show profile for query分析SQL
4. 优化CRUD操作：
   - 优化insert语句：批量插入、手动控制事务、主键顺序插入
   - 优化order by语句：利用索引完成排序
   - 优化group by语句：使用order by null禁用排序
   - 优化嵌套查询：用连接查询替代子查询
   - 优化or条件：确保所有条件都用到索引
   - 优化分页查询：在索引上完成排序和分页

### 5.4 配置优化

**关键配置参数：**
- `max_connections`: MySQL最大连接数量，建议控制在1000以内
- `back_log`: TCP连接的积压请求队列大小，通常是max_connections的五分之一
- `table_open_cache`: 表缓存大小，应该设置为max_connections的N倍
- `innodb_lock_wait_timeout`: InnoDB事务等待行锁的时间，默认50ms
- `innodb_buffer_pool_size`: InnoDB数据和索引的内存缓冲区大小，建议设置为物理内存的80%

### 5.5 架构优化

1. **表拆分**：
   - 垂直拆分：将大表按列拆分为多个小表
   - 水平拆分：将大表按行拆分为多个小表（分库分表）

2. **逆范式理论**：故意降低范式级别增加冗余来减少查询的时间开销

3. **使用中间表**：提高统计查询速度

4. **主从复制和读写分离**：提高读性能

5. **配置MySQL集群**：提高可用性和性能

## 6. InnoDB存储引擎特性

### 6.1 InnoDB与MyISAM的区别

1. InnoDB支持事务，MyISAM不支持
2. InnoDB支持外键，而MyISAM不支持
3. InnoDB是聚集索引，MyISAM是非聚集索引
4. InnoDB不保存表的具体行数，MyISAM用一个变量保存了整个表的行数
5. InnoDB支持表、行(默认)级锁，而MyISAM支持表级锁
6. InnoDB表必须有唯一索引(如主键)，而MyISAM可以没有
7. InnoDB存储文件有frm、ibd，而MyISAM是frm、MYD、MYI

### 6.2 InnoDB的四大特性

1. **插入缓冲(Insert Buffer)**: 对于非聚集索引的插入或更新操作，不是每一次都直接插入到索引页中，而是先判断插入的非聚集索引页是否在缓冲池中，若在，则直接插入；若不在，则先放入到一个Insert Buffer对象中，然后再以一定的频率进行Insert Buffer和辅助索引页子节点的merge操作
2. **两次写(Double Write)**: 在写数据页之前，先将数据页写到共享表空间的doublewrite buffer中，然后再写到数据文件中
3. **自适应哈希索引(Adaptive Hash Index)**: InnoDB存储引擎会监控对表上各索引页的查询，如果观察到建立哈希索引可以带来速度提升，则建立哈希索引
4. **预读(Read Ahead)**: InnoDB使用两种预读算法来提高I/O性能：线性预读和随机预读

### 6.3 InnoDB为什么推荐使用自增ID作为主键？

自增ID可以保证每次插入时B+索引是从右边扩展的，可以避免B+树和频繁合并和分裂。如果使用字符串主键和随机主键，会使得数据随机插入，效率比较差。

## 7. 分库分表

### 7.1 分库分表的原因

- 单表数据量过大，影响查询性能
- 单库连接数过多，影响并发性能
- 单库存储空间有限，需要水平扩展

### 7.2 分库分表策略

**垂直拆分：**
- 按业务模块拆分，不同模块使用不同的数据库
- 优点：业务清晰，易于维护
- 缺点：跨库查询困难，事务处理复杂

**水平拆分：**
- 按数据行拆分，将大表拆分为多个小表
- 拆分方式：
  - 按范围拆分：如按时间、按ID范围
  - 按哈希拆分：如按用户ID取模
  - 按一致性哈希：保证数据分布均匀

### 7.3 分库分表带来的问题

1. **跨库查询**：需要聚合多个库的数据
2. **分布式事务**：需要使用分布式事务解决方案（如Seata）
3. **主键ID生成**：需要使用分布式ID生成方案（如雪花算法）
4. **数据迁移**：需要考虑数据迁移和一致性

## 8. 监控与运维

### 8.1 性能监控

**查看连接状态：**
```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
```

**查看慢查询：**
```sql
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';
```

**查看锁状态：**
```sql
SHOW ENGINE INNODB STATUS;
```

### 8.2 备份与恢复

**mysqldump备份：**
```bash
# 备份单个数据库
mysqldump -u root -p database_name > backup.sql

# 备份所有数据库
mysqldump -u root -p --all-databases > all_backup.sql

# 使用--single-transaction参数进行一致性备份
mysqldump --single-transaction -u root -p database_name > backup.sql
```

**恢复数据：**
```bash
mysql -u root -p database_name < backup.sql
```

### 8.3 常见问题排查

1. **慢查询问题**：开启慢查询日志，分析慢SQL
2. **锁等待问题**：查看锁等待情况，优化事务
3. **连接数过多**：检查连接池配置，优化连接使用
4. **内存使用过高**：调整innodb_buffer_pool_size等参数


<!-- version-check: MySQL 8.4.5 LTS, MySQL 9.3 Innovation, checked 2026-04-22 -->

> 🔄 更新于 2026-04-22

## 9. MySQL 版本演进（2026）

### 9.1 当前版本格局

| 版本 | 类型 | 状态 | 适用场景 |
|------|------|------|---------|
| MySQL 8.4.5 | LTS（长期支持） | ✅ 生产推荐 | 企业级应用、稳定性优先 |
| MySQL 9.3.0 | Innovation（创新版） | 🧪 公开预览 | 新特性尝鲜、AI/ML 场景 |

### 9.2 MySQL 9.x Innovation Release 新特性

**1. VECTOR 数据类型**（MySQL 9.0+）

```sql
-- 创建包含向量字段的表
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT,
    embedding VECTOR(768)  -- 768 维向量
);

-- 插入向量数据
INSERT INTO documents (content, embedding)
VALUES ('AI Agent 技术', TO_VECTOR('[0.1, 0.2, ...]'));
```

MySQL 原生支持向量存储和相似度搜索，适用于 RAG、语义搜索等 AI 场景。

**2. JavaScript 存储程序**（MySQL 9.3）

```sql
-- 使用 JavaScript 编写存储函数
CREATE FUNCTION format_currency(amount DECIMAL(10,2), locale VARCHAR(10))
RETURNS VARCHAR(50)
LANGUAGE JAVASCRIPT AS $$
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
$$;

SELECT format_currency(1234.56, 'en-US');
-- $1,234.56
```

支持 Intl 对象进行本地化格式化，完整的 DECIMAL 处理。

### 9.3 版本选择建议

- **新项目**：MySQL 8.4.x LTS（稳定、长期支持）
- **AI/ML 场景**：评估 MySQL 9.x（VECTOR 类型）或考虑 PostgreSQL + pgvector
- **升级路径**：5.7 → 8.0 → 8.4 LTS（跳过 9.x Innovation 版本）

来源：[MySQL 9.3 新特性](https://dev.mysql.com/doc/mysqld-version-reference/en/) | [MySQL Community Early Access](https://blogs.oracle.com/mysql/mysql-community-early-access-builds)
