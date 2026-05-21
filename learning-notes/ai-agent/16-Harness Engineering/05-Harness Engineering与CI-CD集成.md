# Harness Engineering 与 CI/CD 集成
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 核心循环

Agent 写代码 → CI 运行 → 失败 → Agent 读日志 → 修复 → CI 再运行。

```
┌──────────────────────────────────────────┐
│       Harness + CI/CD 完整循环            │
│                                          │
│  Agent 写代码 ──push──→ CI 验证           │
│       ↑                    │             │
│       └── Agent 读日志修复 ←┘ (失败时)     │
│                            │             │
│                       通过 → 开 PR → 人审核│
└──────────────────────────────────────────┘
```

## 2. GitHub Actions — 基础 CI 流水线

```yaml
# .github/workflows/agent-ci.yml
# <!-- 修复于 2026-05-21: actions/checkout v5 → v6（v6 已 GA） -->
name: Agent CI Pipeline
on:
  push:
    branches: [main, 'agent/**']
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e ".[dev]"

      - name: Lint
        run: ruff check . --output-format=json > lint-report.json
        continue-on-error: true
      - name: Type Check
        run: mypy src/ --json-report mypy-report
        continue-on-error: true
      - name: Architecture Tests
        run: pytest tests/test_architecture.py -v --tb=short
      - name: Unit Tests
        run: pytest tests/ -v --tb=short --junitxml=test-report.xml

      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: ci-reports
          path: |
            lint-report.json
            test-report.xml
```

## 3. Agent 自动修复循环

```yaml
# .github/workflows/agent-autofix.yml
name: Agent Auto-Fix
on:
  workflow_run:
    workflows: ["Agent CI Pipeline"]
    types: [completed]

jobs:
  auto-fix:
    if: >
      github.event.workflow_run.conclusion == 'failure' &&
      startsWith(github.event.workflow_run.head_branch, 'agent/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ github.event.workflow_run.head_branch }}
      - name: Download Reports
        uses: actions/download-artifact@v4
        with:
          name: ci-reports
          run-id: ${{ github.event.workflow_run.id }}

      - name: Agent Fix
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --pipe "CI 失败，分析报告并修复：
            Lint: $(cat lint-report.json)
            Tests: $(cat test-report.xml)
            规则：只修复报告问题，不改业务逻辑"

      - name: Commit & Push
        run: |
          git config user.name "agent-bot"
          git config user.email "agent@bot.com"
          git add -A
          git diff --staged --quiet || git commit -m "fix: auto-fix from CI"
          git push

      - name: Check Retry Limit
        run: |
          COUNT=$(git log --oneline --grep="auto-fix" | wc -l)
          [ "$COUNT" -gt 5 ] && echo "::error::超过 5 次，需人工介入" && exit 1
```

## 4. 质量扫描自动化

```yaml
# .github/workflows/quality-sweep.yml
name: Quality Sweep
on:
  schedule:
    - cron: '0 2 * * 1-5'  # 工作日凌晨 2 点
  workflow_dispatch:

jobs:
  sweep:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        module: [src/api, src/service, src/repository]
    steps:
      - uses: actions/checkout@v6
      - name: Scan & Fix
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude --pipe "扫描 ${{ matrix.module }}：
            找出规范问题、复杂逻辑、缺失类型注解。
            每个问题独立 commit，不改业务逻辑。"
      - uses: peter-evans/create-pull-request@v7
        with:
          title: "chore: quality sweep ${{ matrix.module }}"
          branch: "sweep/${{ matrix.module }}-${{ github.run_id }}"
          labels: quality-sweep
```

## 5. 架构约束测试

详细实现见 → Harness Engineering完整指南.md 第 3.3 节。核心思路：

```python
# tests/test_architecture.py — 用 AST 分析强制执行分层依赖
LAYERS = {"types": 0, "config": 1, "repository": 2, "service": 3, "api": 4}

def test_no_upward_dependency():
    """遍历 src/，检查 import 方向，违反则 CI 失败"""
    # AST 解析每个文件的 import，确保只向下依赖
    ...

def test_api_no_direct_db():
    """API 层不能直接导入 sqlalchemy/psycopg 等"""
    ...
```

## 6. IDE Agent 集成

```
Kiro:       .kiro/steering/ + Hooks（postTaskExecution → pytest）
Claude Code: CLAUDE.md 中写明测试命令，Agent 自动循环
Cursor:     .cursorrules 中写明修改后运行测试
```

## 7. 检查清单

```
□ CI 流水线：Lint + 类型 + 测试 + 架构约束
□ Agent 反馈循环：失败报告 JSON 化 + 自动修复 + 重试限制
□ 质量扫描：定时运行 + 自动 PR + 单模块范围
□ 安全：Agent 代码额外审查 + 覆盖率门禁
□ 可观测：报告上传 Artifact + 修复次数追踪
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [GitHub - GitHub Actions Tutorial](https://www.youtube.com/watch?v=R8_veQiYBjI) — GitHub Actions教程
- [DeepLearning.AI - Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/) — 包含工程化章节（免费）

### 📖 官方文档
- [GitHub Actions Docs](https://docs.github.com/en/actions) — GitHub Actions文档
