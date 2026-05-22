"""
翻译结果合并工具 - 将分块翻译的文件合并为完整文档。

用法：
    python merge_translated.py ./chunks-dir/
    python merge_translated.py ./chunks-dir/ --output translated-full.md
"""

import argparse
import re
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="合并翻译后的分块文件")
    parser.add_argument("input_dir", help="包含翻译后文件的目录")
    parser.add_argument("--output", default=None, help="输出文件路径（默认为目录名-translated.md）")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"错误：目录不存在 - {input_dir}")
        sys.exit(1)

    # 找到所有 .md 文件（排除清单文件），按文件名排序
    md_files = sorted([
        f for f in input_dir.glob("*.md")
        if not f.name.startswith("00-") and not f.name.endswith("-translated.md")
    ])

    # 优先使用 *-zh.md 或 *-translated.md 版本
    final_files = []
    for f in md_files:
        zh_version = f.with_stem(f.stem + "-zh")
        translated_version = f.with_stem(f.stem + "-translated")
        if zh_version.exists():
            final_files.append(zh_version)
        elif translated_version.exists():
            final_files.append(translated_version)
        else:
            final_files.append(f)

    if not final_files:
        print(f"错误：目录中没有找到 .md 文件 - {input_dir}")
        sys.exit(1)

    # 合并
    merged_content = ""
    for f in final_files:
        content = f.read_text(encoding="utf-8")
        merged_content += content + "\n\n---\n\n"

    # 移除末尾多余的分隔符
    merged_content = merged_content.rstrip("\n-\n ")

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        dir_name = input_dir.name.replace("-chunks", "")
        output_path = input_dir.parent / f"{dir_name}-translated.md"

    output_path.write_text(merged_content, encoding="utf-8")

    print(f"✅ 合并完成！")
    print(f"   文件数：{len(final_files)}")
    print(f"   总字符：{len(merged_content)}")
    print(f"   输出到：{output_path}")


if __name__ == "__main__":
    main()
