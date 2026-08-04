"""应用配置管理"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，从环境变量或 .env 文件加载"""

__author__ = "Walter Wang"

    # LLM
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4o"

    # Serper（网络搜索）
    serper_api_key: str = ""

    # Mem0（长期记忆）
    mem0_api_key: str = ""

    # 服务
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
