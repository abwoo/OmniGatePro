from typing import List, Dict, Any
from core.skill import BaseSkill, skill_tool

class ArtTutorSkill(BaseSkill):
    """
    艺术导师技能：提供色彩理论、构图法则、艺术流派知识
    """
    name = "art_tutor"
    description = "Professional art tutoring skill for theory, composition, and art history."

    THEORY_KNOWLEDGE = {
        "色彩理论": "色彩三要素包括色相、明度和纯度。互补色（如红与绿）能产生强烈的对比效果。",
        "三分构图": "将画面横竖各三等分，将主体放在交叉点上，可以使画面更有动感和平衡感。",
        "印象派": "强调光影的瞬间变化，提倡户外写生，代表人物有莫奈、雷诺阿。"
    }

    @skill_tool(description="获取特定的艺术理论知识")
    def get_theory(self, concept: str = "", goal: str = "") -> str:
        # 兼容 concept 或 goal
        text = concept or goal
        return self.THEORY_KNOWLEDGE.get(text, f"抱歉，我目前还没有关于 '{text}' 的深度知识，但我可以帮你查询相关流派。")

    @skill_tool(description="推荐适合当前创作主题的配色方案")
    def suggest_color_palette(self, mood: str = "", goal: str = "") -> Dict[str, Any]:
        # 兼容参数
        text = mood or goal
        palettes = {
            "忧郁": ["#4682B4", "#708090", "#2F4F4F"],
            "热情": ["#FF4500", "#FFD700", "#B22222"],
            "自然": ["#228B22", "#8B4513", "#F5F5DC"]
        }
        
        # 简单匹配氛围
        selected_mood = "自然"
        for m in palettes.keys():
            if m in text:
                selected_mood = m
                break
                
        return {
            "mood": selected_mood,
            "colors": palettes.get(selected_mood),
            "advice": f"基于 '{selected_mood}' 的氛围，建议使用对比鲜明的色调来增强表现力。"
        }
