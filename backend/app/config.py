"""配置管理模块"""

import os
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load only the project-local .env file.
# Do not implicitly read a sibling HelloAgents framework .env because that
# creates hidden machine-specific coupling and breaks repository portability.
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    # 应用基本配置
    app_name: str = "HelloAgents智能旅行助手"
    app_version: str = "1.0.0"
    debug: bool = False

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS 配置
    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:3000"
    )

    # 高德地图 API 配置
    amap_api_key: str = ""

    # Unsplash API 配置
    unsplash_access_key: str = ""
    unsplash_secret_key: str = ""

    # LLM 配置（由 HelloAgentsLLM 从环境变量读取）
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def get_cors_origins_list(self) -> List[str]:
        """获取 CORS origins 列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def validate_config() -> bool:
    """验证配置是否完整"""
    errors = []
    warnings = []

    if not settings.amap_api_key:
        errors.append("AMAP_API_KEY 未配置")

    # HelloAgentsLLM 会自动从 LLM_API_KEY 读取，不强制要求 OPENAI_API_KEY
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        warnings.append("LLM_API_KEY 或 OPENAI_API_KEY 未配置，LLM 功能可能无法使用")

    if errors:
        error_msg = "配置错误:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    if warnings:
        print("\n⚠️  配置警告:")
        for warning in warnings:
            print(f"  - {warning}")

    return True


def print_config() -> None:
    """打印当前配置（隐藏敏感信息）"""
    print(f"应用名称: {settings.app_name}")
    print(f"版本: {settings.app_version}")
    print(f"服务地址: {settings.host}:{settings.port}")
    print(f"高德地图 API Key: {'已配置' if settings.amap_api_key else '未配置'}")

    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL") or settings.openai_base_url
    llm_model = os.getenv("LLM_MODEL_ID") or settings.openai_model

    print(f"LLM API Key: {'已配置' if llm_api_key else '未配置'}")
    print(f"LLM Base URL: {llm_base_url}")
    print(f"LLM Model: {llm_model}")
    print(f"日志级别: {settings.log_level}")
