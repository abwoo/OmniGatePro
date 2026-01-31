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
        :param user_id: 用户唯一标识
        :param context: 当前交互场景描述
        :param base_content: 技能生成的原始结果（如评分、建议）
        :param user_history: 用户历史交互记录，用于行为分析
        """
        # 1. 行为分析：基于历史记录动态选择性格
        personality = self._analyze_user_preference(user_history)
        style_instruction = self.personality_templates.get(personality, self.personality_templates["encouraging"])

        # 2. 构建 Prompt
        prompt = (
            f"你现在的身份是一个具有以下特征的艺术 Agent：{style_instruction}\n"
            f"用户当前的上下文：{context}\n"
            f"原始数据结果：{base_content}\n"
            f"请根据以上信息，生成一段具有个性化风格、情感丰富且自然的回复。不要直接输出原始数据，要将其融入到对话中。"
        )

        # 3. 调用 LLM 生成
        try:
            # 默认使用 deepseek 或第一个可用模型
            response = await self.llm_gateway.chat("deepseek", prompt, user_id)
            if response.get("status") == "success":
                return response.get("text", self._fallback_format(base_content))
            return self._fallback_format(base_content)
        except Exception as e:
            logger.error(f"Persona generation failed: {e}")
            return self._fallback_format(base_content)

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
