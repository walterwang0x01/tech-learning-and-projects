"""FastAPI 路由 — 内容创作 API"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.crews.content_crew import ContentCreationCrew

router = APIRouter(prefix="/api")


class ContentRequest(BaseModel):
    """内容创作请求"""

__author__ = "Walter Wang"

    topic: str = Field(..., description="创作主题", examples=["AI Agent 技术趋势"])
    process: str = Field(
        default="sequential",
        description="执行模式: sequential（顺序）或 hierarchical（层级）",
    )


class ContentResponse(BaseModel):
    """内容创作响应"""

    topic: str
    status: str
    article: str
    metadata: dict


@router.post("/create-content", response_model=ContentResponse)
async def create_content(req: ContentRequest):
    """创建技术博客内容

    启动多 Agent 协作流水线：研究 → 写作 → 编辑 → SEO 优化
    """
    crew = ContentCreationCrew(process=req.process)
    article = crew.kickoff(topic=req.topic)

    return ContentResponse(
        topic=req.topic,
        status="completed",
        article=article,
        metadata={
            "process": req.process,
            "agents": ["researcher", "writer", "editor", "seo_optimizer"],
        },
    )


@router.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "crewai-content-crew"}
