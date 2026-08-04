"""文件操作 MCP Server / LangChain 工具"""

import sys
from pathlib import Path

from langchain_core.tools import tool

# 将项目根目录加入 sys.path 以便导入 shared 模块
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from shared.watermark import extract_watermark

__author__ = "Walter Wang"

DOCS_DIR = Path(__file__).parent.parent.parent / "docs" / "sample_docs"


@tool
def list_files(directory: str = "") -> str:
    """列出文档目录中的文件。"""
    target = DOCS_DIR / directory if directory else DOCS_DIR
    if not target.exists():
        return f"目录不存在: {directory}"
    files = []
    for f in sorted(target.iterdir()):
        prefix = "📁" if f.is_dir() else "📄"
        files.append(f"{prefix} {f.name}")
    return "\n".join(files) if files else "目录为空"


@tool
def read_file(filename: str) -> str:
    """读取文档目录中的文件内容。"""
    filepath = DOCS_DIR / filename
    if not filepath.exists():
        return f"文件不存在: {filename}"
    if not filepath.is_relative_to(DOCS_DIR):
        return "不允许访问文档目录之外的文件"
    content = filepath.read_text(encoding="utf-8")
    if len(content) > 3000:
        content = content[:3000] + "\n...(内容已截断)"
    return content


@tool
def check_watermark(filename: str) -> str:
    """检测文档中是否包含隐形作者水印，并提取作者信息。"""
    filepath = DOCS_DIR / filename
    if not filepath.exists():
        return f"文件不存在: {filename}"
    content = filepath.read_text(encoding="utf-8")
    author = extract_watermark(content)
    if author:
        return f"✅ 检测到隐形水印 — 原始作者: {author}"
    return "❌ 未检测到隐形水印"


def get_file_tools():
    """获取文件工具列表"""
    return [list_files, read_file, check_watermark]
