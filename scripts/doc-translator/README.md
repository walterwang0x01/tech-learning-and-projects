# 文档翻译工具

配合 Kiro doc-translation Skill 使用的辅助脚本。

## 工作流

```
大文档 → split_doc.py 切分 → Kiro 逐块翻译 → merge_translated.py 合并
```

## 快速开始

### 1. 安装依赖（按需）

```bash
# 如果只翻译 Markdown/TXT，无需安装任何依赖

# 如果需要翻译 PDF
pip install pymupdf

# 如果需要翻译 DOCX
pip install python-docx
```

### 2. 切分文档

```bash
# Markdown 文件
python scripts/doc-translator/split_doc.py path/to/document.md

# PDF 文件
python scripts/doc-translator/split_doc.py path/to/document.pdf

# DOCX 文件
python scripts/doc-translator/split_doc.py path/to/document.docx

# 自定义块大小（默认 3000 字符）
python scripts/doc-translator/split_doc.py document.md --chunk-size 5000

# 指定输出目录
python scripts/doc-translator/split_doc.py document.md --output-dir ./my-chunks
```

### 3. 逐块翻译

打开 `{文件名}-chunks/` 目录中的文件，逐个在 Kiro 中翻译：
- 打开文件，对 Kiro 说"翻译成中文"
- Kiro 会按照 doc-translation Skill 的规范翻译
- 翻译结果保存为 `{原文件名}-zh.md`

### 4. 合并结果

```bash
python scripts/doc-translator/merge_translated.py ./document-chunks/

# 指定输出文件名
python scripts/doc-translator/merge_translated.py ./document-chunks/ --output final.md
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `split_doc.py` | 将大文档切分为多个小文件 |
| `merge_translated.py` | 将翻译后的小文件合并为完整文档 |
| `requirements.txt` | Python 依赖（按需安装） |

## 注意事项

- PDF 转换会丢失原始排版，输出为纯文本 Markdown
- DOCX 会保留标题层级，但复杂格式（表格、图片）可能丢失
- 建议 chunk_size 设为 3000-5000，太大 Kiro 处理慢，太小上下文断裂
