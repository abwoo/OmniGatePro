import logging
import asyncio
from typing import Dict, Any, Optional, Type
from core.adapters.base import BaseAdapter, APIResponse

logger = logging.getLogger("artfish.api.engine")

class APIEngine:
    """
    通用 API 调用引擎 (Clawdbot-style)
    支持基于指针 (Pointer) 的动态寻址与调用。
    """
    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        self._init_standard_adapters()

    def _init_standard_adapters(self):
        """初始化并注册标准适配器"""
        from core.adapters import TelegramAdapter, DiscordAdapter, SlackAdapter
        from core.adapters.feishu_adapter import FeishuAdapter
        from core.adapters.clawdbot_adapter import ClawdbotAdapter
        self.register_adapter(TelegramAdapter())
        self.register_adapter(DiscordAdapter())
        self.register_adapter(SlackAdapter())
        self.register_adapter(FeishuAdapter())
        self.register_adapter(ClawdbotAdapter())

    def register_adapter(self, adapter: BaseAdapter):
        """注册新的 API 适配器"""
        if adapter.name in self._adapters:
            logger.warning(f"Adapter [{adapter.name}] already registered. Overwriting.")
        self._adapters[adapter.name] = adapter
        logger.info(f"Adapter [{adapter.name}] registered successfully.")

    async def execute(self, pointer: str, **kwargs) -> APIResponse:
        """
        基于指针执行调用。
        指针格式: "adapter_name.method_name" (例如 "telegram.send_message")
        """
        try:
            if "." not in pointer:
                return APIResponse(status="error", error=f"Invalid pointer format: {pointer}. Expected 'adapter.method'")
            
            adapter_name, method_name = pointer.split(".", 1)
            
            adapter = self._adapters.get(adapter_name)
            if not adapter:
                return APIResponse(status="error", error=f"Adapter [{adapter_name}] not found.")
            
            logger.info(f"Executing API call: {pointer} with params {kwargs}")
            
            # 执行调用
            return await adapter.call(method_name, **kwargs)
            
        except Exception as e:
            logger.error(f"APIEngine execution error for pointer [{pointer}]: {str(e)}")
            return APIResponse(status="error", error=f"Internal Engine Error: {str(e)}")

# 全局单例
api_engine = APIEngine()
