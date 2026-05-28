# pgvector 与向量搜索

> Author: Walter Wang

<!-- version-check: pgvector 0.8.2 (2026-02-26, CVE-2026-3172 fix), pgvectorscale 0.7.x, PostgreSQL 18.4, HNSW/DiskANN, checked 2026-05-28 -->

## 1. 为什么是 pgvector 不是专用向量库

```
┌──────── pgvector 的价值 ────────┐
│                                  │
│  运维：已有 PG 就能用，不需新集群    │
│  事务：向量和业务数据在同一事务       │
│  混合检索：SQL 和向量查询一起用       │
│  成本：无新增基础设施                │
│  规模：支撑到千万~亿级向量无压力      │
│                                  │
│  什么时候需要专用向量库：            │
│  ├─ 10 亿+ 向量                   │
│  ├─ 极端低延迟（<10ms P99）         │
│  └─ 多租户隔离要求高                │
└─────────────────────────────────┘
```

**2026 年推荐**：先用 pgvector，撑不住再考虑 Qdrant / Milvus / Weaviate。

## 2. 安装

```bash
# Docker 镜像（推荐）
docker run -d \
  -e POSTGRES_PASSWORD=postgres \
  pgvector/pgvector:pg18
```

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 3. 基本用法

```sql
-- 创建表，存 1536 维向量（OpenAI text-embedding-3-small 的维度）
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入
INSERT INTO documents (content, embedding) VALUES
    ('猫是一种哺乳动物', '[0.1, 0.2, ...]'::vector);

-- 三种距离
-- <-> L2 距离（Euclidean）
-- <#> 负内积（Inner product）
-- <=> 余弦距离（Cosine distance）

-- 最近邻查询（语义搜索）
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

## 4. 索引：HNSW vs IVFFlat

```sql
-- HNSW（2026 年推荐）：查询快，构建慢，内存大
-- 参数：
--   m             节点的连接数（16 默认）
--   ef_construction 构建时搜索宽度（64 默认）
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- 查询时可以调参数
SET hnsw.ef_search = 100;  -- 搜索宽度，越大越准但越慢

-- IVFFlat：构建快，查询略慢，内存小
-- 参数：
--   lists         聚类数（sqrt(rows) 是经验值）
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

SET ivfflat.probes = 10;  -- 查询时探查的列表数
```

**选型**：
- 数据量 < 100 万 + 更新频繁 → IVFFlat
- 追求查询性能 + 可以接受较长建索引时间 → HNSW（多数场景）

## 5. 混合检索（Hybrid Search）

生产级 RAG 不只是向量相似度，要结合 BM25 全文检索：

```sql
-- 添加全文检索索引
ALTER TABLE documents ADD COLUMN content_tsv TSVECTOR
    GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED;

CREATE INDEX ON documents USING GIN (content_tsv);

-- 混合查询：RRF（Reciprocal Rank Fusion）
WITH vector_results AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> $1) AS rank
    FROM documents
    ORDER BY embedding <=> $1
    LIMIT 50
),
keyword_results AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(content_tsv, plainto_tsquery('simple', $2)) DESC) AS rank
    FROM documents
    WHERE content_tsv @@ plainto_tsquery('simple', $2)
    LIMIT 50
),
fused AS (
    SELECT
        COALESCE(v.id, k.id) AS id,
        COALESCE(1.0 / (60 + v.rank), 0) + COALESCE(1.0 / (60 + k.rank), 0) AS score
    FROM vector_results v
    FULL OUTER JOIN keyword_results k ON v.id = k.id
)
SELECT d.*, f.score
FROM fused f
JOIN documents d ON d.id = f.id
ORDER BY f.score DESC
LIMIT 10;
```

## 6. 带元数据过滤

```sql
-- ❌ 错误：先取 top-k，再过滤，可能不够
SELECT * FROM (
    SELECT * FROM documents ORDER BY embedding <=> $1 LIMIT 100
) t
WHERE metadata->>'category' = 'tech'
LIMIT 10;

-- ✅ 正确：用 HNSW + 过滤条件
-- pgvector 0.7+ 支持向量索引的过滤下推
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON documents USING GIN ((metadata->'category'));

SELECT * FROM documents
WHERE metadata->>'category' = 'tech'
ORDER BY embedding <=> $1
LIMIT 10;

-- ✅ 或者用 partial index（按租户、分类）
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WHERE metadata->>'category' = 'tech';
```

## 7. Python 集成（FastAPI + SQLAlchemy）

```bash
pip install sqlalchemy psycopg[binary] pgvector openai
```

```python
from sqlalchemy import create_engine, Column, BigInteger, Text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from openai import OpenAI

Base = declarative_base()
engine = create_engine("postgresql+psycopg://user:pass@localhost/db")


