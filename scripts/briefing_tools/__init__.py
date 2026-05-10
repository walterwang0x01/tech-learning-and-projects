"""briefing_tools — 简报采集工具包 v3

架构：
  config    读取 .kiro/briefings/config.json
  schemas   数据类型定义 + validate
  http      HTTP 采集 + RSS/Atom 解析
  ingest    一次采集全部源 + 健康熔断
  classify  规则打标 + 评分（可选 LLM）
  dedup     URL / title / 语义去重
  candidates  按主题分流候选集，main-topic 归属
  storage   published-index / run 目录管理
  health    源健康记录
  retention run 目录清理
  notify    Bark 推送
  cli       CLI 入口
"""

from .config import load_config

__all__ = ["load_config"]
