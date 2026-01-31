from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Basic Config
    APP_NAME: str = "artfish-studio"
    DEBUG: bool = True
    VERSION: str = "2.0.0"
    
    # Database Config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./artfish_studio.db")
    
    # Telegram Config
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # External APIs
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    EXCHANGERATE_API_KEY: Optional[str] = os.getenv("EXCHANGERATE_API_KEY")
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    WENXIN_API_KEY: Optional[str] = os.getenv("WENXIN_API_KEY")
    QWEN_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY")
    
    # Feishu (Lark) Config
    FEISHU_APP_ID: Optional[str] = os.getenv("FEISHU_APP_ID")
    FEISHU_APP_SECRET: Optional[str] = os.getenv("FEISHU_APP_SECRET")

    # Other API Configs
    DISCORD_WEBHOOK_URL: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    SLACK_BOT_TOKEN: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    
    # Execution Config
    # Set to True to run tasks synchronously without Redis (Recommended for local dev)
    FORCE_SYNC_EXECUTION: bool = True 
    
    # Async Queue Config (Only used if FORCE_SYNC_EXECUTION is False)
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
