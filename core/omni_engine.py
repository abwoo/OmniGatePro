import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.persona import persona_engine
from core.llm_gateway import LLMGateway

logger = logging.getLogger("omni.core.agent")

class OmniAgent:
    """
    通用智能体 (OmniAgent)
    支持真实任务执行、Token 优化与本地记忆。
    """
    def __init__(self, name: str, role: str, persona_type: str = "scholarly"):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.persona_type = persona_type
        self.memory: List[Dict] = []
        self.llm = LLMGateway()

    async def think(self, user_input: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        推理逻辑：分析用户意图并决定是否调用技能。
        """
        # 优化：压缩上下文 (Token Optimization)
        compressed_context = self._compress_memory()
        
        system_prompt = (
            f"你是一个名为 {self.name} 的全能智能体助理。你的角色是 {self.role}。\n"
            "你可以通过调用技能来完成真实任务。如果你认为需要执行系统命令或操作文件，请在回答中包含特定的指令格式。\n"
            f"历史记忆摘要：{compressed_context}"
        )
        
        # 调用 LLM 进行推理
        prompt = f"{system_prompt}\n\n用户输入：{user_input}\n上下文：{context or '无'}"
        res = await self.llm.chat("deepseek", prompt, "system_user")
        
        return res

    def _compress_memory(self) -> str:
        """
        Token 优化：对长对话记忆进行摘要压缩。
        """
        if len(self.memory) < 5:
            return str(self.memory)
        
        # 简单的滑动窗口 + 关键信息提取逻辑 (示例)
        recent = self.memory[-3:]
        summary = f"用户之前讨论过 {len(self.memory)} 个话题，最近关注点在：{recent[-1].get('content', '')[:50]}"
        return summary

    async def speak(self, user_id: str, context: str, content: Any) -> str:
        """个性化表达"""
        response = await persona_engine.generate_response(user_id, context, content, self.memory)
        self.memory.append({"role": "assistant", "content": response})
        if len(self.memory) > 10: self.memory.pop(0)
        return response

class OmniOrchestrator:
    """
    全能编排网关：管理多平台 API、Skills 与 Agents。
    """
    def __init__(self):
        self.agents: Dict[str, OmniAgent] = {}
        self.skills: Dict[str, Any] = {}
        self._init_core_skills()

    def _init_core_skills(self):
        from core.skills.local_skills import SystemSkill, FileSkill
        self.register_skill(SystemSkill())
        self.register_skill(FileSkill())

    def register_agent(self, agent: OmniAgent):
        self.agents[agent.name] = agent

    def register_skill(self, skill: Any):
        self.skills[skill.name] = skill

    async def dispatch(self, user_input: str, user_id: str = "default") -> str:
        """
        智能分发：OmniGate 的核心入口。
        """
        # 1. 选择合适的 Agent (默认使用 general_agent)
        agent = self.agents.get("omni", OmniAgent("Omni", "全能助理"))
        
        # 2. Agent 思考
        thought_res = await agent.think(user_input)
        raw_text = thought_res.get("text", "")
        
        # 3. 检查是否需要执行本地技能 (此处简化，实际应由 LLM 输出结构化 JSON)
        # 示例：如果回复中包含 "RUN_CMD: xxx"
        if "RUN_CMD:" in raw_text:
            cmd = raw_text.split("RUN_CMD:")[1].strip().split("\n")[0]
            skill_res = await self.skills["system"].execute("run_command", command=cmd)
            return await agent.speak(user_id, "执行任务结果", skill_res)
            
        return await agent.speak(user_id, "普通对话", thought_res)

# 全局实例
omni_orchestrator = OmniOrchestrator()