class Document(Base):
    __tablename__ = "documents"
    id = Column(BigInteger, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))
    metadata_ = Column("metadata", JSONB)


client = OpenAI()


def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def add_document(content: str, metadata: dict | None = None):
    with Session(engine) as session:
        doc = Document(
            content=content,
            embedding=embed(content),
            metadata_=metadata or {},
        )
        session.add(doc)
        session.commit()


def search(query: str, top_k: int = 10) -> list[Document]:
    query_vec = embed(query)
    with Session(engine) as session:
        return (
            session.query(Document)
            .order_by(Document.embedding.cosine_distance(query_vec))
            .limit(top_k)
            .all()
        )
```

## 8. Java 集成（Spring Data JPA）

```xml
<dependency>
    <groupId>com.pgvector</groupId>
    <artifactId>pgvector</artifactId>
    <version>0.1.6</version>
</dependency>
```

```java
@Entity
@Table(name = "documents")
public class Document {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String content;

    @Column(columnDefinition = "vector(1536)")
    private float[] embedding;
}

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {
    @Query(value = """
        SELECT * FROM documents
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :topK
        """, nativeQuery = true)
    List<Document> findNearest(@Param("embedding") String embedding,
                                @Param("topK") int topK);
}
```

## 9. 常用扩展：text embeddings 内存化

```sql
-- pg_vectorize（Tembo）：在数据库里直接做 embedding
-- 不用应用层调 OpenAI
SELECT vectorize.table(
    job_name  => 'product_search',
    "table"   => 'products',
    primary_key => 'id',
    columns   => ARRAY['name', 'description'],
    transformer => 'openai/text-embedding-3-small',
    schedule  => 'realtime'
);

-- 查询也极简
SELECT * FROM vectorize.search(
    job_name => 'product_search',
    query    => '无线蓝牙耳机',
    return_columns => ARRAY['name', 'price']
);
```

## 10. 性能调优

```sql
-- 查看查询计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM documents
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;

-- 调整参数
-- 构建索引时多用并行
SET max_parallel_maintenance_workers = 7;

-- HNSW 查询精度
SET hnsw.ef_search = 100;  -- 默认 40，越大越准

-- 让 PG 把热数据留在缓存
-- shared_buffers 建议 25% 的内存
-- effective_cache_size 建议 75% 的内存
```

## 11. 容量规划

```
估算向量存储：
  每个 float32 = 4 bytes
  每个 1536 维向量 = 6 KB
  HNSW 索引额外开销约 2-3x

  100 万向量 ≈ 6 GB 数据 + 15-20 GB HNSW 索引 = 25 GB
  1000 万向量 ≈ 60 GB 数据 + 150-200 GB HNSW 索引 = 260 GB

压缩选项：
  ├─ halfvec：float16，存储减半
  ├─ bit：二值向量，极致压缩
  └─ 可以和精度平衡（召回率略降）
```

## 12. 反模式

```
❌ 每个查询都重新 embed 查询字符串
   → 缓存！用 Redis 或 LRU

❌ 单个 embedding 表存所有数据
   → 按业务分表，建 partial index

❌ 不做 chunk
   → 大文档直接 embed 效果很差，应该切 chunk

❌ 只用向量相似度
   → 生产必用混合检索（向量 + BM25 + 过滤）

❌ 不评估召回率
   → 建议定期跑 eval 集

❌ 用 IVFFlat 又频繁更新数据
   → 数据漂移导致准确率下降，改用 HNSW
```

## 13. pgvectorscale：DiskANN 大规模向量搜索

> 🔄 更新于 2026-05-13

当向量数据超过内存容量时，HNSW 索引性能急剧下降。pgvectorscale 扩展提供 **StreamingDiskANN** 索引，将热数据保留在内存、冷数据流式读取磁盘，支撑远超内存的向量规模。

来源：[pgvectorscale GitHub](https://github.com/timescale/pgvectorscale)、[dbi-services 索引对比](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/)

### 13.1 安装

```bash
# 需要 pgvector 0.8+ 作为前置依赖
# Docker（Timescale 官方镜像已内置）
docker run -d timescale/timescaledb-ha:pg18

# 或手动编译安装（Rust 工具链）
cargo install --git https://github.com/timescale/pgvectorscale
```

```sql
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;
-- CASCADE 会自动安装 vector 扩展
```

### 13.2 StreamingDiskANN 索引

```sql
-- 创建 DiskANN 索引（适合超大规模向量）
CREATE INDEX ON documents
USING diskann (embedding vector_cosine_ops);

-- 带参数调优
CREATE INDEX ON documents
USING diskann (embedding vector_cosine_ops)
WITH (
    max_neighbors = 50,        -- 图中每个节点的最大邻居数（默认 50）
    l_value_ib = 100,          -- 索引构建时的搜索宽度
    l_value_is = 100           -- 索引搜索时的搜索宽度
);

