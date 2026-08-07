# briefing-kit 开源项目 — 需求

## 目标

把 `tech-learning-and-projects/scripts/briefing_tools/` 抽取为一个独立可安装的 Python CLI 包，开源到 `github.com/walterwang0x01/briefing-kit`，MIT 协议。

## 核心原则

1. **原仓库继续正常工作** — 抽取后 `tech-learning-and-projects` 的简报流水线不能断。最终可以让原仓库 `pip install briefing-kit` 并删掉自己的 `scripts/briefing_tools/`，但这是后续步骤，不在本次范围内。
2. **零外部依赖** — 引擎本身只用 Python 标准库（当前已满足）。LLM 调用由外部 agent 负责，不引入 openai / anthropic 等 SDK。
3. **个人信息剥离** — 不包含：Walter 的 RSS 源列表、偏好栈、评分覆盖、简报 md 内容、published-index、source-health。
4. **机制完整保留** — 候选集互斥切分、URL 复用检查、熔断自愈、零产出检测、条目计数、BriefingDoc schema、render + 三道校验，全部保留。

## 产出物

### 仓库结构

```
briefing-kit/
├── README.md                    # 架构图 + 30 秒 quick start + 设计亮点
├── LICENSE                      # MIT
├── pyproject.toml               # 可安装，CLI 入口 briefing-kit
├── src/briefing_kit/            # 引擎（从 scripts/briefing_tools/ 重命名）
│   ├── __init__.py
│   ├── cli.py                   # 主命令
│   ├── config.py                # 路径改为基于项目根（自动探测或 --project）
│   ├── ingest.py
│   ├── classify.py
│   ├── candidates.py
│   ├── render.py
│   ├── health.py
│   ├── notify.py
│   ├── storage.py
│   ├── ...（其余模块）
│   └── templates/               # init 命令用的骨架文件
│       ├── config.example.json
│       ├── prompts/_shared.md
│       └── prompts/curate.example.md
├── tests/                       # 232 个测试
│   ├── conftest.py
│   ├── fixtures/
│   └── test_*.py
├── docs/
│   ├── architecture.md          # v3.1 流水线设计
│   ├── failure-modes.md         # 5 个 silent failure 的诊断记录
│   └── decisions.md             # 设计决策（为什么候选集互斥、为什么 half-open...）
└── examples/
    └── minimal/                 # 3 个 RSS 源的最小可运行示例
        ├── config.json
        └── prompts/
```

### CLI 命令

```
briefing-kit init <project-name>    # 生成项目骨架
briefing-kit run-all                # 主流水线（ingest → classify → candidates → cleanup）
briefing-kit render --json <path>   # JSON → md + 三道校验
briefing-kit register --topic <t>   # 登记 URL
briefing-kit finalize --topic all   # 收尾（register + index + notify + 待办汇总）
briefing-kit health                 # 源健康状态
briefing-kit doctor                 # 索引一致性检查
briefing-kit status                 # 状态面板
```

### 关键改动点（vs 原代码）

| 原代码 | 开源版 |
|---|---|
| `REPO_ROOT` 硬编码为脚本目录的 parent | 自动探测（向上找 `.briefing-kit/` 或 `config.json`）或 `--project` 参数 |
| 配置路径 `.kiro/briefings/config.json` | `.briefing-kit/config.json`（不依赖 Kiro 目录结构） |
| 产出路径 `learning-notes/_briefings/` | 可配置，默认 `output/` |
| source-health 路径 `.kiro_tmp/briefings/` | `.briefing-kit/.cache/` |
| runs 目录 `.kiro_tmp/briefings/runs/` | `.briefing-kit/.cache/runs/` |
| `get_env_var` 搜索 sibling 项目的 .env | 只读当前项目的 `.env` |
| `get_bark_url` 推送 | 保留但可选（配置里 `bark_url` 为空则不推） |
| Walter 偏好栈 boost | 移到 config 的 `score_overrides` 里，示例配置不包含 |

### 文档重点

`docs/failure-modes.md` 是最有传播力的内容，包含：

1. **并行 curate 破坏跨主题去重** — cross_topic_dup 判据在并行下失效，因为 subagent 同时写 md 互相看不见
2. **熔断源永不自愈** — 跳过时不调 record_source_result，consecutive_failures 冻结在阈值
3. **推送计数漏数自由块** — count_briefing_items 不认 `**标题** — 描述` 格式
4. **web search 补充链接绕过全部去重** — 不经候选集的链接无人管
5. **抓取成功但零产出无告警** — HTTP 200 + XML 合法 + 0 item，全链路判 ok

每条包含：现象 → 根因 → 为什么难发现 → 怎么修 → 怎么防回归。

## 不做的事

- 不改原仓库的任何代码（本次只做新仓库的创建）
- 不发布到 PyPI（等 v0.1.0 稳定后再做）
- 不写 MCP server / Kiro Power（后续迭代）
- 不做 Web UI

## 验证标准

1. `briefing-kit init demo && cd demo && briefing-kit run-all` 能跑通
2. `pytest tests/` 232 个测试全绿
3. README 的 quick start 复制粘贴能跑
4. `git log` 里没有 Walter 的个人 config / 源列表 / 简报内容
