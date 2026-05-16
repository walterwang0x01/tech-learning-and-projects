# Airflow 与 Dagster 编排

> Author: Walter Wang

<!-- version-check: Airflow 3.2 (2026-Q2), Airflow 3.1 (HITL), Dagster 1.10, Prefect 3.x, checked 2026-05-16 -->

## 1. 为什么要编排

```
数据管道的复杂度：
├─ 数百个任务，相互依赖
├─ 定时调度（每天、每小时、Cron 表达式）
├─ 失败重试和告警
├─ 回填历史数据
├─ 资源限制（并发度）
├─ 可观测性（哪个任务慢了）
└─ 跨团队协作（谁 own 哪个 DAG）

没有编排器 → 一堆 Cron + 脆弱的 shell 脚本
```

## 2. 主流工具对比

| 工具 | 范式 | 2026 状态 |
|------|------|-----------|
| **Airflow** | Task-first | 老牌，生态最大，3.0 大幅重写 |
| **Dagster** | Asset-first | 现代，推荐新项目 |
| **Prefect** | Flow-first | Python 原生，易用 |
| **Temporal** | Workflow | 侧重业务流程（不只是数据） |
| **Argo Workflows** | K8s 原生 | 容器密集场景 |
| **Kestra** | YAML-first | 声明式，欧洲流行 |

**2026 年选型**：
- 已有 Airflow 生态 → 留
- 新数据项目 → **Dagster**（Asset + Resource + IO Manager 设计更合理）
- 业务流程编排 → **Temporal**
- K8s-Native → **Argo Workflows**

## 3. Airflow 3.0 速览

Airflow 3.0 是 10 年来最大的重写：

```
Airflow 3.0 关键变化（2025 发布）：
├─ 多调度器（scale-out scheduler）
├─ Task SDK：任务可以用其他语言写（不只 Python）
├─ React 新 UI
├─ 原生 Asset 支持（类似 Dagster）
├─ Edge Executor（边缘节点执行任务）
└─ 更强的 dynamic task mapping
```

### 基础 DAG

```python
# dags/daily_etl.py
from airflow import DAG
from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
}

@dag(
    dag_id="daily_etl",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["etl", "production"],
)
def etl_dag():

    @task
    def extract():
        return fetch_data_from_api()

    @task
    def transform(data: list) -> list:
        return [clean(row) for row in data]

    @task
    def load(data: list):
        write_to_warehouse(data)

    raw = extract()
    clean_data = transform(raw)
    load(clean_data)

etl_dag()
```

### Dynamic Task Mapping

```python
@task
def get_files() -> list[str]:
    return list_s3_files("my-bucket/*.csv")

@task
def process_file(filename: str):
    process(filename)

files = get_files()
process_file.expand(filename=files)  # 每个文件一个任务
```

### Sensors 等待外部条件

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_for_file = S3KeySensor(
    task_id="wait_s3",
    bucket_key="s3://my-bucket/data.csv",
    mode="reschedule",    # 不占 slot
    timeout=3600,
)
```

## 4. Dagster：Asset-First 范式

Dagster 的核心理念：**数据产物（Asset）是一等公民**，不是任务。

```python
# Airflow 思维：
#   task 跑完 → 输出到某处 → 下游 task 读
#   编排器不关心"这份数据是什么"

# Dagster 思维：
#   定义"我产出什么 Asset"
#   Dagster 自动推导依赖
#   可以问：这个 Asset 最后什么时候更新的？谁在用它？
```

### 定义 Asset

```python
# assets.py
import pandas as pd
from dagster import asset, AssetExecutionContext, Config

class ApiConfig(Config):
    api_url: str

@asset(group_name="raw")
def raw_users(context: AssetExecutionContext, config: ApiConfig) -> pd.DataFrame:
    """原始用户数据。"""
    df = pd.read_json(config.api_url)
    context.log.info(f"loaded {len(df)} rows")
    return df

@asset(group_name="processed", deps=[raw_users])
def clean_users(raw_users: pd.DataFrame) -> pd.DataFrame:
    """清洗后的用户。"""
    return raw_users.dropna().drop_duplicates(subset=["email"])

@asset(group_name="analytics", deps=[clean_users])
def user_stats(clean_users: pd.DataFrame) -> dict:
    """用户统计。"""
    return {
        "total": len(clean_users),
        "by_country": clean_users["country"].value_counts().to_dict(),
    }
