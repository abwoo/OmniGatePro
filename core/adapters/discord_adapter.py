from core.adapters.base import BaseAdapter, APIResponse
import httpx
import logging

logger = logging.getLogger("artfish.api.discord")

class DiscordAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "discord"

    async def call(self, method: str, **kwargs) -> APIResponse:
        """
        支持 Discord Webhook 调用示例。
        指针示例: "discord.execute_webhook"
        """
        if method == "execute_webhook":
            webhook_url = kwargs.pop("webhook_url", None)
            if not webhook_url:
                return APIResponse(status="error", error="Missing webhook_url")
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(webhook_url, json=kwargs)
                    if response.status_code in [200, 204]:
                        return APIResponse(status="success", data="Message sent to Discord")
                    else:
                        return APIResponse(status="error", error=f"Discord error: {response.text}")
            except Exception as e:
                return self.format_error(e)
        
        return APIResponse(status="error", error=f"Method [{method}] not supported for Discord adapter.")
