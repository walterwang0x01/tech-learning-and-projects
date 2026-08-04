"""
健康检查接口
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "RAG LLM Agent Platform"
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查端点"""
    # 可以添加数据库连接检查等
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }

