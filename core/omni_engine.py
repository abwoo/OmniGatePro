import asyncio
import logging
from typing import Dict, Any
from core.agent import OmniAgent
from core.skills.local_skills import SystemSkill, FileSkill

logger = logging.getLogger("omni.engine")

class OmniEngine:
    """
    OmniGate 核心引擎：定位为 Clawdbot 增强插件 + 轻量网关。
    """
    def __init__(self):
        self.agent = OmniAgent("Omni", "Clawdbot Helper")
        self.skills = {
            "system": SystemSkill(),
            "file": FileSkill()
        }

    async def execute_task(self, task_desc: str) -> str:
        """执行本地任务并返回结果"""
        # 简单正则/关键字匹配，无需 LLM 即可执行常用命令 (更轻量)
        if task_desc.startswith("RUN:"):
            cmd = task_desc.replace("RUN:", "").strip()
            res = await self.skills["system"].execute("run_command", command=cmd)
            return str(res.get("data", res.get("error")))
        
        # 否则交给 Agent 思考
        thought = await self.agent.think(task_desc)
        return thought.get("text", "Task failed")

    def compress_context(self, context: str) -> str:
        """Token 优化核心：本地摘要算法 (无需 LLM)"""
        if not context: return ""
        lines = context.split("\n")
        # 简单的基于关键词和长度的压缩逻辑
        summary = [line for line in lines if len(line) > 5][-3:]
        return "[Omni Compressed] " + " | ".join(summary)

# 全局实例
omni_engine = OmniEngine()
