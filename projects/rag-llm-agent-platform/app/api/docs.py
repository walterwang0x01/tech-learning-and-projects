"""
API 文档配置（FastAPI 自动生成 OpenAPI 文档）
"""
from fastapi.openapi.utils import get_openapi
from app.main import app


def custom_openapi():
    """自定义 OpenAPI 文档"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="RAG LLM Agent Platform API",
        version="1.0.0",
        description="""
        ## RAG + LLM Agent 平台 API 文档
        
        基于 RAG（检索增强生成）和 Function Calling 的企业级 AI Agent 平台。
        
        ### 核心功能
        - **RAG 检索增强生成**：基于向量数据库的语义检索
        - **Function Calling**：支持 10+ 业务工具调用
        - **流式交互**：WebSocket 实时流式输出
        
        ### 认证
        当前版本无需认证，生产环境请添加 API Key 认证。
        """,
        routes=app.routes,
        contact={
            "name": "王蕴",
            "email": "walterhandsome@163.com"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        }
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

