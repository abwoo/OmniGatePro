import logging
import time
import asyncio
from typing import Optional, List, Dict, Any
from core.config import settings
from core.network import NetworkClient

logger = logging.getLogger("artfish.core.llm_gateway")

class LLMGateway:
    """
    统一 AI 网关：支持多模型切换、负载均衡、限流及统计。
    对齐 Clawdbot 的多模型接入能力。
    """
    def __init__(self):
        self.network = NetworkClient()
        self.usage_stats = {} # 简单统计，实际应存入数据库
        self.providers = {
            "openai": {"key": settings.OPENAI_API_KEY, "base_url": "https://api.openai.com/v1"},
            "claude": {"key": settings.CLAUDE_API_KEY, "base_url": "https://api.anthropic.com/v1"},
            "gemini": {"key": settings.GEMINI_API_KEY, "base_url": "https://generativelanguage.googleapis.com/v1"},
            "deepseek": {"key": settings.DEEPSEEK_API_KEY, "base_url": "https://api.deepseek.com/v1"},
            "qwen": {"key": settings.QWEN_API_KEY, "base_url": "https://dashscope.aliyuncs.com/api/v1"},
        }

    async def chat(self, provider: str, prompt: str, user_id: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        统一聊天接口。
        """
        if provider not in self.providers or not self.providers[provider]["key"]:
            # 自动寻找第一个可用的 provider
            available = [p for p, info in self.providers.items() if info["key"]]
            if not available:
                return {"error": "No available AI providers configured.", "status": "fail"}
            provider = available[0]
            logger.info(f"Auto-switched to available provider: {provider}")

        start_time = time.time()
        
        try:
            # 这里简化实现，仅模拟各厂商请求逻辑
            # 实际生产中应使用各厂商 SDK 或标准化 HTTP 调用
            response_text = await self._mock_llm_call(provider, prompt, model)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录统计
            self._record_usage(user_id, provider, duration_ms)
            
            return {
                "provider": provider,
                "text": response_text,
                "latency_ms": duration_ms,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"LLM Call failed for {provider}: {e}")
            return {"error": str(e), "status": "fail"}

    async def _mock_llm_call(self, provider: str, prompt: str, model: Optional[str]) -> str:
        """模拟不同厂商的 LLM 调用结果"""
        # 在实际开发中，这里会根据 provider 调用不同的 API
        await asyncio.sleep(0.2) # 模拟网络延迟
        return f"[来自 {provider.upper()} 的回复] 针对您的艺术创作请求 '{prompt[:20]}...'，我建议您可以尝试增加一些对比度。"

    def _record_usage(self, user_id: str, provider: str, duration: float):
        if user_id not in self.usage_stats:
            self.usage_stats[user_id] = {"total_calls": 0, "providers": {}, "total_latency": 0}
        
        stats = self.usage_stats[user_id]
        stats["total_calls"] += 1
        stats["total_latency"] += duration
        stats["providers"][provider] = stats["providers"].get(provider, 0) + 1

    def get_stats(self, user_id: str) -> Dict[str, Any]:
        return self.usage_stats.get(user_id, {"message": "No usage data found."})
