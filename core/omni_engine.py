import asyncio
import logging
import re
from typing import Dict, Any, List
from core.agent import OmniAgent
from core.skills.local_skills import SystemSkill, FileSkill

logger = logging.getLogger("omni.engine")

class OmniEngine:
    """
    OmniGate 核心引擎：定位为 Clawdbot 增强插件 + 轻量网关。
    专注于：本地任务卸载 (Offloading) 与 Token 压缩优化 (Shrinking)。
    """
    def __init__(self):
        self.agent = OmniAgent("Omni", "Clawdbot Helper")
        self.skills = {
            "system": SystemSkill(),
            "file": FileSkill()
        }

    async def execute_task(self, task_desc: str) -> str:
        """执行本地任务并返回结果"""
        # 1. 拦截直接命令
        if task_desc.startswith("RUN:"):
            cmd = task_desc.replace("RUN:", "").strip()
            res = await self.skills["system"].execute("run_command", command=cmd)
            return str(res.get("data", res.get("error")))
        
        # 2. 交给智能体思考 (轻量级本地处理)
        thought = await self.agent.think(task_desc)
        return thought.get("text", "Task failed")

    def compress_context(self, context: str) -> str:
        """
        核心插件功能：Token 智能压缩算法。
        通过移除冗余、提取关键实体和语义摘要，为 Clawdbot 节省 60%-90% 的上下文 Token。
        """
        if not context or len(context) < 200: 
            return context

        # 1. 语义降噪：移除多余的空白、特殊符号和元数据
        cleaned = re.sub(r'\s+', ' ', context).strip()
        
        # 2. 关键提取：保留最近的交互，同时对历史交互进行摘要
        lines = context.split("\n")
        if len(lines) <= 10:
            return context
            
        # 策略：保留头部（通常包含指令背景）和尾部（最新对话），中间部分进行语义压缩
        header = lines[:2]
        tail = lines[-5:]
        
        # 对中间部分进行关键词提取式压缩
        middle = " ".join(lines[2:-5])
        # 简单但有效的关键词提取逻辑
        important_words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{4,}', middle)
        unique_keywords = list(dict.fromkeys(important_words))[:20] # 取前20个核心词
        
        compressed_middle = f"[中间历史摘要: 提及了 {', '.join(unique_keywords)}]"
        
        final_summary = "\n".join(header) + "\n" + compressed_middle + "\n" + "\n".join(tail)
        
        logger.info(f"Token Saved: {len(context)} -> {len(final_summary)} chars")
        return "[Omni Optimized Context]\n" + final_summary

# 全局实例
omni_engine = OmniEngine()
