"""全局配置，从 .env 文件读取环境变量"""
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv(Path(__file__).parent / ".env")


class Settings(BaseSettings):
    # LLM 配置
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "qwen-plus"

    # Embedding 配置
    embedding_api_key: str = ""
    embedding_api_base: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-v2"

    # Milvus 配置
    milvus_host: str = "localhost"
    milvus_port: Optional[int] = 19530
    milvus_user: str = ""
    milvus_password: str = ""
    milvus_collection: str = "rag_documents"

    # 文本分割
    chunk_size: Optional[int] = 500
    chunk_overlap: Optional[int] = 50

    # MySQL 配置
    mysql_url: str = "mysql+pymysql://user:password@host:3306/dbname"

    # JWT 配置
    jwt_secret: str = "change-this-to-a-random-secret"
    jwt_expire_minutes: Optional[int] = 1440

    model_config = {"case_sensitive": False}

    @field_validator("milvus_port", "chunk_size", "chunk_overlap", "jwt_expire_minutes", mode="before")
    @classmethod
    def empty_str_to_default(cls, v):
        if v == "" or v is None:
            return None  # pydantic 会使用字段默认值
        return v


settings = Settings()