-- 查询时调参
SET diskann.query_search_list_size = 100;  -- 越大越准但越慢
SET diskann.query_rescore = 100;           -- 重排数量
```

### 13.3 Statistical Binary Quantization（SBQ）

pgvectorscale 的 SBQ 将 float32 向量压缩为二值表示，内存占用降低 **32x**：

```sql
-- DiskANN 默认启用 SBQ
-- 搜索时先用压缩向量粗筛，再用原始向量精排（rescore）
-- 这就是 query_rescore 参数的作用
```

### 13.4 三种索引选型（2026）

```
┌─────────────────────────────────────────────────────────────────┐
│                  pgvector 索引选型决策树                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  向量数据能放进内存？                                             │
│  ├─ YES → HNSW（最佳查询性能，pgvector 内置）                    │
│  │         适合：< 5000 万 1536 维向量（~300 GB 内存）            │
│  │                                                               │
│  └─ NO  → StreamingDiskANN（pgvectorscale）                      │
│            适合：5000 万 ~ 10 亿+ 向量                            │
│            特点：热数据内存 + 冷数据磁盘流式读取                    │
│                                                                  │
│  IVFFlat：仅在数据量小 + 频繁重建索引场景使用                      │
│           2026 年新项目不推荐                                     │
└─────────────────────────────────────────────────────────────────┘
```

| 特性 | HNSW (pgvector) | StreamingDiskANN (pgvectorscale) | IVFFlat (pgvector) |
|------|----------------|--------------------------------|-------------------|
| 查询延迟 | 最低（全内存） | 中等（部分磁盘 I/O） | 中等 |
| 内存需求 | 高（全索引驻留） | 低（仅热数据） | 中等 |
| 构建速度 | 慢 | 中等 | 快 |
| 过滤支持 | 0.8+ 改进 | Label-based filtering | 有限 |
| 适合规模 | < 5000 万 | 5000 万 ~ 10 亿+ | < 1000 万 |
| 更新友好 | 好 | 好 | 差（需重建） |

来源：[dbi-services pgvector 索引对比](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/)

### 13.5 pgvector 0.8.x 版本改进

pgvector 0.8.0（2024-11）→ 0.8.2（2025 年底）的关键改进：

- **过滤查询代价估算改进**：PostgreSQL 优化器更准确判断何时使用 ANN 索引 vs B-tree 索引，AWS 测试显示过滤查询延迟降低 **9.4x**
- **HNSW 构建速度提升 40%**（大规模数据集）
- **halfvec 类型**：16-bit 浮点存储，存储减半，召回率损失极小
- **IVFFlat 召回率改进**：相同 lists 设置下召回率更高

来源：[pgvector 0.8.0 Released](https://www.postgresql.org/about/news/pgvector-0.8.0-released-2952/)、[AWS Aurora pgvector 0.8.0](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)

## 14. 亿级向量：Amazon S3 Vectors + Aurora 联合方案

> 🔄 更新于 2026-05-13

当向量规模达到数十亿级别，即使 DiskANN 也面临单机存储瓶颈。AWS 推出 S3 Vectors 服务，与 Aurora PostgreSQL 联合查询：

```sql
-- Aurora PostgreSQL 通过 aws_s3_vectors 扩展查询 S3 Vectors
-- 适合：10 亿+ 向量、低频查询、成本敏感场景
-- 不适合：低延迟实时搜索（S3 延迟较高）
```

来源：[AWS Blog - Query billion-scale vectors with SQL](https://aws.amazon.com/blogs/database/query-billion-scale-vectors-with-sql-integrating-amazon-s3-vectors-and-aurora-postgresql/)

## 📖 参考资料

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [pgvectorscale GitHub](https://github.com/timescale/pgvectorscale)
- [Supabase pgvector 指南](https://supabase.com/docs/guides/ai/vector-columns)
- [Neon pgvector 实战](https://neon.tech/blog/pgvector-best-practices)
- [Hybrid Search with pgvector](https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/)
- [dbi-services pgvector 索引对比（2026-03）](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/)
- 关联：[ai-agent/06-RAG进阶/02-向量数据库选型.md](../ai-agent/06-RAG进阶/02-向量数据库选型.md)

## 15. pgvector 0.8.2 与 PG 18.4 协同

> 🔄 更新于 2026-05-28（修复：版本号从虚构的 0.9.1 改为实际的 0.8.2）

<!-- version-check: pgvector 0.8.2 (2026-02-26 release), PostgreSQL 18.4 (2026-05-14), checked 2026-05-28 -->

pgvector 0.8.x 把最低 PostgreSQL 版本提升到 13，对应 PG 18.4 安全发布（2026-05-14，11 个 CVE）后的推荐组合是 **pgvector 0.8.2 + PG 18.4**。

> ⚠️ 重要修正：之前文档中提到的 0.9.1 是错误的版本号——pgvector 当前最新稳定版是 0.8.2（2026-02-26 发布，修复 CVE-2026-3172 并行 HNSW 构建缓冲区溢出）。来源：[pgvector 0.8.2 Released](https://www.postgresql.org/about/news/pgvector-082-released-3245/)

### 15.1 0.8.x 关键变化

- **0.8.2（2026-02-26）安全修复**：修复 CVE-2026-3172，并行 HNSW 索引构建可能泄露其他关系数据或导致服务崩溃，建议立即升级
- **0.8.0（2024-11）核心改进**：HNSW 维护成本下降、过滤查询代价模型改进（AWS 测试显示带过滤向量查询延迟降低 9.4x）
- **HNSW + iterative scan**：0.8 起支持迭代式向量索引扫描，对带过滤的查询召回率显著提升
- **Statistical Binary Quantization（SBQ）成熟**：与 pgvectorscale 配合，把每维向量压成 1 bit，索引体积可降至原来的 1/32，再用原向量做 rerank。来源：[DigitalOcean — Advanced Vector Workloads with pgvectorscale](https://docs.digitalocean.com/products/vector-databases/postgresql/how-to/advanced-workloads/)
- **混合查询代价模型继续修正**：约 15% 的非向量查询时间增加（带 vector 列时），是较此前版本可接受的回归。来源：[markaicode — pgvector vs Redis 2026](https://markaicode.com/vs/pgvector-vs-redis/)（Content was rephrased for compliance with licensing restrictions）

### 15.2 binary_quantize 实战示例

适合内存吃紧、可接受 ~5-10% 召回率损失换 32x 索引体积压缩的场景。

```sql
-- 1. 建索引时直接用 binary_quantize 转 bit 类型
CREATE INDEX ON items
USING hnsw ((binary_quantize(embedding)::bit(1536)) bit_hamming_ops);

