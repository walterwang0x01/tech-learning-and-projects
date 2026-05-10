# PostgreSQL 运维

> Author: Walter Wang

<!-- version-check: PostgreSQL 18.3, Patroni 4.0, pgBackRest 2.54, CloudNativePG 1.25, checked 2026-05-10 -->

## 1. 运维的三个核心问题

```
1. 性能：查询要快
2. 可用性：不能挂
3. 数据安全：不能丢
```

性能见 [03-PostgreSQL性能优化.md](./03-PostgreSQL性能优化.md)。本篇重点：高可用、备份、升级、监控。

## 2. 流复制（主备）

### 2.1 原理

```
主库（Primary）
  └─ 写 WAL → 通过流协议推送 → 备库 Apply WAL
                                  ↓
                           备库（Standby / Hot Standby）
                           可读、不可写
```

### 2.2 主库配置

```ini
# postgresql.conf
listen_addresses = '*'
wal_level = replica          # 最低 replica，逻辑复制用 logical
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 4GB          # 保留最近 4GB WAL
archive_mode = on
archive_command = 'pgbackrest --stanza=main archive-push %p'
```

```
# pg_hba.conf
host replication replicator 10.0.0.0/8 scram-sha-256
```

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'xxx';
SELECT pg_create_physical_replication_slot('standby1');
```

### 2.3 备库初始化

```bash
# 从主库做基础备份
pg_basebackup \
    -h primary-host \
    -D /var/lib/postgresql/data \
    -U replicator \
    -P -R \
    -S standby1 \
    -X stream

# -R 自动生成 standby.signal 和 primary_conninfo
# -S 用复制槽
# -X stream 流式备份 WAL
```

## 3. Patroni：自动故障转移

手动主备切换操作风险太高。生产应该用自动化方案。

```
Patroni 方案组件：
├─ Patroni（Python 守护进程，每节点一个）
├─ etcd / Consul（分布式协调）
├─ HAProxy / Kubernetes Service（流量路由）
└─ VIP / DNS（故障切换）
```

Patroni 会：
- 持续监控主节点健康
- 主节点挂掉 → 自动选一个备节点晋升
- 原主恢复后 → 自动变成新主的备

配置示例（Kubernetes 方案推荐用 **CloudNativePG**）：

```yaml
# CloudNativePG Operator
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: pg-cluster
spec:
  instances: 3        # 1 主 2 备
  imageName: ghcr.io/cloudnative-pg/postgresql:18.3

  storage:
    size: 100Gi
    storageClass: fast-ssd

  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "4GB"
      effective_cache_size: "12GB"

  monitoring:
    enablePodMonitor: true

  backup:
    barmanObjectStore:
      destinationPath: s3://my-backups/pg-cluster
      s3Credentials:
        accessKeyId: {name: pg-backup, key: ACCESS_KEY_ID}
        secretAccessKey: {name: pg-backup, key: SECRET_ACCESS_KEY}
    retentionPolicy: "30d"
```

## 4. 逻辑复制

物理复制：整个集群。
逻辑复制：按表/行。

```sql
-- 发布端
CREATE PUBLICATION my_pub FOR TABLE orders, users;
-- 或所有表
-- CREATE PUBLICATION my_pub FOR ALL TABLES;

-- 订阅端
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=primary dbname=mydb user=replicator'
    PUBLICATION my_pub;
```

**用途**：
- 跨大版本升级（PG 13 → 18）
- 多主（需要冲突解决）
- CDC（见 [data-engineering/05-CDC与Debezium.md](../data-engineering/05-CDC与Debezium.md)）
- 跨数据中心同步

## 5. 备份：pgBackRest（推荐）

2026 年生产级首选。

```bash
# 配置 /etc/pgbackrest.conf
[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2
repo1-cipher-type=aes-256-cbc
repo1-cipher-pass=xxx

repo1-type=s3
repo1-s3-bucket=my-backups
repo1-s3-region=us-east-1

[main]
pg1-path=/var/lib/postgresql/data
pg1-port=5432
```

```bash
# 全量备份
pgbackrest --stanza=main backup

# 增量备份（只有变化的 WAL）
pgbackrest --stanza=main --type=incr backup

# 恢复到最新
pgbackrest --stanza=main restore

# 时间点恢复（PITR）
pgbackrest --stanza=main --type=time \
    --target='2026-05-10 10:30:00' restore
```

**备份策略**：
- 每周全量 + 每天增量
- 保留 14-30 天
- 至少两地（主备份 + S3 归档）
- 每月验证恢复

## 6. 升级策略

PG 主版本升级（如 16 → 18）有两种方式：

### 6.1 pg_upgrade（in-place）

```bash
pg_upgrade \
    -b /usr/lib/postgresql/16/bin \
    -B /usr/lib/postgresql/18/bin \
    -d /var/lib/postgresql/16/data \
    -D /var/lib/postgresql/18/data \
    --link       # 硬链接文件，最快
```

**优势**：快（分钟级）。
**缺点**：单机，有 downtime。

### 6.2 逻辑复制升级（零停机）

```
步骤：
1. 搭 PG 18 新实例
2. 新实例作为 PG 16 的逻辑复制订阅者
3. 追平数据
4. 切换应用连接字符串
5. 废弃旧实例
```

大公司推荐这种，但操作复杂。

## 7. 监控

### 必监控指标

```
连接：
├─ pg_stat_activity 当前连接数
├─ 按 state 分布（active / idle / idle in transaction）
└─ 长事务（> 5 分钟告警）

查询性能：
├─ pg_stat_statements Top N 慢查询
├─ 缓存命中率 > 99%
└─ 临时文件大小（表示 work_mem 不够）

复制：
├─ 复制延迟（字节数 + 时间）
├─ 复制槽保留的 WAL 大小（避免磁盘爆）
└─ 备库可见性

VACUUM：
├─ 死元组比例
├─ autovacuum 运行状态
└─ wraparound 风险（xmin_horizon）

存储：
├─ 数据目录大小增长
├─ WAL 目录大小
└─ 最大表和索引 Top 10

资源：
├─ CPU / Memory / Disk I/O / Network
└─ Connection count vs max_connections
```

### 工具

```
Prometheus + Grafana：
├─ postgres_exporter（最流行）
├─ pgwatch2
└─ 现成 Dashboard：ID 9628 / 12485

商业：
├─ Datadog
├─ pganalyze（专业 PG 监控）
└─ percona PMM
```

### 查询示例

```sql
-- 当前长事务
SELECT pid, now() - xact_start AS duration, state, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND now() - xact_start > interval '5 minutes'
ORDER BY duration DESC;

-- 复制延迟
SELECT
    client_addr,
    application_name,
    state,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn)) AS sent_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), write_lsn)) AS write_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn)) AS flush_lag,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) AS replay_lag
