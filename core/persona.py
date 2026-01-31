import logging
import random
from typing import Dict, Any, List, Optional
from core.llm_gateway import LLMGateway
from core.config import settings

logger = logging.getLogger("artfish.core.persona")

class PersonaEngine:
    """
    个性化内容生成引擎：基于用户历史交互与性格模板生成动态回复。
    """
    def __init__(self):
        self.llm_gateway = LLMGateway()
        # 性格模板配置
        self.personality_templates = {
            "encouraging": "热情、富有鼓励性，多用感叹号，像一个耐心的艺术导师。",
            "critical": "严谨、挑剔、追求极致，像一个毒舌但专业的画廊评论家。",
            "mysterious": "抽象、富有诗意、充满隐喻，像一个超现实主义艺术家。",
            "scholarly": "学究气、注重历史背景、引用专业术语，像一个艺术史教授。"
        }

    async def generate_response(self, user_id: str, context: str, base_content: Any, user_history: List[Dict] = []) -> str:
        """
        生成个性化回复。
        """
        # 1. 行为分析：基于历史记录动态选择性格
        personality = self._analyze_user_preference(user_history)
        style_instruction = self.personality_templates.get(personality, self.personality_templates["encouraging"])

        # 2. 核心：强制性艺术角色扮演 Prompt
        system_prompt = (
            f"你是一个专业的艺术教育助手。你必须严格扮演以下性格角色：{style_instruction}\n"
            "你的任务是根据提供的原始艺术分析数据，生成一段自然、生动且极具专业度的艺术评论。\n"
            "注意规范：\n"
            "1. 严禁提及你是一个AI、助手或大语言模型。\n"
            "2. 严禁使用 '好的'、'当然'、'我能为您做什么' 等通用的AI客套话。\n"
            "3. 必须使用 Markdown 格式，合理使用粗体、列表或引用来增强排版的美观度。\n"
            "4. 如果数据包含评分，请将其转化为感性的艺术评价，而不是简单的数字罗列。\n"
            "5. 你的回复应体现出对色彩理论、艺术史或构图法则的深刻理解。"
        )

        user_prompt = (
            f"当前艺术场景：{context}\n"
            f"原始数据结果：{base_content}\n"
            f"请以此为基础，开始你的专业艺术点评："
        )

        # 3. 调用 LLM 生成 (注入 System Prompt)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            response = await self.llm_gateway.chat("deepseek", full_prompt, user_id)
            if response.get("status") == "success":
                # 后处理：清理可能的 AI 痕迹
                text = response.get("text", "")
                text = self._clean_ai_traces(text)
                return text
            return self._fallback_format(base_content)
        except Exception as e:
            logger.error(f"Persona generation failed: {e}")
            return self._fallback_format(base_content)

    def _clean_ai_traces(self, text: str) -> str:
        """后处理：强制清理 AI 痕迹词汇"""
        traces = [
            "作为AI", "作为一个人工智能", "大语言模型", "好的，", "当然可以", 
            "为您提供帮助", "我能为您做什么", "理解了您的", "为您生成了",
            "DeepSeek", "deepseek", "模型回复"
        ]
        for trace in traces:
            text = text.replace(trace, "")
        
        # 移除常见的 AI 开场白
        lines = text.split("\n")
        if lines and ("分析" in lines[0] or "评价" in lines[0]):
            # 如果第一行是类似 "以下是您的分析" 的废话，尝试移除
            pass 

        return text.strip()

    def _fallback_format(self, content: Any) -> str:
        """兜底格式化：当 LLM 不可用时，将数据转换为可读文本"""
        if isinstance(content, dict):
            # 提取常见的艺术字段
            view = content.get("view") or content.get("concept") or content.get("critique")
            if view:
                return str(view)
            return ", ".join([f"{k}: {v}" for k, v in content.items()])
        return str(content)

    def _analyze_user_preference(self, history: List[Dict]) -> str:
        """
        简单行为分析逻辑：根据用户历史互动频率或关键词选择性格。
        实际系统中可使用更复杂的模型。
        """
        if not history:
            return "encouraging"
        
        # 统计用户常用的词汇倾向（示例逻辑）
        interaction_count = len(history)
        if interaction_count > 10:
            return "critical" # 熟客可以更严厉
        elif any("美" in str(h) for h in history):
            return "mysterious"
        
        return random.choice(list(self.personality_templates.keys()))

# 全局实例
persona_engine = PersonaEngine()
