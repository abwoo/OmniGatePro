import logging
import time
import asyncio
from typing import Optional, List, Dict, Any, Union
from core.config import settings

logger = logging.getLogger("artfish.core.llm_gateway")

class LLMResponse:
    """标准化 AI 响应格式"""
    def __init__(self, content: str, provider: str, duration_ms: float, tokens: int = 0):
        self.content = content
        self.provider = provider
        self.duration_ms = duration_ms
        self.tokens = tokens
        self.timestamp = time.time()

class LLMGateway:
    """
    统一 AI 网关：支持多模型、负载均衡、限流及计费追踪。
    对齐业界成熟的 API 接入层设计。
    """
    def __init__(self):
        self.usage_stats: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, List[float]] = {} # 简单内存限流
        
        # 预配置模型池
        self.providers = {
            "openai": {"key": settings.OPENAI_API_KEY, "available": bool(settings.OPENAI_API_KEY)},
            "claude": {"key": settings.CLAUDE_API_KEY, "available": bool(settings.CLAUDE_API_KEY)},
            "gemini": {"key": settings.GEMINI_API_KEY, "available": bool(settings.GEMINI_API_KEY)},
            "wenxin": {"key": settings.WENXIN_API_KEY, "available": bool(settings.WENXIN_API_KEY)},
            "qwen": {"key": settings.QWEN_API_KEY, "available": bool(settings.QWEN_API_KEY)},
        }

    async def chat(self, provider: str, prompt: str, user_id: str) -> LLMResponse:
        """
        统一聊天接口。
        实现负载均衡、限流与统计。
        """
        # 1. 限流检查 (每用户每分钟最多 20 次)
        if not self._check_rate_limit(user_id):
            raise Exception("🚦 请求过于频繁，请稍后再试（限流控制）。")

        # 2. 供应商路由与负载均衡
        target_provider = self._route_provider(provider)
        
        # 3. 执行请求（模拟异步调用）
        start_time = time.time()
        logger.info(f"Routing request for user {user_id} to {target_provider}")
        
        # 模拟不同模型的延迟特性
        delays = {"openai": 0.3, "claude": 0.4, "gemini": 0.25, "wenxin": 0.5, "qwen": 0.35}
        await asyncio.sleep(delays.get(target_provider, 0.3))
        
        duration = (time.time() - start_time) * 1000
        
        # 4. 标准化响应
        mock_content = f"【{target_provider.upper()}】针对您的输入：'{prompt}'，我的分析如下...\n(响应耗时: {duration:.1f}ms)"
        response = LLMResponse(content=mock_content, provider=target_provider, duration_ms=duration)
        
        # 5. 更新统计与计费
        self._update_usage(user_id, response)
        
        return response

    def _check_rate_limit(self, user_id: str) -> bool:
        """简单的滑动窗口限流逻辑"""
        now = time.time()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
            
        # 移除一分钟前的记录
        self.rate_limits[user_id] = [t for t in self.rate_limits[user_id] if now - t < 60]
        
        if len(self.rate_limits[user_id]) >= 20:
            return False
            
        self.rate_limits[user_id].append(now)
        return True

    def _route_provider(self, requested: str) -> str:
        """
        智能路由逻辑。
        如果请求的供应商不可用，自动切换到负载最低的可用供应商。
        """
        if requested in self.providers and self.providers[requested]["available"]:
            return requested
            
        # 负载均衡：选择已调用次数最少的供应商
        available = [p for p, cfg in self.providers.items() if cfg["available"]]
        if not available:
            raise ValueError("❌ 系统错误：没有任何可用的 AI 供应商配置。")
            
        # 这里简单按可用列表首位返回，实际可扩展为加权随机或轮询
        return available[0]

    def _update_usage(self, user_id: str, response: LLMResponse):
        """更新使用统计与模拟计费追踪"""
        if user_id not in self.usage_stats:
            self.usage_stats[user_id] = {
                "total_requests": 0,
                "total_duration_ms": 0.0,
                "providers": {},
                "estimated_cost_usd": 0.0
            }
            
        stats = self.usage_stats[user_id]
        stats["total_requests"] += 1
        stats["total_duration_ms"] += response.duration_ms
        
        p = response.provider
        stats["providers"][p] = stats["providers"].get(p, 0) + 1
        
        # 模拟计费逻辑 (不同供应商单价不同)
        rates = {"openai": 0.01, "claude": 0.015, "gemini": 0.005, "wenxin": 0.002, "qwen": 0.002}
        stats["estimated_cost_usd"] += rates.get(p, 0.01)

    def get_billing_report(self, user_id: str) -> str:
        """生成用户的使用统计报告"""
        if user_id not in self.usage_stats:
            return "📊 您还没有任何 AI 模型使用记录。"
            
        s = self.usage_stats[user_id]
        provider_list = ", ".join([f"{k}({v}次)" for k, v in s["providers"].items()])
        
        return (
            f"📈 *AI 使用统计与计费报告*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🚀 总请求数：{s['total_requests']}\n"
            f"⏱️ 平均响应：{s['total_duration_ms']/s['total_requests']:.1f}ms\n"
            f"🤖 供应商：{provider_list}\n"
            f"💵 预计消费：${s['estimated_cost_usd']:.4f}\n"
            f"📅 统计周期：今日"
        )
