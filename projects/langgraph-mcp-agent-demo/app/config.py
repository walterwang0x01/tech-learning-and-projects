"""应用配置管理"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # 数据库
    database_url: str = "postgresql://postgres:postgres@localhost:5432/agent_demo"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # 可观测性
    langsmith_api_key: str = ""
    langsmith_project: str = "langgraph-mcp-demo"

    # Mem0
    mem0_api_key: str = ""

    # 服务
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
