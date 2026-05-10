#!/usr/bin/env python3
"""简报工具集 v3 — CLI 入口（薄壳）

实际实现见 `scripts/briefing_tools/`。本文件仅转发到 package 主函数。

子命令概览:
  ingest / classify / candidates / run-all   — 主流水线
  register / rebuild-index                   — 已发布索引管理
  validate                                   — 简报 md 事务性校验
  cleanup                                    — run 目录清理
  health / health-reset                      — 源健康与熔断
  status / index / notify                    — 通用工具
  collect / dedup                            — v1 兼容命令
  show-rules                                 — 输出 briefing-rules.md
"""

import sys
from pathlib import Path

# 把 scripts/ 加入 path，方便 package 导入
sys.path.insert(0, str(Path(__file__).resolve().parent))

from briefing_tools.cli import main

if __name__ == "__main__":
    main()
