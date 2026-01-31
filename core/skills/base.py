from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("omni.skills.base")

class BaseSkill(ABC):
    """
    OmniGate 技能基类
    """
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        执行具体动作
        """
        pass

    def format_result(self, status: str, data: Any = None, error: Optional[str] = None) -> Dict[str, Any]:
        return {
            "skill": self.name,
            "status": status,
            "data": data,
            "error": error
        }
