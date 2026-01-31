from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Basic Config
    APP_NAME: str = "edusense-gateway"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # Database Config
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./edusense.db")
    
    # Telegram Config
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    
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
