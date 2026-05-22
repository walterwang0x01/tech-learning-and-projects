"""
文档切分工具 - 将大文档按章节/页数切分为多个小文件，方便 Kiro 分批翻译。

支持格式：
- Markdown (.md)
- 纯文本 (.txt)
- PDF (.pdf) — 需要安装 marker-pdf 或 pymupdf
- DOCX (.docx) — 需要安装 python-docx

用法：
    python split_doc.py input.md --chunk-size 3000 --output-dir ./chunks
    python split_doc.py input.pdf --chunk-size 3000 --output-dir ./chunks
    python split_doc.py input.docx --chunk-size 3000 --output-dir ./chunks
"""

import argparse
import os
import re
import sys
from pathlib import Path


def split_markdown(content: str, chunk_size: int) -> list[dict]:
    """按标题层级切分 Markdown，保证每块不超过 chunk_size 字符。"""
    # 按一级/二级标题切分
    sections = re.split(r'(^#{1,2}\s+.+$)', content, flags=re.MULTILINE)

    chunks = []
    current_chunk = ""
    current_title = "part"

    for i, section in enumerate(sections):
        # 检测是否是标题行
        if re.match(r'^#{1,2}\s+', section):
            # 如果当前块已经有内容且加上新 section 会超限，先保存
            if current_chunk.strip():
                chunks.append({"title": current_title, "content": current_chunk.strip()})
                current_chunk = ""
            current_title = re.sub(r'^#{1,2}\s+', '', section).strip()
            current_chunk = section + "\n"
        else:
            # 如果当前块加上这段会超过 chunk_size，需要进一步切分
            if len(current_chunk) + len(section) > chunk_size and current_chunk.strip():
                chunks.append({"title": current_title, "content": current_chunk.strip()})
                current_chunk = ""
                # 对超长段落按段落切分
                paragraphs = section.split('\n\n')
                for para in paragraphs:
                    if len(current_chunk) + len(para) > chunk_size and current_chunk.strip():
                        chunks.append({"title": current_title, "content": current_chunk.strip()})
                        current_chunk = ""
                    current_chunk += para + "\n\n"
            else:
                current_chunk += section

    # 保存最后一块
    if current_chunk.strip():
        chunks.append({"title": current_title, "content": current_chunk.strip()})

    return chunks


def split_plain_text(content: str, chunk_size: int) -> list[dict]:
    """按段落切分纯文本。"""
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = ""
    chunk_index = 1

    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk.strip():
            chunks.append({"title": f"part-{chunk_index}", "content": current_chunk.strip()})
            current_chunk = ""
            chunk_index += 1
        current_chunk += para + "\n\n"

    if current_chunk.strip():
        chunks.append({"title": f"part-{chunk_index}", "content": current_chunk.strip()})

    return chunks


def extract_pdf_to_markdown(pdf_path: str) -> str:
    """将 PDF 转为 Markdown 文本。"""
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            print("错误：需要安装 pymupdf 来处理 PDF 文件")
            print("运行：pip install pymupdf")
            sys.exit(1)

    doc = pymupdf.open(pdf_path)
    full_text = ""
    for page_num, page in enumerate(doc, 1):
        text = page.get_text("text")
        if text.strip():
            full_text += f"\n\n## Page {page_num}\n\n{text}"
    doc.close()
    return full_text


def extract_docx_to_markdown(docx_path: str) -> str:
    """将 DOCX 转为 Markdown 文本。"""
    try:
        from docx import Document
    except ImportError:
        print("错误：需要安装 python-docx 来处理 DOCX 文件")
        print("运行：pip install python-docx")
        sys.exit(1)

    doc = Document(docx_path)
    full_text = ""

    for para in doc.paragraphs:
        if not para.text.strip():
            full_text += "\n"
            continue

        # 根据样式判断标题级别
        style_name = para.style.name.lower() if para.style else ""
        if "heading 1" in style_name:
            full_text += f"\n# {para.text}\n\n"
        elif "heading 2" in style_name:
            full_text += f"\n## {para.text}\n\n"
        elif "heading 3" in style_name:
            full_text += f"\n### {para.text}\n\n"
        else:
            full_text += f"{para.text}\n\n"

    return full_text


def sanitize_filename(name: str) -> str:
    """清理文件名，移除不安全字符。"""
    name = re.sub(r'[^\w\s\-]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    return name[:50] if name else "untitled"


def main():
    parser = argparse.ArgumentParser(description="文档切分工具 - 将大文档切分为多个小文件")
    parser.add_argument("input", help="输入文件路径")
    parser.add_argument("--chunk-size", type=int, default=3000,
                        help="每块最大字符数（默认 3000）")
    parser.add_argument("--output-dir", default=None,
                        help="输出目录（默认为 input 同目录下的 chunks/ 子目录）")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件不存在 - {input_path}")
        sys.exit(1)

    # 确定输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = input_path.parent / f"{input_path.stem}-chunks"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 根据文件类型提取文本
    suffix = input_path.suffix.lower()
    if suffix == ".md":
        content = input_path.read_text(encoding="utf-8")
    elif suffix == ".txt":
        content = input_path.read_text(encoding="utf-8")
    elif suffix == ".pdf":
        print("正在解析 PDF...")
        content = extract_pdf_to_markdown(str(input_path))
    elif suffix == ".docx":
        print("正在解析 DOCX...")
        content = extract_docx_to_markdown(str(input_path))
    else:
        print(f"错误：不支持的文件格式 - {suffix}")
        print("支持的格式：.md, .txt, .pdf, .docx")
        sys.exit(1)

    # 切分
    if suffix == ".md":
        chunks = split_markdown(content, args.chunk_size)
    else:
        chunks = split_plain_text(content, args.chunk_size)

    # 写入文件
    print(f"\n文档已切分为 {len(chunks)} 个部分：\n")
    manifest_lines = []

    for i, chunk in enumerate(chunks, 1):
        filename = f"{i:02d}-{sanitize_filename(chunk['title'])}.md"
        filepath = output_dir / filename
        filepath.write_text(chunk["content"], encoding="utf-8")
        char_count = len(chunk["content"])
        print(f"  [{i:02d}] {filename} ({char_count} 字符)")
        manifest_lines.append(f"- [ ] `{filename}` ({char_count} 字符)")

    # 生成翻译清单
    manifest_path = output_dir / "00-翻译清单.md"
    manifest_content = f"""# 翻译清单

源文件：`{input_path.name}`
切分块数：{len(chunks)}
每块上限：{args.chunk_size} 字符

## 翻译进度

{chr(10).join(manifest_lines)}

## 使用方法

1. 在 Kiro 中打开每个文件
2. 对 Kiro 说："请将这个文件翻译成中文，保持 Markdown 格式，技术术语保留英文原文并在括号中注明"
3. 翻译完成后在上方清单中打勾
4. 全部完成后运行合并脚本：
   ```
   python scripts/doc-translator/merge_translated.py {output_dir}/
   ```
"""
    manifest_path.write_text(manifest_content, encoding="utf-8")

    print(f"\n✅ 切分完成！文件保存在：{output_dir}/")
    print(f"📋 翻译清单：{manifest_path}")
    print(f"\n下一步：打开 {output_dir}/ 中的文件，逐个让 Kiro 翻译")


if __name__ == "__main__":
    main()
