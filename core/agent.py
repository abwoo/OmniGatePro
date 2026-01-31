import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.persona import persona_engine
from core.api_engine import api_engine

logger = logging.getLogger("artfish.pro.agent")

class ArtAgent(ABC):
    """
    高度可扩展的多智能体基类。
    支持分布式调用、个性化表达与自主协作。
    """
    def __init__(self, name: str, role: str, persona_type: str = "encouraging"):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.persona_type = persona_type
        self.memory: List[Dict] = []

    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务的核心逻辑"""
        pass

    async def speak(self, user_id: str, context: str, content: Any) -> str:
        """通过个性化引擎生成发言"""
        response = await persona_engine.generate_response(user_id, context, content, self.memory)
        # 记录自己的发言到记忆中
        self.memory.append({"role": "assistant", "content": response})
        if len(self.memory) > 10: # 保持最近 10 条记忆
            self.memory.pop(0)
        return response

class AgentOrchestrator:
    """
    Agent 编排系统：实现并行处理、交叉验证与协作模式。
    """
    def __init__(self):
        self.agents: Dict[str, ArtAgent] = {}
        self.task_queue = asyncio.Queue()

    def register_agent(self, agent: ArtAgent):
        self.agents[agent.name] = agent

    async def run_parallel(self, task_description: str, agent_names: List[str]) -> Dict[str, Any]:
        """并行任务处理模式"""
        tasks = []
        for name in agent_names:
            if name in self.agents:
                tasks.append(self.agents[name].process_task({"description": task_description}))
        
        results = await asyncio.gather(*tasks)
        return {name: res for name, res in zip(agent_names, results)}

    async def run_debate(self, topic: str, pro_agent_name: str, con_agent_name: str) -> List[str]:
        """辩论模式：对同一任务启动正反方 Agent 进行多轮论证"""
        pro_agent = self.agents.get(pro_agent_name)
        con_agent = self.agents.get(con_agent_name)
        
        if not pro_agent or not con_agent:
            return ["无法启动辩论：Agent 未就绪"]

        dialogue = []
        context = f"关于主题 '{topic}' 的学术辩论"
        
        # 第一轮：陈述观点
        pro_view = await pro_agent.process_task({"topic": topic, "side": "pro"})
        dialogue.append(await pro_agent.speak("system", context, pro_view))
        
        con_view = await con_agent.process_task({"topic": topic, "side": "con", "opponent_view": pro_view})
        dialogue.append(await con_agent.speak("system", context, con_view))
        
        return dialogue

    async def run_interaction(self, topic: str, agent_names: List[str], rounds: int = 3) -> List[str]:
        """艺术互动模式：多个 Agent 围绕主题进行多轮交互互动"""
        if not all(name in self.agents for name in agent_names):
            return ["无法启动互动：部分 Agent 未注册"]

        dialogue = []
        context = f"关于 '{topic}' 的艺术互动工坊"
        last_message = f"我们要讨论的主题是：{topic}"

        for i in range(rounds):
            for name in agent_names:
                agent = self.agents[name]
                # Agent 根据上一条消息产生新的想法
                response_data = await agent.process_task({
                    "topic": topic,
                    "last_interaction": last_message,
                    "round": i + 1
                })
                # 个性化发言
                speech = await agent.speak("system", context, response_data)
                formatted_speech = f"[{agent.name} ({agent.role})]: {speech}"
                dialogue.append(formatted_speech)
                last_message = speech # 更新上下文

        return dialogue

# 全局编排器
orchestrator = AgentOrchestrator()
