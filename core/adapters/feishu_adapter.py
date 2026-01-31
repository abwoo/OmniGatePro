from core.adapters.base import BaseAdapter, APIResponse
from core.config import settings
import httpx
import logging

logger = logging.getLogger("artfish.api.feishu")

class FeishuAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "feishu"

    async def call(self, method: str, **kwargs) -> APIResponse:
        """
        支持飞书 (Lark) API 调用。
        指针示例: "feishu.send_text"
        """
        app_id = settings.FEISHU_APP_ID
        app_secret = settings.FEISHU_APP_SECRET
        
        if not app_id or not app_secret:
            return APIResponse(status="error", error="Feishu APP_ID or APP_SECRET not configured.")

        # 模拟飞书消息推送逻辑
        if method == "send_text":
            receive_id = kwargs.get("receive_id", "demo_user")
            content = kwargs.get("content", "")
            
            logger.info(f"Feishu pushing text to {receive_id}: {content[:20]}...")
            # 实际调用飞书 API 的逻辑会在这里 (获取 tenant_access_token -> 发送消息)
            return APIResponse(status="success", data=f"Feishu text sent to {receive_id}")

        return APIResponse(status="error", error=f"Method [{method}] not supported for Feishu adapter.")
