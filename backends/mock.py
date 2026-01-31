import time
import secrets
from typing import Any
from interfaces.backend import BackendAdapter, BackendResponse, BackendUsage
from core.plan import AtomicAction
from core.config import settings

class MockBackend(BackendAdapter):
    """
    MockBackend 是系统的参考实现。
    它用于在没有外部 API 密钥的环境下模拟高延迟的生成过程。
    """
    def execute(self, action: AtomicAction) -> BackendResponse:
        # 模拟模型处理延迟
        time.sleep(0.5)
        
        goal = action.params.get("goal", "unspecified")
        output = f"[Simulated Image Artifact] Concept: {goal} | Status: Rendered"
        
        # 商业化：模拟 Token 消耗和成本
        prompt_tokens = len(str(action.params)) // 4
        completion_tokens = len(output) // 4
        
        # 基础成本 + 随机波动
        cost = settings.DEFAULT_COST_PER_ACTION + (secrets.SystemRandom().random() * 0.005)
        
        usage = BackendUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=cost,
            model_name="artfish-mock-v1"
        )
        
        return BackendResponse(
            output=output,
            usage=usage,
            raw_response={"mock_id": "mock_123456"}
        )
