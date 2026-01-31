from core.adapters.base import BaseAdapter, APIResponse
import httpx
import logging

logger = logging.getLogger("artfish.api.slack")

class SlackAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "slack"

    async def call(self, method: str, **kwargs) -> APIResponse:
        """
        支持 Slack Web API 调用示例。
        指针示例: "slack.chat.postMessage"
        """
        token = kwargs.pop("token", None) # 也可以从 settings 获取默认值
        if not token:
            return APIResponse(status="error", error="Slack token not provided.")
        
        # 将 "chat.postMessage" 转换为 Slack 的 API 路径
        url = f"https://slack.com/api/{method}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=kwargs, headers=headers)
                data = response.json()
                
                if data.get("ok"):
                    return APIResponse(status="success", data=data)
                else:
                    return APIResponse(status="error", error=data.get("error", "Unknown Slack error"))
                    
        except Exception as e:
            return self.format_error(e)
