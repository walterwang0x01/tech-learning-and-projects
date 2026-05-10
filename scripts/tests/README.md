# 简报工具测试套件

```bash
# 跑全部
python3 -m unittest discover scripts/tests

# 跑单个文件
python3 -m unittest scripts.tests.test_classify

# verbose
python3 -m unittest discover scripts/tests -v
```

## 覆盖范围

| 文件 | 内容 | 关键回归点 |
|------|------|------------|
| `test_url.py` | URL 归一化 | utm 剥离、尾斜杠、根路径保留 |
| `test_schemas.py` | 数据校验 | 必填字段、类型转换、截断 |
| `test_classify.py` | 规则分类 + 评分 | "rag" 不误命中 "Frag"、source hint fallback、primacy override |
| `test_dedup.py` | 去重 | Jaccard 基本正确、shingle 近义检测、保留高分 |
| `test_candidates.py` | 主题分流 | min-score、published-before、require-main-topic |
| `test_storage.py` | 存储 | 原子写入、md 校验、register 事务性 |
| `test_health.py` | 源健康 | 熔断计数、同一天只累计一次、reset |
| `test_retention.py` | 清理 | cutoff 日期、忽略非日期目录 |
| `test_integration.py` | 端到端 | 多主题候选集不互相污染（核心回归） |

## 依赖

纯标准库，`unittest`。不需要 pytest / fixture library。
