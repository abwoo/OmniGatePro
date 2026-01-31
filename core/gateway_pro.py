import time
import logging
from typing import Dict, Any, List
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.api_engine import api_engine
from core.agent import orchestrator

logger = logging.getLogger("artfish.pro.gateway")

# API 限流器
limiter = Limiter(key_func=get_remote_address)

class ProGateway:
    """
    增强版 API 网关：包含限流、熔断与实时监控统计。
    """
    def __init__(self):
        self.stats = {
            "total_requests": 0,
            "errors": 0,
            "latency_history": [],
            "agent_usage": {}
        }
        self.circuit_breaker_status = "closed" # closed, open, half-open

    async def handle_request(self, user_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        统一请求处理入口。
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # 1. 熔断检查
            if self.circuit_breaker_status == "open":
                return {"error": "System is currently in maintenance (Circuit Breaker Open)"}

            # 2. 路由分发 (Agent 协作)
            if "debate" in command:
                result = await orchestrator.run_debate(params["topic"], "tutor", "critic")
            else:
                # 默认并行处理
                result = await orchestrator.run_parallel(command, ["tutor", "artist", "critic"])

            # 3. 监控记录
            latency = (time.time() - start_time) * 1000
            self.stats["latency_history"].append(latency)
            
            return {
                "status": "success",
                "data": result,
                "latency_ms": f"{latency:.2f}ms"
            }

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Gateway Error: {e}")
            # 简单熔断逻辑
            if self.stats["errors"] > 50:
                self.circuit_breaker_status = "open"
            return {"status": "error", "message": str(e)}

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取实时监控仪表盘数据"""
        avg_latency = sum(self.stats["latency_history"][-100:]) / max(len(self.stats["latency_history"][-100:]), 1)
        error_rate = (self.stats["errors"] / max(self.stats["total_requests"], 1)) * 100
        
        return {
            "requests_per_minute": self.stats["total_requests"],
            "avg_latency_ms": f"{avg_latency:.2f}",
            "error_rate": f"{error_rate:.2f}%",
            "circuit_breaker": self.circuit_breaker_status,
            "active_agents": list(orchestrator.agents.keys())
        }

# 实例
pro_gateway = ProGateway()
