# GraphRAG 知识图谱
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 知识图谱基础

```
传统 RAG：文档 → 分块 → 向量 → 相似度检索
GraphRAG：文档 → 实体/关系提取 → 知识图谱 → 图检索 + 向量检索

优势：
- 捕获实体间的关系（传统 RAG 丢失）
- 支持多跳推理（A→B→C）
- 全局摘要能力（跨文档理解）
```

## 2. 实体关系提取

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.2", temperature=0)  # <!-- 修复于 2026-05-13: gpt-4o 已退役 -->

extraction_prompt = ChatPromptTemplate.from_template("""
从以下文本中提取实体和关系，以 JSON 格式输出。

文本：{text}

输出格式：
{{
  "entities": [
    {{"name": "实体名", "type": "类型", "description": "描述"}}
  ],
  "relationships": [
    {{"source": "实体A", "target": "实体B", "relation": "关系", "description": "描述"}}
  ]
}}
""")

text = "OpenAI 开发了 GPT-5.2 模型，该模型支持多模态输入。Anthropic 推出了 Claude Sonnet 4.6，在代码生成方面表现优秀。"
result = (extraction_prompt | llm).invoke({"text": text})
print(result.content)
# {"entities": [{"name": "OpenAI", "type": "公司", ...}, {"name": "GPT-5.2", "type": "模型", ...}],
#  "relationships": [{"source": "OpenAI", "target": "GPT-5.2", "relation": "开发", ...}]}
```

## 3. Neo4j 知识图谱存储

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

def create_knowledge_graph(entities, relationships):
    """将提取的实体和关系存入 Neo4j"""
    with driver.session() as session:
        # 创建实体节点
        for entity in entities:
            session.run(
                "MERGE (e:Entity {name: $name}) SET e.type = $type, e.description = $desc",
                name=entity["name"], type=entity["type"], desc=entity["description"],
            )

        # 创建关系
        for rel in relationships:
            session.run(
                """MATCH (a:Entity {name: $source}), (b:Entity {name: $target})
                   MERGE (a)-[r:RELATES {type: $relation}]->(b)
                   SET r.description = $desc""",
                source=rel["source"], target=rel["target"],
                relation=rel["relation"], desc=rel["description"],
            )

# 图查询
def graph_query(question: str) -> list:
    """基于问题进行图检索"""
    # 先提取问题中的实体
    entities = extract_entities(question)

    with driver.session() as session:
        # 查找相关实体及其 1-2 跳关系
        result = session.run("""
            MATCH (e:Entity)-[r*1..2]-(related:Entity)
            WHERE e.name IN $entities
            RETURN e, r, related
            LIMIT 20
        """, entities=entities)
        return [record.data() for record in result]
```

## 4. Microsoft GraphRAG

```python
# Microsoft GraphRAG 使用流程
# pip install graphrag

# 1. 初始化项目
# graphrag init --root ./my_project

# 2. 配置 settings.yaml
"""
llm:
  model: gpt-5.2
  api_key: ${OPENAI_API_KEY}

embeddings:
  model: text-embedding-3-small

chunks:
  size: 300
  overlap: 100

entity_extraction:
  max_gleanings: 1

community_reports:
  max_length: 2000
"""

# 3. 构建索引（提取实体、关系、社区）
# graphrag index --root ./my_project

# 4. 查询
# 全局查询（跨文档摘要）
# graphrag query --root ./my_project --method global --query "AI Agent 的发展趋势"

# 局部查询（特定实体相关）
# graphrag query --root ./my_project --method local --query "MCP 协议的核心特点"
```

## 5. 图 + 向量混合检索

```python
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings

# Neo4j 同时支持图查询和向量搜索
graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="password")

# 创建向量索引
vector_store = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    node_label="Entity",
    text_node_properties=["name", "description"],
    embedding_node_property="embedding",
)

def hybrid_graph_retrieval(question: str) -> str:
    """图 + 向量混合检索"""
    # 1. 向量相似度检索
    vector_results = vector_store.similarity_search(question, k=5)

    # 2. 图结构检索（关系遍历）
    graph_results = graph.query("""
        MATCH (e:Entity)-[r]->(related)
        WHERE e.name CONTAINS $keyword
        RETURN e.name, type(r), related.name, related.description
        LIMIT 10
    """, params={"keyword": extract_keyword(question)})

    # 3. 合并结果
    context = format_results(vector_results, graph_results)
    return context
```

## 6. 适用场景

```
GraphRAG 适合：
├── 多实体关系复杂的领域（医疗、法律、金融）
├── 需要多跳推理的问答
├── 跨文档全局摘要
└── 实体关系变化频繁的动态知识库

传统 RAG 足够：
├── 单文档问答
├── 事实性检索
└── 实体关系简单的场景
```
## 🎬 推荐视频资源

- [Microsoft Research - GraphRAG](https://www.youtube.com/watch?v=r09tJfnassM) — 微软GraphRAG官方讲解
- [DeepLearning.AI - Knowledge Graphs for RAG](https://www.deeplearning.ai/short-courses/knowledge-graphs-rag/) — 知识图谱+RAG（免费）
