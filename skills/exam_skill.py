import random
from typing import List, Dict, Any
from core.skill import BaseSkill, skill_tool

class ExamSkill(BaseSkill):
    """
    智能测评技能：阶梯式出题、难度评估
    """
    name = "exam"
    description = "Smart examination skill for generating quizzes and assessing difficulty."

    @skill_tool(description="根据知识点生成阶梯式练习题")
    def generate_quiz(self, kp_title: str, difficulty: int = 1) -> Dict[str, Any]:
        # 模拟出题库
        quizzes = {
            "勾股定理": [
                {"q": "直角三角形直角边为3和4，求斜边。", "level": 1, "tags": ["计算"]},
                {"q": "已知直角三角形周长为12，两边长为3和4，判断其类型。", "level": 2, "tags": ["逻辑", "逆定理"]},
                {"q": "证明：勾股定理在非欧几何中是否成立？", "level": 5, "tags": ["理论", "拓展"]}
            ],
            "拟人": [
                {"q": "请写出一个描写‘风’的拟人句。", "level": 1, "tags": ["基础写作"]},
                {"q": "分析《春》中‘小草偷偷地从土里钻出来’的修辞效果。", "level": 3, "tags": ["文学鉴赏"]}
            ]
        }
        
        pool = quizzes.get(kp_title, [{"q": f"关于{kp_title}的基础练习题", "level": 1, "tags": ["通用"]}])
        # 过滤难度
        filtered = [q for q in pool if q["level"] <= difficulty + 1]
        
        return {
            "question": random.choice(filtered) if filtered else pool[0],
            "kp": kp_title,
            "difficulty_assigned": difficulty
        }

    @skill_tool(description="评估学生答案的错误模式")
    def analyze_error_pattern(self, student_answer: str, correct_answer: str) -> str:
        # 模拟错误分析逻辑
        if student_answer.isdigit() and correct_answer.isdigit():
            diff = abs(int(student_answer) - int(correct_answer))
            if diff < 5: return "计算失误：结果接近，可能是加减乘除过程中的小疏忽。"
        
        if len(student_answer) < len(correct_answer) * 0.5:
            return "知识点遗漏：回答过于简略，未覆盖核心得分点。"
            
        return "逻辑偏差：解题思路偏离了核心知识点的应用范围。"
