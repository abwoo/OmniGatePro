from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, Union
import os

class Settings(BaseSettings):
    # Basic Config
    ENV: str = "prod"
    DEBUG: bool = False
    APP_NAME: str = "OmniGate Pro"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "3.0.0"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Union[str, bool]) -> bool:
        """增强 DEBUG 校验：支持 *、1、true 等字符串"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            v = v.lower()
            if v in ("*", "true", "1", "yes", "on"):
                return True
        return False
    
    # Database Config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./omnigate_pro.db")
    
    # Platform Tokens (Social)
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_OWNER_ID: Optional[str] = os.getenv("TELEGRAM_OWNER_ID")
    DISCORD_BOT_TOKEN: Optional[str] = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    SLACK_BOT_TOKEN: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    FEISHU_APP_ID: Optional[str] = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET: Optional[str] = os.getenv("FEISHU_APP_SECRET")
    DINGTALK_WEBHOOK: Optional[str] = os.getenv("DINGTALK_WEBHOOK")
    
    # LLM API Keys (Global & Mainstream)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY") # GPT-4, etc.
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY") # Claude 3.5
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") # Gemini 1.5
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY") # DeepSeek V3/R1
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")     # Llama 3 (Fast)
    
    # LLM API Keys (Chinese Mainstream)
    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY")     # 通义千问 (DashScope)
    HUNYUAN_API_KEY: Optional[str] = os.getenv("HUNYUAN_API_KEY") # 腾讯混元
    WENXIN_API_KEY: Optional[str] = os.getenv("WENXIN_API_KEY") # 百度文心一言
    ZHIPU_API_KEY: Optional[str] = os.getenv("ZHIPU_API_KEY")   # 智谱清言 (GLM)
    
    # Execution Config
    FORCE_SYNC_EXECUTION: bool = True 
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage Config
    EXPORT_DIR: str = "exports"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )

# Create global settings instance
settings = Settings()

# Ensure export directory exists
if not os.path.exists(settings.EXPORT_DIR):
    os.makedirs(settings.EXPORT_DIR)
