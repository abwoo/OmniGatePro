from typing import List, Dict, Any
import random
from core.skill import BaseSkill, skill_tool

class ArtCritiqueSkill(BaseSkill):
    """
    艺术鉴赏技能：模拟专业评审进行作品点评
    """
    name = "art_critique"
    description = "Expert art critique skill for aesthetic evaluation and improvement suggestions."

    @skill_tool(description="对艺术作品描述或思路进行审美点评")
    def critique_concept(self, description: str = "", goal: str = "") -> Dict[str, Any]:
        # 兼容参数
        text = description or goal
        aspects = ["构图", "色彩", "创意", "情感"]
        scores = {a: random.randint(70, 95) for a in aspects}
        
        feedback = f"作品构思 '{description}' 具有很强的表现力。 "
        if scores["创意"] > 90:
            feedback += "创意非常新颖，打破了常规的视觉范式。"
        
        return {
            "overall_score": sum(scores.values()) / len(scores),
            "detailed_scores": scores,
            "expert_feedback": feedback,
            "improvement_tip": "建议在细节处增加更多肌理变化，以丰富画面的层次感。"
        }

    @skill_tool(description="分析作品是否符合特定流派的特征")
    def analyze_style_match(self, content: str, style: str) -> str:
        # 简单逻辑模拟
        if style == "印象派" and "光" in content:
            return "匹配度高：准确捕捉到了印象派对光影瞬间捕捉的核心特征。"
        return f"匹配度中等：建议加强对 {style} 典型笔触或色彩逻辑的应用。"