```

Dagster UI 自动生成血缘图，运维可以直接点 Asset 看：
- 最后成功时间
- 上游是否出错
- 消费这个 Asset 的下游是谁

### 分区（Partitioned Assets）

```python
from dagster import DailyPartitionsDefinition, asset

daily = DailyPartitionsDefinition(start_date="2026-01-01")

@asset(partitions_def=daily)
def daily_orders(context) -> pd.DataFrame:
    date = context.partition_key
    return pd.read_sql(f"""
        SELECT * FROM orders
        WHERE DATE(created_at) = '{date}'
    """, engine)
```

每天自动产出一份；回填只需指定日期范围。

### Resource 和 IO Manager

```python
from dagster import resource, Definitions

@resource
def postgres_engine(context):
    return create_engine(context.resource_config["url"])

defs = Definitions(
    assets=[raw_users, clean_users, user_stats],
    resources={
        "db": postgres_engine.configured({"url": "postgres://..."}),
    },
)
```

**IO Manager** 自动处理 Asset 的读写（不用每个函数里手动 read/write）。

## 5. 两种范式对比

```
Airflow 风格（过程式）：
  DAG 1：extract → transform → load
  DAG 2：extract → transform → load
  每个 DAG 独立，依赖靠"前一个 DAG 跑完"

Dagster 风格（声明式）：
  定义所有 Asset 和依赖
  跑某个 Asset → 自动跑它的上游
  全局视图，血缘清晰
```

**迁移路径**：Airflow DAG 可以逐步拆成 Asset（Airflow 3 也支持了）。

## 6. 生产级配置

### 6.1 失败处理

```python
# Airflow
@dag(default_args={
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(hours=1),
})

