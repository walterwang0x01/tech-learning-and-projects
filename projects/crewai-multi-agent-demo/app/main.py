"""应用入口 — 支持 API 服务和 CLI 两种模式"""

import argparse
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

# FastAPI 应用
app = FastAPI(
    title="CrewAI Content Crew",
    description="基于 CrewAI 多 Agent 协作的技术博客内容创作流水线",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def run_cli(topic: str, process: str = "sequential") -> None:
    """CLI 模式：直接运行内容创作流水线"""

__author__ = "Walter Wang"
    from app.crews.content_crew import ContentCreationCrew

    print(f"\n{'='*60}")
    print(f"  CrewAI 内容创作流水线")
    print(f"  主题: {topic}")
    print(f"  模式: {process}")
    print(f"{'='*60}\n")

    crew = ContentCreationCrew(process=process)
    result = crew.kickoff(topic=topic)

    print(f"\n{'='*60}")
    print("  创作完成！")
    print(f"{'='*60}\n")
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrewAI 内容创作流水线")
    parser.add_argument("--topic", type=str, help="创作主题")
    parser.add_argument(
        "--process",
        type=str,
        default="sequential",
        choices=["sequential", "hierarchical"],
        help="执行模式 (默认: sequential)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="启动 API 服务模式",
    )

    args = parser.parse_args()

    if args.serve:
        # API 服务模式
        uvicorn.run(
            "app.main:app",
            host=settings.app_host,
            port=settings.app_port,
            reload=True,
        )
    elif args.topic:
        # CLI 模式
        run_cli(topic=args.topic, process=args.process)
    else:
        print("请指定 --topic 参数或使用 --serve 启动 API 服务")
        print("示例: python -m app.main --topic 'AI Agent 技术趋势'")
        sys.exit(1)
