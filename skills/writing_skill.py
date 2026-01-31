from typing import List, Dict, Any
from core.skill import BaseSkill, skill_tool

class WritingSkill(BaseSkill):
    """
    作文辅导技能：修辞识别、结构评分
    """
    name = "writing"
    description = "Educational writing skill for composition analysis and feedback."

    @skill_tool(description="识别作文中的修辞手法")
    def detect_rhetoric(self, content: str) -> Dict[str, List[str]]:
        rhetoric_map = {
            "拟人": ["钻出来", "点头", "低语", "沉思"],
            "排比": ["有的...有的...", "不仅...而且...还..."],
            "比喻": ["像", "好似", "仿佛", "宛如"]
        }
        
        found = {}
        for style, keywords in rhetoric_map.items():
            matches = [k for k in keywords if k in content]
            if matches:
                found[style] = matches
                
        return found

    @skill_tool(description="对作文结构进行初步评估并给出改进建议")
    def evaluate_structure(self, content: str) -> Dict[str, Any]:
        paragraphs = content.split('\n')
        para_count = len([p for p in paragraphs if p.strip()])
        
        score = 0
        feedback = ""
        
        if para_count < 3:
            score = 60
            feedback = "结构过于单薄，建议增加‘总-分-总’的层次感，至少包含开头、正文和结尾。"
        elif 3 <= para_count <= 5:
            score = 85
            feedback = "结构清晰，层次分明。如果能增加段落间的过渡句会更好。"
        else:
            score = 90
            feedback = "结构严谨，细节丰富。注意段落重点的平衡，避免头重脚轻。"
            
        return {
            "score": score,
            "paragraph_count": para_count,
            "suggestion": feedback
        }