-- 2. 查询：先用 Hamming 距离取前 20，再用原向量 rerank 出 top-5
SELECT * FROM (
    SELECT *
    FROM items
    ORDER BY binary_quantize(embedding)::bit(1536)
             <~> binary_quantize('[1,-2,3,...]')
    LIMIT 20
) AS rerank
ORDER BY embedding <=> '[1,-2,3,...]'
LIMIT 5;
```

来源：[pgEdge Documentation — Binary Quantization](https://docs.pgedge.com/pgvector/development/binary-quantization/)

### 15.3 PG 18.4 升级提示

如果用 PG 18.0-18.2 + pgvector 0.8.x 的组合，升级到 PG 18.4 时**必须 REINDEX 依赖 `json_strip_nulls`/`jsonb_strip_nulls` 的索引**。这与 pgvector 索引无关，但很多 RAG 项目用 JSONB 存元数据 + vector 存 embedding，会同时触发：

```sql
-- 检测哪些索引需要重建
SELECT indexrelid::regclass AS index_name, indrelid::regclass AS table_name
FROM pg_index
WHERE indexprs::text LIKE '%json_strip_nulls%'
   OR indexprs::text LIKE '%jsonb_strip_nulls%';

-- REINDEX
REINDEX INDEX CONCURRENTLY my_metadata_idx;
```

来源：[PostgreSQL 18.4 安全发布](https://www.postgresql.org/about/news/postgresql-184-1710-1614-1518-and-1423-released-3297/)、[releasebot — PostgreSQL May 2026](https://releasebot.io/updates/postgresql)

### 15.4 2026 年向量搜索选型表（修订版）

| 场景 | 数据规模 | 推荐方案 | 备注 |
|------|----------|---------|------|
| RAG 单租户 | < 1000 万 | **pgvector 0.8.2 + HNSW** | PG 已部署即用 |
| RAG 中等规模 | 1000 万 ~ 5000 万 | **pgvector 0.8.2 + HNSW + halfvec** | 内存减半 |
| RAG 大规模 | 5000 万 ~ 10 亿 | **pgvectorscale + StreamingDiskANN** | 热数据内存 + 冷数据磁盘 |
| 内存吃紧 | 任意 | **binary_quantize + bit_hamming_ops + rerank** | 索引体积压 32x |
| 数十亿级 | > 10 亿 | **Aurora pgvector 联合 S3 Vectors** | 低频查询、成本敏感 |
| 多租户 + 极低延迟 | 任意 | **专用向量库（Qdrant/Milvus/Weaviate）** | pgvector 不适合 |

来源：[AWS Blog — Aurora + S3 Vectors](https://aws.amazon.com/blogs/database/query-billion-scale-vectors-with-sql-integrating-amazon-s3-vectors-and-aurora-postgresql/)、[Timescale — pgvector 完整指南](https://www.timescale.com/learn/postgresql-extensions-pgvector)
