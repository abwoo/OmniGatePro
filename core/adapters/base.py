from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("artfish.api.adapter")

class APIResponse:
    """标准化 API 响应格式"""
    def __init__(self, status: str, data: Any = None, error: Optional[str] = None):
        self.status = status # 'success' or 'error'
        self.data = data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "error": self.error
        }

class BaseAdapter(ABC):
    """第三方 API 适配器基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """适配器名称，用于指针寻址 (如 'telegram')"""
        pass

    @abstractmethod
    async def call(self, method: str, **kwargs) -> APIResponse:
        """执行具体的 API 调用"""
        pass

    def format_error(self, e: Exception) -> APIResponse:
        """统一错误格式化"""
        logger.error(f"Adapter [{self.name}] error: {str(e)}")
        return APIResponse(status="error", error=str(e))
