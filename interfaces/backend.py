from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class BackendUsage(BaseModel):
    """
    记录单次调用的资源消耗。
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    model_name: str = "unknown"

class BackendResponse(BaseModel):
    """
    后端的标准响应格式，包含结果和消耗统计。
    """
    output: Any
    usage: BackendUsage
    raw_response: Optional[Dict[str, Any]] = None

class BackendAdapter(ABC):
    """
    BackendAdapter 是所有后端实现的抽象基类。
    它定义了标准的执行契约，确保核心引擎与具体的 AI 模型实现完全解耦。
    """
    @abstractmethod
    def execute(self, action: Any) -> BackendResponse:
        """
        执行给定的原子动作并返回标准化的 BackendResponse。
        """
        pass
