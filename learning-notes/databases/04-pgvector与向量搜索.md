# pgvector 与向量搜索

> Author: Walter Wang

<!-- version-check: pgvector 0.8.0, PostgreSQL 18, HNSW index, checked 2026-05-10 -->

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

## 📖 参考资料

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Supabase pgvector 指南](https://supabase.com/docs/guides/ai/vector-columns)
- [Neon pgvector 实战](https://neon.tech/blog/pgvector-best-practices)
- [Hybrid Search with pgvector](https://jkatz05.com/post/postgres/hybrid-search-postgres-pgvector/)
- 关联：[ai-agent/06-RAG进阶/02-向量数据库选型.md](../ai-agent/06-RAG进阶/02-向量数据库选型.md)
