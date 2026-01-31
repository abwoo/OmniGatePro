import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from core.llm_gateway import LLMGateway

logger = logging.getLogger("omni.core.agent")

class OmniAgent:
    """
    轻量化全能智能体：核心逻辑仅保留推理与记忆。
    """
    def __init__(self, name: str, role: str):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.memory: List[Dict] = []
        self.llm = LLMGateway()

    async def think(self, user_input: str) -> Dict[str, Any]:
        # 极致压缩：仅传递关键上下文
        context_summary = self._get_fast_summary()
        
        system_prompt = (
            f"You are {self.name}, a professional assistant for Clawdbot. "
            "Your goal is to provide concise, expert-level support. "
            "NEVER mention you are an AI or LLM. NEVER use polite filler like 'Certainly' or 'I understand'. "
            "Use Markdown formatting. Focus on the local device context."
        )
        
        prompt = f"{system_prompt}\n\nUser: {user_input}\nContext: {context_summary}"
        res = await self.llm.chat("deepseek", prompt, "system")
        
        # 清理 AI 痕迹
        if res.get("status") == "success":
            from core.persona import persona_engine
            res["text"] = persona_engine._clean_ai_traces(res["text"])
            
        return res

    def _get_fast_summary(self) -> str:
        if not self.memory: return "None"
        return self.memory[-1].get("content", "")[:100]

    def add_memory(self, role: str, content: str):
        self.memory.append({"role": role, "content": content})
        if len(self.memory) > 5: self.memory.pop(0) # 内存中仅保留 5 条
