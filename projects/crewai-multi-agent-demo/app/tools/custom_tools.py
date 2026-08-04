"""自定义工具 — 文件保存、字数统计、关键词密度分析"""

import re
import sys
from pathlib import Path

from crewai.tools import tool

# 将项目根目录加入 sys.path 以便导入 shared 模块
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from shared.watermark import embed_watermark

__author__ = "Walter Wang"

# 输出目录
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"

# 默认水印作者
_WATERMARK_AUTHOR = "Walter Wang"


@tool("save_article")
def save_article(filename: str, content: str) -> str:
    """将文章保存到 output/ 目录。

    Args:
        filename: 文件名（不含路径，如 'ai-agent-trends.md'）
        content: 文章内容（Markdown 格式）
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 确保文件名安全
    safe_name = re.sub(r"[^\w\-.]", "_", filename)
    if not safe_name.endswith(".md"):
        safe_name += ".md"

    # 嵌入隐形作者水印
    watermarked_content = embed_watermark(content, _WATERMARK_AUTHOR)

    filepath = OUTPUT_DIR / safe_name
    filepath.write_text(watermarked_content, encoding="utf-8")
    return f"文章已保存到: {filepath}"


@tool("word_count")
def word_count(text: str) -> str:
    """统计文本的字数（中文按字符计数，英文按单词计数）。

    Args:
        text: 要统计的文本内容
    """
    # 中文字符数
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    # 英文单词数
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    total = chinese_chars + english_words
    return f"总字数: {total}（中文字符: {chinese_chars}, 英文单词: {english_words}）"


@tool("keyword_density")
def keyword_density(text: str, keyword: str) -> str:
    """分析指定关键词在文本中的出现频率和密度。

    Args:
        text: 要分析的文本内容
        keyword: 目标关键词
    """
    # 统计关键词出现次数（不区分大小写）
    count = len(re.findall(re.escape(keyword), text, re.IGNORECASE))

    # 计算总字数
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    total_words = chinese_chars + english_words

    density = (count / total_words * 100) if total_words > 0 else 0

    return (
        f"关键词「{keyword}」分析结果:\n"
        f"  出现次数: {count}\n"
        f"  文本总字数: {total_words}\n"
        f"  关键词密度: {density:.2f}%\n"
        f"  建议: {'密度适中' if 1.0 <= density <= 3.0 else '建议调整到 1%-3% 之间'}"
    )
