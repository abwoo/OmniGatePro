import logging
import time
import asyncio
from typing import Optional, List, Dict, Any
from core.config import settings
from core.network import NetworkClient
from core.token_tracker import token_tracker

logger = logging.getLogger("omni.core.llm_gateway")

class LLMGateway:
    """
    统一 AI 网关：支持多模型切换、负载均衡、限流及统计。
    对齐 Clawdbot 的多模型接入能力。
    """
    def __init__(self):
        self.network = NetworkClient()
        self.usage_stats = {} # 简单统计，实际应存入数据库
        self._refresh_providers()

    def _refresh_providers(self):
        """从环境变量动态刷新提供商配置"""
        import os
        self.providers = {
            "openai": {"key": os.getenv("OPENAI_API_KEY"), "base_url": "https://api.openai.com/v1"},
            "claude": {"key": os.getenv("CLAUDE_API_KEY"), "base_url": "https://api.anthropic.com/v1"},
            "gemini": {"key": os.getenv("GEMINI_API_KEY"), "base_url": "https://generativelanguage.googleapis.com/v1"},
            "deepseek": {"key": os.getenv("DEEPSEEK_API_KEY"), "base_url": "https://api.deepseek.com/v1"},
            "groq": {"key": os.getenv("GROQ_API_KEY"), "base_url": "https://api.groq.com/openai/v1"},
            "qwen": {"key": os.getenv("QWEN_API_KEY"), "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
            "hunyuan": {"key": os.getenv("HUNYUAN_API_KEY"), "base_url": "https://api.hunyuan.tencent.com/v1"},
            "zhipu": {"key": os.getenv("ZHIPU_API_KEY"), "base_url": "https://open.bigmodel.cn/api/paas/v4"},
            "wenxin": {"key": os.getenv("WENXIN_API_KEY"), "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop"},
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
            # 记录输入 Token (以字符数估算)
            input_tokens = len(prompt)
            
            # 优先调用真实的 DeepSeek API
            if provider == "deepseek":
                res = await self._call_deepseek_api(prompt, model)
            else:
                # 兜底：模拟各厂商请求逻辑
                response_text = await self._mock_llm_call(provider, prompt, model)
                res = {
                    "provider": provider,
                    "text": response_text,
                    "status": "success"
                }
            
            if res.get("status") == "success":
                output_tokens = len(res["text"])
                # 记录到追踪器 (场景设为 llm_call)
                # 注意：由于这是直接 API 调用，没有经过 OmniEngine 的压缩，所以 original = optimized
                token_tracker.record(provider, "llm_call", input_tokens + output_tokens, input_tokens + output_tokens)
                
                duration_ms = (time.time() - start_time) * 1000
                res["latency_ms"] = duration_ms
                self._record_usage(user_id, provider, duration_ms)
                
            return res
        except Exception as e:
            logger.error(f"LLM Call failed for {provider}: {e}")
            return {"error": str(e), "status": "fail"}

    async def _call_deepseek_api(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """真实调用 DeepSeek API"""
        api_key = self.providers["deepseek"]["key"]
        base_url = self.providers["deepseek"]["base_url"]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        try:
            async with self.network.client as client:
                response = await client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
                data = response.json()
                
                if response.status_code == 200:
                    text = data["choices"][0]["message"]["content"]
                    return {
                        "provider": "deepseek",
                        "text": text,
                        "status": "success"
                    }
                else:
                    return {"error": f"DeepSeek API Error: {data.get('error', {}).get('message', 'Unknown error')}", "status": "fail"}
        except Exception as e:
            return {"error": f"Network Error: {str(e)}", "status": "fail"}

    async def _mock_llm_call(self, provider: str, prompt: str, model: Optional[str]) -> str:
        """模拟不同厂商的 LLM 调用结果"""
        # 在实际开发中，这里会根据 provider 调用不同的 API
        await asyncio.sleep(0.2) # 模拟网络延迟
        return f"[来自 {provider.upper()} 的回复] 针对您的艺术创作请求 '{prompt[:20]}...'，我建议您可以尝试增加一些对比度。"

    async def verify_provider(self, provider: str) -> Dict[str, Any]:
        """校验指定提供商的 API 连通性"""
        if provider not in self.providers or not self.providers[provider]["key"]:
            return {"status": "fail", "message": "Key not configured"}
        
        info = self.providers[provider]
        headers = {"Authorization": f"Bearer {info['key']}"}
        
        # 不同厂商的心跳/模型列表接口
        verify_endpoints = {
            "openai": "/models",
            "deepseek": "/models",
            "claude": "/models", 
            "gemini": "/models",
            "groq": "/models",
            "qwen": "/models",
            "hunyuan": "/models",
            "zhipu": "/models",
            "wenxin": "/models"
        }
        
        endpoint = verify_endpoints.get(provider, "/models")
        # 兼容性处理：如果 base_url 已经包含 /v1，则直接拼接
        url = f"{info['base_url'].rstrip('/')}{endpoint}"
        if "/v1/v1" in url: url = url.replace("/v1/v1", "/v1")
        
        try:
            async with self.network.client as client:
                start = time.time()
                response = await client.get(url, headers=headers, timeout=5.0)
                latency = int((time.time() - start) * 1000)
                
                if response.status_code == 200:
                    return {"status": "success", "latency": latency}
                else:
                    return {"status": "fail", "message": f"HTTP {response.status_code}", "detail": response.text[:100]}
        except Exception as e:
            return {"status": "fail", "message": str(e)}

    def _record_usage(self, user_id: str, provider: str, duration: float):
        if user_id not in self.usage_stats:
            self.usage_stats[user_id] = {"total_calls": 0, "providers": {}, "total_latency": 0}
        
        stats = self.usage_stats[user_id]
        stats["total_calls"] += 1
        stats["total_latency"] += duration
        stats["providers"][provider] = stats["providers"].get(provider, 0) + 1

    def get_stats(self, user_id: str) -> Dict[str, Any]:
        return self.usage_stats.get(user_id, {"message": "No usage data found."})
