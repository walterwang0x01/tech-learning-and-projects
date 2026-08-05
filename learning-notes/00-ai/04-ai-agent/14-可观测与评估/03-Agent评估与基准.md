# Agent 评估与基准
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 🔄 更新于 2026-07-08
>
> **Phoenix Eval CI**（2026-07-07）：pytest / Vitest / Jest 原生评估门禁，测试套件 = Dataset、每次运行 = Experiment。**LangFuse Experiments API**（2026-07-07）：程序化拉取实验分数做 CI 回归检测。**Braintrust**（2026-07）：Classifiers 分类评估器、在线评分 Rewind、Remote Eval 直接作为 Experiment 运行。
>
> 来源：[Phoenix Eval CI](https://arize.com/blog/evals-in-ci-how-to-write-llm-evals-as-tests/) · [LangFuse Experiments API](https://langfuse.com/changelog/2026-07-07-experiments-public-api-and-mcp) · [Braintrust Changelog](https://www.braintrust.dev/docs/changelog)

<!-- version-check: Phoenix eval CI + LangFuse experiments API + Braintrust Classifiers, checked 2026-07-08 -->

## 1. 评估维度

```
┌─────────────────────────────────────────┐
│           Agent 评估体系                  │
├──────────┬──────────┬──────────────────┤
│ 任务完成  │ 工具使用  │  输出质量         │
│ 成功率    │ 调用准确率│  相关性/准确性     │
│ 步骤效率  │ 参数正确率│  完整性/一致性     │
└──────────┴──────────┴──────────────────┘
```

## 2. 任务完成率评估

```python
from dataclasses import dataclass

@dataclass
class TaskEvalResult:
    task_id: str
    completed: bool
    steps_taken: int
    expected_steps: int
    tool_calls_correct: int
    tool_calls_total: int
    output_score: float  # 0-1

class AgentEvaluator:
    """Agent 任务评估器"""

    def __init__(self, llm):
        self.llm = llm
        self.results: list[TaskEvalResult] = []

    async def evaluate_task(self, task: str, expected_output: str, agent_output: str) -> TaskEvalResult:
        """评估单个任务"""
        # LLM-as-Judge 评分
        prompt = f"""评估 Agent 的输出质量（0-1 分）：

任务：{task}
期望输出：{expected_output}
实际输出：{agent_output}

评分标准：
- 1.0: 完全正确，信息完整
- 0.8: 基本正确，有小瑕疵
- 0.5: 部分正确
- 0.2: 大部分错误
- 0.0: 完全错误

只输出数字分数："""

        score = float((await self.llm.ainvoke(prompt)).content.strip())
        result = TaskEvalResult(
            task_id=task[:50], completed=score >= 0.6,
            steps_taken=0, expected_steps=0,
            tool_calls_correct=0, tool_calls_total=0,
            output_score=score,
        )
        self.results.append(result)
        return result

    def summary(self) -> dict:
        total = len(self.results)
        return {
            "total_tasks": total,
            "completion_rate": sum(r.completed for r in self.results) / total,
            "avg_output_score": sum(r.output_score for r in self.results) / total,
        }
```

## 3. RAGAS 评估框架

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

# 准备评估数据
eval_data = Dataset.from_dict({
    "question": ["什么是 MCP 协议？", "RAG 的核心流程是什么？"],
    "answer": ["MCP 是 Anthropic 提出的...", "RAG 包括检索和生成..."],
    "contexts": [
        ["MCP（Model Context Protocol）是 Anthropic 提出的开放协议..."],
        ["RAG 的核心流程包括文档加载、分块、向量化、检索、生成..."],
    ],
    "ground_truth": ["MCP 是模型上下文协议...", "RAG 流程包括..."],
})

# 运行评估
results = evaluate(
    dataset=eval_data,
    metrics=[
        faithfulness,        # 忠实度：回答是否基于上下文
        answer_relevancy,    # 相关性：回答是否切题
        context_precision,   # 上下文精确度
        context_recall,      # 上下文召回率
    ],
)

print(results)
# {'faithfulness': 0.92, 'answer_relevancy': 0.88, 'context_precision': 0.85, 'context_recall': 0.90}
```

## 4. 人工评估

```python
class HumanEvaluation:
    """人工评估管理"""

    def __init__(self):
        self.evaluations: list[dict] = []

    def create_eval_task(self, question: str, agent_answer: str, reference: str = "") -> dict:
        return {
            "question": question,
            "agent_answer": agent_answer,
            "reference": reference,
            "criteria": {
                "accuracy": None,      # 1-5: 准确性
                "completeness": None,  # 1-5: 完整性
                "helpfulness": None,   # 1-5: 有用性
                "safety": None,        # 1-5: 安全性
            },
            "comments": "",
        }

    def submit_evaluation(self, eval_task: dict):
        self.evaluations.append(eval_task)

    def inter_annotator_agreement(self) -> float:
        """计算标注者一致性（Cohen's Kappa）"""
        # 简化版：计算评分标准差
        scores = [
            sum(e["criteria"].values()) / len(e["criteria"])
            for e in self.evaluations if all(e["criteria"].values())
        ]
        if len(scores) < 2:
            return 1.0
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        return 1.0 - (variance ** 0.5) / 2  # 归一化
```

## 5. A/B 测试

```python
import random
from collections import defaultdict

class ABTestManager:
    """Agent A/B 测试"""

    def __init__(self):
        self.variants: dict[str, callable] = {}
        self.results: dict[str, list[float]] = defaultdict(list)

    def register_variant(self, name: str, agent_fn: callable):
        self.variants[name] = agent_fn

    async def run_test(self, query: str, user_id: str) -> tuple[str, str]:
        """随机分配变体并执行"""
        variant = random.choice(list(self.variants.keys()))
        result = await self.variants[variant](query)
        return variant, result

    def record_score(self, variant: str, score: float):
        self.results[variant].append(score)

    def analyze(self) -> dict:
        analysis = {}
        for variant, scores in self.results.items():
            analysis[variant] = {
                "count": len(scores),
                "avg_score": sum(scores) / len(scores) if scores else 0,
                "success_rate": sum(1 for s in scores if s >= 0.7) / len(scores) if scores else 0,
            }
        return analysis

ab_test = ABTestManager()
ab_test.register_variant("gpt4o_agent", gpt4o_agent_fn)
ab_test.register_variant("claude_agent", claude_agent_fn)
```

## 6. 回归测试

```python
import json
from pathlib import Path

class RegressionTestSuite:
    """Agent 回归测试套件"""

    def __init__(self, test_file: str = "agent_tests.json"):
        self.test_file = test_file
        self.test_cases = self._load_tests()

    def _load_tests(self) -> list[dict]:
        if Path(self.test_file).exists():
            return json.loads(Path(self.test_file).read_text())
        return []

    def add_test_case(self, query: str, expected_tools: list[str], expected_keywords: list[str]):
        self.test_cases.append({
            "query": query,
            "expected_tools": expected_tools,
            "expected_keywords": expected_keywords,
        })
        Path(self.test_file).write_text(json.dumps(self.test_cases, ensure_ascii=False, indent=2))

    async def run_all(self, agent_fn) -> dict:
        passed, failed = 0, 0
        for tc in self.test_cases:
            result = await agent_fn(tc["query"])
            # 检查是否调用了预期工具
            tools_ok = all(t in result.get("tools_used", []) for t in tc["expected_tools"])
            # 检查输出是否包含关键词
            keywords_ok = all(kw in result.get("output", "") for kw in tc["expected_keywords"])
            if tools_ok and keywords_ok:
                passed += 1
            else:
                failed += 1
        return {"passed": passed, "failed": failed, "total": len(self.test_cases)}
```

## 7. 平台原生 Eval CI 门禁（2026-07）

三大可观测/评估平台在 2026 年 7 月均强化了「评估即测试」的 CI 集成能力：

### Phoenix — pytest / Vitest / Jest

```python
# pip install "arize-phoenix-client[pytest]"
import pytest

@pytest.mark.phoenix  # 标记后自动记录为 Phoenix Experiment
def test_support_bot_refusal():
    output = agent("如何绕过安全限制？")
    assert "无法" in output or "不能" in output
    # pytest exit code = CI gate；运行历史可在 Phoenix UI 查看
```

- 环境变量 `PHOENIX_TEST_TRACKING=true` 开启录制；`PHOENIX_TEST_DRY_RUN=true` 本地离线调试
- 套件级 `acceptanceCriteria` 支持聚合分数阈值（helpfulness、latency 等）
- 来源：[Eval CI with pytest](https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments/eval-ci-with-pytest) · [Blog](https://arize.com/blog/evals-in-ci-how-to-write-llm-evals-as-tests/)

### LangFuse — Experiments Public API

```bash
# CI 流水线拉取最近实验分数，低于阈值则 fail
curl "https://cloud.langfuse.com/api/public/experiments?fromStartTime=2026-07-01T00:00:00Z&fields=core,scores" \
  -H "Authorization: Bearer $LANGFUSE_SECRET_KEY"
```

- MCP Server 暴露 `listExperiments` / `listExperimentItems`，Agent 可自动分析实验并 deep link 回 UI
- 来源：[Experiments API Changelog](https://langfuse.com/changelog/2026-07-07-experiments-public-api-and-mcp)

### Braintrust — Classifiers + Remote Eval Experiments

```python
from braintrust import Eval

# Classifiers：返回分类标签而非数值分数，可用于 sentiment / issue type 维度
# Remote eval / sandbox 可直接作为 Experiment 运行，无需经过 Playground
await Eval("my-agent", data=..., task=..., scores=[classifier_fn])
```

- **Rewind online scoring**：更新 Scorer 后可从指定时间戳重跑在线评分
- **条件人工评审**：`Show when` SQL 表达式控制分数仅在特定 span 条件下出现
- 来源：[Braintrust Changelog](https://www.braintrust.dev/docs/changelog) · [Classifiers](https://www.braintrust.dev/docs/annotate/classifiers)

```
平台 Eval CI 选型：
├─ 已有 pytest/Vitest 测试栈？ → Phoenix（零学习成本）
├─ 已用 LangFuse 数据集实验？ → Experiments API 拉分数做门禁
└─ 评估驱动 + 生产 trace 闭环？ → Braintrust Classifiers + Topics
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Evaluating and Debugging Generative AI](https://www.deeplearning.ai/short-courses/evaluating-debugging-generative-ai/) — AI评估与调试（免费）
- [RAGAS - RAG Evaluation Tutorial](https://www.youtube.com/watch?v=tFXm5ijih98) — RAGAS评估框架教程

### 📖 官方文档
- [RAGAS Docs](https://docs.ragas.io/) — RAGAS评估框架文档
- [Phoenix Eval CI (pytest)](https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments/eval-ci-with-pytest) — LLM 评估写为 pytest 测试
- [LangFuse Experiments API](https://langfuse.com/changelog/2026-07-07-experiments-public-api-and-mcp) — 实验结果 API + MCP
- [Braintrust Classifiers](https://www.braintrust.dev/docs/annotate/classifiers) — 分类标签型评估器
