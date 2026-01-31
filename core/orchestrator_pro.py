import asyncio
from typing import List, Dict, Any
from core.agent import orchestrator
from core.agents.art_agents import TutorAgent, ArtistAgent, CriticAgent

class DiscussionRoom:
    """
    Agent 讨论室：支持多个 Agent 对同一任务进行相互讨论与协同。
    """
    def __init__(self):
        # 注册基础 Agent
        orchestrator.register_agent(TutorAgent())
        orchestrator.register_agent(ArtistAgent())
        orchestrator.register_agent(CriticAgent())

    async def start_session(self, user_id: str, prompt: str) -> str:
        """
        开启一个讨论会话。
        """
        context = f"关于 '{prompt}' 的创作讨论"
        
        # 1. 并行获取初始观点
        views = await orchestrator.run_parallel(prompt, ["tutor", "artist"])
        
        # 2. 交叉验证 (评审介入)
        critic_task = {"description": prompt, "opponent_view": views["artist"]}
        critique = await orchestrator.agents["critic"].process_task(critic_task)
        
        # 3. 汇总讨论结果并个性化输出
        final_dialogue = []
        final_dialogue.append(await orchestrator.agents["tutor"].speak(user_id, context, views["tutor"]))
        final_dialogue.append(await orchestrator.agents["artist"].speak(user_id, context, views["artist"]))
        final_dialogue.append(await orchestrator.agents["critic"].speak(user_id, context, critique))
        
        return "\n\n".join(final_dialogue)

class MultiModalCreator:
    """
    协同创作引擎：多个 Agent 共同生成包含文本、图像建议的模态内容。
    """
    async def create_collaborative_work(self, theme: str) -> Dict[str, Any]:
        # 1. 导师定调 (Text)
        tutor_view = await orchestrator.agents["tutor"].process_task({"topic": theme})
        
        # 2. 艺术家生成视觉提示词 (Image Suggestion)
        artist_concept = await orchestrator.agents["artist"].process_task({"theme": theme})
        
        # 3. 评审优化
        final_advice = await orchestrator.agents["critic"].process_task({"concept": artist_concept})
        
        return {
            "theme": theme,
            "theory": tutor_view,
            "visual_prompt": artist_concept,
            "optimization": final_advice
        }

# 实例
discussion_room = DiscussionRoom()
multimodal_creator = MultiModalCreator()
