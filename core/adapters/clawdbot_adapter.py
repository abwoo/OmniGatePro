from core.adapters.base import BaseAdapter, APIResponse
from core.omni_engine import omni_orchestrator
import logging

logger = logging.getLogger("omni.adapters.clawdbot")

class ClawdbotAdapter(BaseAdapter):
    """
    Clawdbot 插件适配器：将 OmniGate 的能力暴露给 Clawdbot。
    支持任务卸载与 Token 优化服务。
    """
    @property
    def name(self) -> str:
        return "clawdbot"

    async def call(self, method: str, **kwargs) -> APIResponse:
        """
        Clawdbot 调用接口。
        """
        if method == "offload_task":
            # 任务卸载：Clawdbot 将本地执行任务转交给 OmniGate
            task_desc = kwargs.get("task")
            res = await omni_orchestrator.dispatch(task_desc)
            return APIResponse(status="success", data=res)
        
        elif method == "optimize_token":
            # Token 优化：为 Clawdbot 压缩超长上下文
            context = kwargs.get("context", "")
            # 调用 Agent 的摘要能力 (此处简化)
            summary = f"OmniGate 摘要: {context[:100]}... [已压缩]"
            return APIResponse(status="success", data={"summary": summary})

        return APIResponse(status="error", error=f"Unknown method for Clawdbot: {method}")