# Dagster
@asset(
    retry_policy=RetryPolicy(max_retries=3, delay=300, backoff=Backoff.EXPONENTIAL),
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
```

### 6.2 告警

```python
# Airflow：email_on_failure、Slack callback
def slack_alert(context):
    slack.post(f"Failed: {context['task_instance_key_str']}")

default_args = {"on_failure_callback": slack_alert}

# Dagster：Sensor + Alerting Policy（内置）
@sensor(asset_selection=[critical_asset])
def alert_sensor(context):
    materialization = context.latest_materialization_record
    if materialization.status == "failed":
        send_slack_alert(materialization.asset_key)
```

### 6.3 并发控制

```python
# Airflow：pool
pool = "production_db"
task_db = PythonOperator(
    task_id="heavy_query",
    pool=pool,
    pool_slots=1,
    ...
)

# Dagster：ConcurrencyLimit
from dagster import define_asset_job
job = define_asset_job(
    name="etl",
    selection=[clean_users],
    tags={"dagster/max_retries": "3", "dagster/concurrency_key": "db"},
)
```

## 7. 部署方式

```
Airflow：
├─ 自建：Docker Compose / Helm
├─ Astronomer（托管）
├─ MWAA（AWS）
└─ Cloud Composer（GCP）

Dagster：
├─ 自建：Dagster Open Source
├─ Dagster Cloud（托管，推荐新项目）
└─ 支持 K8s + Serverless 混合

Prefect：
├─ 自建 Server
└─ Prefect Cloud（免费层慷慨）
```

## 8. dbt 集成

dbt 运行也要编排：

```python
# Dagster 方式（最优雅）
from dagster_dbt import dbt_assets, DbtCliResource

@dbt_assets(manifest="target/manifest.json")
def my_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

# Airflow 方式
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

dbt_run = DbtCloudRunJobOperator(task_id="dbt_run", job_id=123)
```

## 9. 反模式

```
❌ 一个超大 DAG 管所有任务
   → 出错时爆炸半径大、调度慢
   ✅ 拆成多个按业务域划分的 DAG

❌ 任务里写死时间（datetime.now()）
   → 回填时逻辑错误
   ✅ 用 execution_date / partition_key

❌ 跨 DAG 通过 XCom 传大数据
   → DB 爆炸
   ✅ 用 S3 / 数据库作为中间存储

❌ 定时 Cron 依赖（A 跑完 5 分钟后 B 再跑）
   → 脆弱
   ✅ 用 ExternalTaskSensor 或 Dagster Asset 依赖

❌ 不在 DAG 里写测试
   → 上线才发现错
   ✅ 单元测试 + dry-run

❌ 所有任务都用最强的 Worker
   → 成本爆
   ✅ 任务分类（CPU / Memory / GPU / Light），按类型调度
```

## 10. 生产检查清单

```
☐ 每个 DAG/Asset 有 Owner 标签
☐ 有失败告警（Slack / PagerDuty）
☐ 关键任务有 SLA 告警
☐ 资源限制（pool / concurrency）
☐ 幂等（重跑同一天不出错）
☐ 有 metadata（runtime、行数、数据质量）
☐ 历史回填有预案
☐ 数据产物和 Dashboard 关联
☐ 代码在 Git + CI 校验
☐ 生产和开发环境隔离
```

## 📖 参考资料

- [Airflow 官方](https://airflow.apache.org/)
- [Dagster 官方](https://docs.dagster.io/)
- [Dagster vs Airflow](https://dagster.io/blog/dagster-airflow)
- [Prefect 官方](https://docs.prefect.io/)
- [Temporal 官方](https://temporal.io/)
- [Data Engineering Weekly](https://www.dataengineeringweekly.com/)

## 11. 2026 年版本演进

> 🔄 更新于 2026-05-16

### 11.1 Airflow 3.1：Human-in-the-Loop（2025-09 发布）

Airflow 3.1 把"人在回路（HITL）"做成内置一等公民——AI/ML 工作流不再需要拼凑 Slack/Email/外部审批工具。来源：[Astronomer Blog](https://www.astronomer.io/blog/introducing-apache-airflow-3-1/)、[Airflow Blog](https://airflow.apache.org/blog/)

**核心新特性**：

| 特性 | 说明 |
|------|------|
| HITL Tasks | DAG 里直接定义"等待人工批准"任务 |
| 17 种语言国际化 | UI 默认支持中文、日文、韩文等 |
| Deadline Alerts | DAG 错过 SLA 直接触发告警（不再依赖 timeout 黑魔法） |
| React Plugin System | 插件用 React 编写，融入新 UI |

**HITL 代码示例**：

```python
from airflow.decorators import dag, task
from airflow.providers.human.operators import HumanInTheLoopOperator
from datetime import datetime

@dag(start_date=datetime(2026, 1, 1), schedule="@daily")
def llm_data_pipeline():

    @task
    def generate_summary():
        # LLM 生成内容
        return {"summary": "...", "confidence": 0.65}

    summary = generate_summary()

    review = HumanInTheLoopOperator(
        task_id="manual_review",
        prompt="请审核 LLM 生成的摘要",
        # 低置信度才进入人工审核
        skip_if=lambda ctx: ctx["task_instance"].xcom_pull(
            task_ids="generate_summary"
        )["confidence"] > 0.9,
        timeout_minutes=30,
    )

    @task
    def publish(approved_summary):
        # 发布到下游
        pass

    publish(review)

llm_data_pipeline()
```

### 11.2 Airflow 3.2：Asset Partitioning + Multi-Team

Airflow 3.2 在 3.1 之后聚焦"数据感知工作流"，将 Asset（资产）的精度提到分区级别。来源：[Airflow 3.2 Blog](https://airflow.apache.org/blog/airflow-3.2.0/)

**关键能力**：

- **Asset 分区编排**：DAG 可以只重跑某个分区的数据，而不是整个表
- **Multi-team Deployment**：同一个 Airflow 集群隔离多个团队，各自的权限/资源/部署节奏
- **同步 Deadline Alert 回调**：deadline 触发后立即调用回调，不再有延迟
- **Task SDK 分离**：worker 不再需要完整的 Airflow 包，缩小镜像体积

**版本时间线**：

| 版本 | 发布 | 重点 |
|------|------|------|
| 3.0 | 2025-04 | DAG Versioning、Event-Driven Scheduling、Remote Execution |
| 3.1 | 2025-09 | HITL、i18n、Deadline Alerts |
| 3.2 | 2026 春季 | Asset Partitioning、Multi-team |

**升级建议**：

```
2.x  →  必须升级！2.x EOL 于 2026 年内（详见 Apache Release Plan）
3.0  →  3.1 / 3.2 都是平滑升级（API 兼容）
3.1  →  3.2（已发布版本）
```

来源：[Apache Airflow Release Plan](https://cwiki.apache.org/confluence/display/AIRFLOW/Release+Plan)
