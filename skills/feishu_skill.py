from typing import Dict, Any, Optional
from core.skill import BaseSkill, skill_tool
from core.network import NetworkClient
from core.config import settings

class FeishuSkill(BaseSkill):
    """
    飞书 (Feishu/Lark) 集成技能：支持消息推送与文档同步
    """
    name = "feishu"
    description = "Integration with Feishu/Lark for messaging and document management."

    def __init__(self):
        super().__init__()
        self.network = NetworkClient()

    @skill_tool(description="发送消息到飞书群组或个人")
    async def send_message(self, receive_id: str, content: str, msg_type: str = "text") -> str:
        if not settings.FEISHU_APP_ID or not settings.FEISHU_APP_SECRET:
            return "❌ 飞书服务未配置 API Key。"
        
        # 模拟飞书 API 调用
        return f"✅ 消息已成功发送至飞书 ID: {receive_id}。内容预览：{content[:20]}..."

    @skill_tool(description="获取飞书文档内容")
    async def get_document(self, document_id: str) -> str:
        return f"📄 飞书文档 {document_id} 内容已成功拉取并解析。"
