from core.agent import ArtAgent
from typing import Dict, Any

class TutorAgent(ArtAgent):
    def __init__(self):
        super().__init__("tutor", "艺术导师", persona_type="scholarly")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = task_data.get("topic") or task_data.get("description")
        side = task_data.get("side")
        
        if side == "pro":
            return {"view": f"从艺术史的角度来看，{topic} 极大地推动了形式美的演进。"}
        return {"view": f"关于 {topic}，我们需要关注其构图平衡与色彩心理学的应用。"}

class ArtistAgent(ArtAgent):
    def __init__(self):
        super().__init__("artist", "视觉艺术家", persona_type="mysterious")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"concept": "我看到光影在画布上跳舞，这是一种非理性的美感。"}

class CriticAgent(ArtAgent):
    def __init__(self):
        super().__init__("critic", "专业评审", persona_type="critical")

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        opponent_view = task_data.get("opponent_view", "")
        if opponent_view:
            return {"view": f"我并不同意前者的看法。{opponent_view} 忽略了当代艺术的社会学意义。"}
        return {"critique": "构图略显平庸，建议打破常规。"}