FROM pg_stat_replication;

-- 复制槽状态（泄漏检查）
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal
FROM pg_replication_slots;

-- Top 10 大表
SELECT
    schemaname || '.' || relname AS table,
    pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;
```

## 8. 常见运维事故

```
事故 1：复制槽泄漏
  症状：主库磁盘迅速增长
  原因：备库连不上但槽还在，WAL 无法回收
  处理：立即处理备库或删除槽

事故 2：VACUUM 来不及
  症状：表膨胀、查询变慢
  原因：UPDATE / DELETE 量大，autovacuum 跟不上
  处理：手动 VACUUM 或 pg_repack；调 autovacuum 参数

事故 3：XID wraparound
  症状：数据库拒绝写入
  原因：事务 ID 耗尽（20 亿）
  预防：监控 xmin_horizon，及时 VACUUM FREEZE

事故 4：连接数耗尽
  症状：新连接失败
  原因：应用未用连接池 / 连接泄漏
  处理：加 PgBouncer，查应用代码

事故 5：主从切换失败
  症状：主挂了，备没晋升
  原因：Patroni 配置错 / etcd 故障
  预防：定期演练故障转移
```

## 9. 重要扩展

```
必装：
├─ pg_stat_statements（慢查询分析）
└─ pgcrypto（加密）

高价值：
├─ pg_partman（自动分区管理）
├─ pg_cron（数据库内定时任务）
├─ pg_repack（在线重建表，无锁）
├─ pgvector（AI 向量）
├─ TimescaleDB（时序）
├─ PostGIS（地理）
├─ pglogical（增强逻辑复制）
└─ hypopg（虚拟索引，先测试再建）

监控：
├─ auto_explain（自动记录慢查询计划）
└─ pg_wait_sampling（等待事件分析）
```

## 10. Kubernetes 上的 PG（2026 推荐）

```
CloudNativePG（CNCF 孵化，2024 起流行）
├─ Operator 模式
├─ 支持 PG 12-18
├─ 自动 failover
├─ Barman 集成备份
└─ 读写分离

其他：
├─ Zalando Postgres Operator
└─ CrunchyData PGO
```

## 11. 生产检查清单

```
配置：
☐ shared_buffers = 25% 内存
☐ effective_cache_size = 75% 内存
☐ work_mem 设置合理
☐ max_connections 和连接池匹配
☐ wal_level = replica / logical
☐ archive_mode = on + WAL 归档到 S3

备份：
☐ pgBackRest 全量 + 增量
☐ 保留策略明确（30 天）
☐ 备份在独立故障域
☐ 每月演练恢复
☐ 备份监控 + 告警

高可用：
☐ 至少 1 个同步备库 + 1 个异步
☐ Patroni / CloudNativePG 自动切换
☐ 监控复制延迟
☐ 有明确的切换 Runbook

监控：
☐ pg_stat_statements 启用
☐ 慢查询告警（> 1s）
☐ 长事务告警（> 5 min）
☐ 复制延迟告警
☐ 磁盘空间告警
☐ autovacuum 监控

安全：
☐ SSL/TLS 启用
☐ pg_hba.conf 最小放行
☐ 应用账号非 SUPERUSER
☐ 独立 read-only 账号
☐ 定期轮换密码（或用 Vault Dynamic Secrets）
☐ Audit Log（pgaudit 扩展）
```

## 📖 参考资料

- [PG 官方高可用文档](https://www.postgresql.org/docs/current/high-availability.html)
- [Patroni 文档](https://patroni.readthedocs.io/)
- [CloudNativePG](https://cloudnative-pg.io/)
- [pgBackRest](https://pgbackrest.org/)
- [PG Backup Strategies](https://www.postgresql.fastware.com/blog/postgresql-backup-strategies)
- [postgres_exporter](https://github.com/prometheus-community/postgres_exporter)
