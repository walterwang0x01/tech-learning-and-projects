#!/usr/bin/env bash
# 同步全局 steering 到锚点 workspace 的 .kiro/steering/
# Kiro 不跟随软链接，必须复制为真实文件才能被自动加载
# 锚点策略：multi-root workspace 通常会包含 tech-learning-and-projects，
# 所以只在这一个 workspace 维护副本，避免重复加载浪费 token
# 用法：~/.kiro/steering/sync.sh

set -euo pipefail

SOURCE_DIR="$HOME/.kiro/steering"
ANCHOR_WORKSPACE="$HOME/PycharmProjects/tech-learning-and-projects"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 源目录不存在：$SOURCE_DIR"
    exit 1
fi

if [ ! -d "$ANCHOR_WORKSPACE" ]; then
    echo "❌ 锚点 workspace 不存在：$ANCHOR_WORKSPACE"
    exit 1
fi

# 收集源目录下所有 .md 文件名（排除 README）
files=()
while IFS= read -r f; do
    files+=("$(basename "$f")")
done < <(find -L "$SOURCE_DIR" -maxdepth 1 -name "*.md" -type f -not -name "README.md")

if [ ${#files[@]} -eq 0 ]; then
    echo "❌ $SOURCE_DIR 下没有可同步的 .md 文件"
    exit 1
fi

target_dir="$ANCHOR_WORKSPACE/.kiro/steering"
mkdir -p "$target_dir"

echo "源目录：$SOURCE_DIR"
echo "锚点：$target_dir"
echo "同步文件 (${#files[@]} 个)："
for f in "${files[@]}"; do
    cp "$SOURCE_DIR/$f" "$target_dir/$f"
    echo "  ✅ $f"
done

echo
echo "完成。重启 Kiro 或重新加载 workspace 让新规则生效。"
