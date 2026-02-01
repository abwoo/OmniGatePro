import asyncio
import logging
import re
import os
import json
from typing import Dict, Any, List, Optional
from core.agent import OmniAgent
from core.skills.local_skills import SystemSkill, FileSkill
from core.token_tracker import token_tracker

logger = logging.getLogger("omni.engine")

class MemoryStore:
    """本地持久化记忆存储"""
    def __init__(self, storage_path: str = "data/memory.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.memory = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
        return {"user_profile": {}, "long_term_facts": [], "task_history": []}

    def save(self):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def update_profile(self, key: str, value: Any):
        self.memory["user_profile"][key] = value
        self.save()

    def add_fact(self, fact: str):
        if fact not in self.memory["long_term_facts"]:
            self.memory["long_term_facts"].append(fact)
            self.save()

class OmniEngine:
    """
    OmniGate 核心引擎：定位为 Clawdbot 增强插件 + 轻量网关。
    专注于：本地任务卸载 (Offloading)、Token 压缩优化 (Shrinking) 与长效记忆 (Memory)。
    """
    def __init__(self):
        self.agent = OmniAgent("Omni", "Clawdbot Helper")
        self.memory = MemoryStore()
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
        
        # 2. 记忆注入：如果是自我介绍或偏好设置，存入记忆
        if any(k in task_desc.lower() for k in ["我是", "我喜欢", "记住", "我的名字"]):
            self.memory.add_fact(task_desc)
            return f"Omni 已将此信息存入长效记忆：'{task_desc}'"

        # 3. 交给智能体思考 (轻量级本地处理)
        thought = await self.agent.think(task_desc)
        return thought.get("text", "Task failed")

    def compress_context(self, context: str, provider: str = "deepseek", scene: str = "general") -> str:
        """
        核心插件功能：语义级 Token 压缩算法 (Smart Shrinking)。
        针对 DeepSeek 进行优化，自动识别关键路径、API Key 和代码块。
        """
        if not context or len(context) < 400: 
            return context

        original_len = len(context)
        
        # 1. 保护性提取：防止压缩破坏关键信息
        # 保护 API Keys
        keys = re.findall(r'sk-[a-zA-Z0-9]{20,}', context)
        # 保护 文件路径
        paths = re.findall(r'[a-zA-Z]:\\[^ \n]+|/[a-zA-Z0-9/_.-]+', context)
        # 保护 代码块 (极简提取)
        code_snippets = re.findall(r'```[\s\S]*?```', context)
        
        important_entities = list(dict.fromkeys(keys + paths))
        
        # 2. 结构化降噪
        lines = [line.strip() for line in context.split("\n") if line.strip()]
        if len(lines) <= 10:
            return context
            
        # 保留最近的对话 (Last 5 lines) 和 系统提示 (First 2 lines)
        header = lines[:2]
        tail = lines[-6:]
        
        # 3. 中间层语义压缩
        middle_lines = lines[2:-6]
        middle_text = " ".join(middle_lines)
        
        # 提取动词和名词作为摘要
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,}|[A-Z][a-z]{3,}', middle_text)
        summary_points = list(dict.fromkeys(keywords))[:20]
        
        # 注入长效记忆提示 (如果存在)
        mem_info = ""
        if self.memory.memory["long_term_facts"]:
            relevant_mems = self.memory.memory["long_term_facts"][-3:]
            mem_info = f"\n[长效记忆提示: {'; '.join(relevant_mems)}]"

        compressed_middle = f"\n[历史上下文压缩摘要: 讨论了 {', '.join(summary_points)}]"
        if important_entities:
            compressed_middle += f" | 关键实体: {', '.join(important_entities[:5])}"
        
        # 重新组装
        final_summary = "\n".join(header) + mem_info + compressed_middle + "\n" + "\n".join(tail)
        
        # 如果有代码块，选择性保留最新的一个
        if code_snippets:
            final_summary += f"\n\n[附带最新代码片段引用]\n{code_snippets[-1]}"

        # 记录节省数据
        token_tracker.record(provider, scene, original_len, len(final_summary))
        
        logger.info(f"Token Optimized: {original_len} -> {len(final_summary)} bytes")
        return "[Omni Optimized Context]\n" + final_summary

# 全局实例
omni_engine = OmniEngine()
