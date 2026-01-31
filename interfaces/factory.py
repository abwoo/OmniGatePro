from typing import Dict, Any
from interfaces.backend import BackendAdapter
from backends.mock import MockBackend
import logging

logger = logging.getLogger("artfish.factory")

class BackendFactory:
    """
    后端工厂：根据用户配置动态创建后端适配器。
    """
    @staticmethod
    def create_backend(config: Dict[str, Any]) -> BackendAdapter:
        backend_type = config.get("type", "mock").lower()
        
        if backend_type == "mock":
            return MockBackend()
        
        # 未来可以支持真实后端
        # elif backend_type == "openai":
        #     return OpenAIBackend(api_key=config.get("api_key"))
            
        logger.warning(f"Unknown backend type: {backend_type}, falling back to mock")
        return MockBackend()
