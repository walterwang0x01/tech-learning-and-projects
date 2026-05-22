---
name: doc-translation
description: 翻译各种格式的文档变成中文。用户说"翻译"、"translate"、"翻成中文"、"帮我翻译这个文档/文件"时使用。支持 Markdown、TXT、PDF、DOCX 等格式，通过分块策略处理长文档。
---

# 文档翻译 Skill

将英文文档翻译为中文的完整工作流。

## 适用场景

- 用户要求翻译文档、文件内容
- 用户拖入英文文档要求翻译
- 用户指定文件路径要求翻译

## 工作流程

### 场景 1：短文档（< 5000 字符）

直接在对话中翻译，无需切分。

1. 读取文件内容
2. 按照下方翻译规范翻译
3. 将翻译结果写入 `{原文件名}-zh.md`

### 场景 2：中等文档（5000 - 15000 字符）

分 2-3 次翻译。

1. 读取文件，按标题/段落切分为 2-3 块
2. 逐块翻译，保持上下文连贯
3. 合并结果写入 `{原文件名}-zh.md`

### 场景 3：长文档（> 15000 字符）

使用切分脚本。

1. 告知用户文档较长，建议使用切分工具：
   ```bash
   python scripts/doc-translator/split_doc.py <文件路径> --chunk-size 3000
   ```
2. 脚本会生成 `{文件名}-chunks/` 目录，包含多个小文件和翻译清单
3. 用户逐个打开小文件，让我翻译
4. 全部翻译完成后，运行合并脚本：
   ```bash
   python scripts/doc-translator/merge_translated.py <chunks目录>
   ```

### 场景 4：PDF / DOCX 文件

1. 先用脚本转换+切分：
   ```bash
   # PDF（需要 pip install pymupdf）
   python scripts/doc-translator/split_doc.py document.pdf

   # DOCX（需要 pip install python-docx）
   python scripts/doc-translator/split_doc.py document.docx
   ```
2. 然后按场景 3 的流程逐块翻译

## 翻译规范

### 基本原则

- **忠实原文**：准确传达原文含义，不添加、不遗漏
- **自然流畅**：符合中文表达习惯，不是逐词翻译
- **技术准确**：技术术语翻译准确，必要时保留英文

### 术语处理

- 通用技术术语翻译为中文：API → 接口，database → 数据库，deploy → 部署
- 专有名词保留英文：Kubernetes、Docker、React、Python
- 首次出现的重要术语：中文翻译（English Original）
- 代码中的标识符不翻译：函数名、变量名、类名保持原样

### 格式规范

- 保持原文的 Markdown 格式结构（标题层级、列表、代码块）
- 代码块内容不翻译，仅翻译代码注释
- 表格结构保持不变，仅翻译单元格文本内容
- 链接文字翻译，URL 保持不变：`[翻译后的文字](原URL)`
- 中英文之间加空格：`这是一个 Markdown 文件`
- 中文与数字之间加空格：`共 87 页`

### 翻译风格

- 技术文档：简洁准确，使用"您"而非"你"
- 教程/指南：亲切自然，可以用"你"
- 学术论文：正式严谨，使用被动语态的中文对应表达
- 根据原文风格自动判断，不确定时问用户

### 分块翻译时的上下文保持

- 每块翻译前回顾前一块的最后几行，保持术语和风格一致
- 如果前文已经确定了某个术语的翻译，后续保持一致
- 跨块的句子在下一块开头补完

## 输出规范

- 翻译结果文件命名：`{原文件名}-zh.md`
- 输出目录：与原文件同目录，或用户指定的目录
- 文件开头添加翻译信息注释（可选）：
  ```markdown
  <!-- 翻译自: original-filename.md -->
  <!-- 翻译时间: 2024-xx-xx -->
  ```

## 工具脚本位置

- 切分脚本：`scripts/doc-translator/split_doc.py`
- 合并脚本：`scripts/doc-translator/merge_translated.py`
- 依赖说明：`scripts/doc-translator/requirements.txt`

## 术语表（持续积累）

在翻译过程中遇到的领域术语，记录在此供后续翻译参考：

| English | 中文 | 备注 |
|---------|------|------|
| Agent | 智能体 / Agent | 上下文决定 |
| Prompt | 提示词 | |
| Token | Token / 令牌 | LLM 语境用 Token |
| Fine-tuning | 微调 | |
| Embedding | 嵌入 / 向量化 | |
| RAG | RAG（检索增强生成） | 首次出现写全称 |
| Pipeline | 管道 / 流水线 | |
| Middleware | 中间件 | |
| Deployment | 部署 | |
| Containerization | 容器化 | |
| Orchestration | 编排 | |
| Microservice | 微服务 | |
| Observability | 可观测性 | |
| Idempotent | 幂等 | |

用户可以要求扩展此术语表。
