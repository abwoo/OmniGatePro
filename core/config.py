from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # 基础配置
    APP_NAME: str = "artfish-runtime"
    DEBUG: bool = False
    VERSION: str = "0.1.0"
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./artfish.db")
    
    # 商业化计费配置 (默认费率)
    DEFAULT_COST_PER_ACTION: float = 0.01
    CURRENCY: str = "USD"
    
    # 异步任务配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "artfish-super-secret-key-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Stripe 配置
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # 支付宝配置
    ALIPAY_APP_ID: str = os.getenv("ALIPAY_APP_ID", "")
    ALIPAY_DEBUG: bool = os.getenv("ALIPAY_DEBUG", "True").lower() == "true"
    # 密钥内容或路径
    ALIPAY_PRIVATE_KEY: str = os.getenv("ALIPAY_PRIVATE_KEY", "")
    ALIPAY_PUBLIC_KEY: str = os.getenv("ALIPAY_PUBLIC_KEY", "")
    
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # 管理员配置 (建议通过环境变量设置)
    SUPER_ADMIN_EMAIL: str = os.getenv("SUPER_ADMIN_EMAIL", "admin@artfish.ai")
    
    # 存储配置
    EXPORT_DIR: str = "exports"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True
    )

# 创建全局配置实例
settings = Settings()

# 确保导出目录存在
if not os.path.exists(settings.EXPORT_DIR):
    os.makedirs(settings.EXPORT_DIR)
