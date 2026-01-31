from core.adapters.base import BaseAdapter, APIResponse
from core.config import settings
import httpx
import logging

logger = logging.getLogger("artfish.api.telegram")

class TelegramAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "telegram"

    async def call(self, method: str, **kwargs) -> APIResponse:
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            return APIResponse(status="error", error="Telegram token not configured.")
        
        url = f"https://api.telegram.org/bot{token}/{method}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=kwargs)
                data = response.json()
                
                if response.status_code == 200 and data.get("ok"):
                    return APIResponse(status="success", data=data.get("result"))
                else:
                    return APIResponse(status="error", error=data.get("description", "Unknown Telegram error"))
                    
        except Exception as e:
            return self.format_error(e)
