"""
應用程式配置管理
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定"""
    
    # 應用程式基本設定
    app_name: str = "思考機器人"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # 資料庫配置
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "chatbot_db"
    db_user: str = "chatbot_user"
    db_password: str = "chatbot_password"
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "redis_password"
    redis_db: int = 0
    
    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    default_ai_model: str = "chatgpt"
    
    # LINE配置
    line_channel_access_token: Optional[str] = None
    line_channel_secret: Optional[str] = None
    
    # 會話配置
    session_timeout_minutes: int = 30
    max_conversation_history: int = 50
    
    # 服務配置
    web_host: str = "0.0.0.0"
    web_port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def database_url(self) -> str:
        """PostgreSQL資料庫連接URL"""
        # 優先使用DATABASE_URL環境變數
        database_url_env = os.getenv("DATABASE_URL")
        if database_url_env:
            return database_url_env
        # 否則使用個別配置
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def redis_url(self) -> str:
        """Redis連接URL"""
        # 優先使用REDIS_URL環境變數
        redis_url_env = os.getenv("REDIS_URL")
        if redis_url_env:
            return redis_url_env
        # 否則使用個別配置
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_development(self) -> bool:
        """是否為開發環境"""
        return self.debug
    
    @property
    def is_production(self) -> bool:
        """是否為生產環境"""
        return not self.debug


# 全域設定實例
settings = Settings()
