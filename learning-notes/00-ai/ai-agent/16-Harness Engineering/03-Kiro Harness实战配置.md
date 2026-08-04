# Kiro Harness 实战配置
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

本文档提供一套可直接使用的 Kiro Harness 配置模板，将 Harness Engineering
的五大实践落地为 Kiro 的 Steering + Hooks + Specs 体系。

## 2. 完整目录结构

```
.kiro/
├── steering/                    # Harness 地图层
│   ├── project-overview.md      # 项目全局地图（auto）
│   ├── architecture.md          # 架构规范（auto）
│   ├── coding-standards.md      # 编码标准（auto）
│   ├── api-conventions.md       # API 约定（fileMatch: **/routes/*）
│   ├── testing-guide.md         # 测试规范（fileMatch: **/test_*）
│   └── database-guide.md       # 数据库规范（fileMatch: **/models/*）
│
├── hooks/                       # Harness 反馈循环层
│   ├── lint-on-save.hook        # 保存时自动 lint
│   ├── test-on-save.hook        # 保存时自动测试
│   ├── arch-guard.hook          # 写操作前架构检查
│   ├── verify-after-task.hook   # 任务完成后验证
│   └── security-check.hook      # 安全检查
│
├── specs/                       # Harness 执行计划层
│   └── (按功能创建)
│
└── settings/
    └── mcp.json                 # MCP 工具配置
```

## 3. Steering 文件模板

### project-overview.md（全局地图）

```markdown
---
inclusion: auto
---

## 项目
[项目名] — [一句话描述]

## 技术栈
- 语言: Python 3.12 / TypeScript 5.x
- 框架: FastAPI / Next.js
- 数据库: PostgreSQL + Redis
- 测试: pytest / Vitest

## 目录结构
src/
├── types/       # 类型定义（无依赖）
├── config/      # 配置管理（依赖 types）
├── repository/  # 数据访问（依赖 config）
├── service/     # 业务逻辑（依赖 repository）
├── api/         # API 路由（依赖 service）
└── common/      # 共享工具

## 常用命令
- 测试: pytest -xvs
- Lint: ruff check .
- 类型检查: mypy src/
- 启动: uvicorn app.main:app --reload

## 关键约束
- 依赖方向: types → config → repository → service → api
- 所有公共函数必须有类型注解和 docstring
- API 返回统一 Result 格式
```

### coding-standards.md（编码标准）

```markdown
---
inclusion: auto
---

## 命名
- 文件: snake_case.py
- 类: PascalCase
- 函数/变量: snake_case
- 常量: UPPER_SNAKE_CASE
- API 路由: /kebab-case

## 错误处理
- 使用自定义异常类，不用裸 Exception
- API 层统一捕获，返回标准错误格式
- 业务层抛出领域异常，不处理 HTTP 细节

## 函数规范
- 单一职责，不超过 30 行
- 必须有类型注解（参数 + 返回值）
- 公共函数必须有 docstring
- 避免超过 3 层嵌套

## 测试规范
- 测试文件与源文件同目录: test_xxx.py
- 每个公共函数至少一个测试
- 使用 pytest fixture，不在测试中硬编码数据
- Mock 外部依赖，不 Mock 被测代码
```

## 4. Hooks 配置模板

### lint-on-save.hook

```json
{
  "name": "Lint on Save",
  "version": "1.0.0",
  "description": "文件保存时自动运行 lint 检查",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "runCommand",
    "command": "ruff check --fix ."
  }
}
```

### arch-guard.hook（架构守卫）

```json
{
  "name": "Architecture Guard",
  "version": "1.0.0",
  "description": "写文件前检查是否违反分层架构",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "在写入之前，检查这段代码是否遵循项目的分层架构规则（types → config → repository → service → api）。如果存在反向依赖（如 service 导入 api 的内容），必须拒绝并重新设计。同时检查是否遵循 coding-standards.md 中的命名和函数规范。"
  }
}
```

### verify-after-task.hook（任务完成验证）

```json
{
  "name": "Verify After Task",
  "version": "1.0.0",
  "description": "Spec 任务完成后自动运行完整验证",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "pytest -x --tb=short && ruff check . && mypy src/"
  }
}
```

### auto-fix-loop.hook（自动修复循环）

```json
{
  "name": "Auto Fix on Agent Stop",
  "version": "1.0.0",
  "description": "Agent 完成后如果测试失败，提示自动修复",
  "when": {
    "type": "agentStop"
  },
  "then": {
    "type": "askAgent",
    "prompt": "运行 pytest -x --tb=short 检查是否有测试失败。如果有失败的测试，分析失败原因并修复代码，然后再次运行测试确认修复成功。重复此过程直到所有测试通过。"
  }
}
```

## 5. 自动循环模式实现

这是你提到的"黑盒自动运转"模式。通过组合 Hooks 实现：

```
Agent 执行任务
    │
    ▼
[postTaskExecution hook] → 运行 pytest + lint + mypy
    │
    ├── 全部通过 → 完成 ✅
    │
    └── 有失败 → [agentStop hook] 触发
                    │
                    ▼
              Agent 读取失败日志
              自动修复代码
                    │
                    ▼
              [fileEdited hook] → 再次运行测试
                    │
                    ├── 通过 → 完成 ✅
                    └── 失败 → 继续循环...

退出条件（防止无限循环）：
- 在 agentStop hook 的 prompt 中加入：
  "如果连续修复 3 次仍然失败，停止并报告问题"
```

## 6. 团队编码基线模板

将以上配置打包为团队标准，新项目直接复制使用：

```bash
# 初始化项目 Harness
cp -r templates/.kiro .kiro

# 目录结构
templates/
├── .kiro/
│   ├── steering/
│   │   ├── project-overview.md    # 修改项目名和技术栈
│   │   ├── architecture.md        # 通用架构规范
│   │   └── coding-standards.md    # 通用编码标准
│   └── hooks/
│       ├── lint-on-save.hook
│       ├── arch-guard.hook
│       ├── verify-after-task.hook
│       └── auto-fix-loop.hook
├── tests/
│   └── test_architecture.py       # 架构约束测试
├── pyproject.toml                  # 统一工具配置
└── .github/
    └── workflows/
        └── quality-sweep.yml      # 定期质量扫描
```

## 7. 效果度量

```
搭建 Harness 前后对比：

指标                    Before      After
─────────────────────────────────────────
Agent 首次通过率        30-40%      70-80%
人工修复时间/PR         15-30 min   2-5 min
架构违规率              频繁        接近 0
代码规范一致性          60%         95%+
日均 PR 产出            1-2 个      3-5 个

注：数据为 OpenAI 内部实验参考值，实际效果因项目而异
```
## 🎬 推荐视频资源

### 📖 官方文档
- [Kiro Documentation](https://kiro.dev/docs) — Kiro官方文档
- [Kiro Steering Guide](https://kiro.dev/docs/steering) — Steering配置指南
