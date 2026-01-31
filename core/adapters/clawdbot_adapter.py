from core.adapters.base import BaseAdapter, APIResponse
from core.omni_engine import omni_engine
import logging

logger = logging.getLogger("omni.adapters.clawdbot")

class ClawdbotAdapter(BaseAdapter):
    """
    Clawdbot 核心插件适配器：极致轻量，聚焦于任务卸载与 Token 优化。
    """
    @property
    def name(self) -> str:
        return "clawdbot"

    async def call(self, method: str, **kwargs) -> APIResponse:
        try:
            if method == "offload":
                # 将 Clawdbot 的任务卸载到本地执行
                task = kwargs.get("task")
                res = await omni_engine.execute_task(task)
                return APIResponse(status="success", data=res)
            
            elif method == "shrink":
                # 本地 Token 压缩服务
                ctx = kwargs.get("context", "")
                summary = omni_engine.compress_context(ctx)
                return APIResponse(status="success", data={"summary": summary})

            return APIResponse(status="error", error=f"Unsupported: {method}")
        except Exception as e:
            return self.format_error(e)
