import re
from typing import List, Dict, Any
from core.skill import BaseSkill, skill_tool

class TutorSkill(BaseSkill):
    """
    学科辅导技能：提供智能答疑、术语识别与启发式引导
    """
    name = "tutor"
    description = "Educational tutoring skill for subject Q&A and term recognition."

    # 学科专业术语库 (模拟核心术语识别)
    SUBJECT_TERMS = {
        "math": ["勾股定理", "二次函数", "全等三角形", "导数", "积分", "矩阵"],
        "physics": ["牛顿定律", "动量守恒", "安培力", "光电效应", "量子力学"],
        "chinese": ["修辞手法", "借代", "排比", "拟人", "文言文", "通假字"],
        "english": ["Past Participle", "Subjunctive Mood", "Relative Clause"]
    }

    @skill_tool(description="识别输入中的学科术语并提供初步解析")
    def recognize_terms(self, text: str) -> Dict[str, Any]:
        found_terms = []
        subject_detected = "unknown"
        
        for subject, terms in self.SUBJECT_TERMS.items():
            for term in terms:
                if term in text:
                    found_terms.append(term)
                    subject_detected = subject
                    
        return {
            "found_terms": found_terms,
            "subject": subject_detected,
            "count": len(found_terms),
            "confidence": 0.95 if found_terms else 0.0
        }

    @skill_tool(description="针对特定知识点提供启发式引导（不直接给出答案）")
    def heuristic_tutor(self, query: str = "", goal: str = "", subject: str = "math") -> str:
        # 兼容 query 或 goal 参数
        text = query or goal
        if "勾股定理" in text:
            return "思考一下：在一个直角三角形中，两条直角边的平方和与斜边的平方有什么关系？你可以尝试画一个 3x3 和 4x4 的正方形拼接看看。"
        elif "拟人" in text:
            return "回想一下：如果我们把桌子描述成‘它在那儿沉思’，这赋予了它什么特质？这能让描写更生动吗？"
        
        return "这个问题很有趣。我们可以先从这个概念的最基础定义开始回顾，你觉得它在实际题目中通常出现在什么位置？"

    @skill_tool(description="解析数学公式（支持简单的 LaTeX 提取）")
    def parse_formula(self, latex_str: str) -> Dict[str, str]:
        # 模拟公式解析逻辑
        clean_latex = latex_str.strip("$ ")
        if "^2" in clean_latex and "+" in clean_latex:
            return {"type": "Pythagorean/Quadratic", "parsed": clean_latex, "message": "识别到平方和公式或二次型"}
        
        return {"type": "generic", "parsed": clean_latex, "message": "公式已解析为标准字符串"}
