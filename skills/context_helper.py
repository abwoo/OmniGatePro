from core.skill import BaseSkill, skill_tool
from core.omni_engine import omni_engine

class ContextHelperSkill(BaseSkill):
    """
    上下文辅助技能：直接在对话中触发 Token 压缩或记忆检索。
    """
    name = "context_helper"
    description = "Advanced context and memory management tools"

    @skill_tool(name="force_shrink", description="强制压缩当前提供的文本块")
    def force_shrink(self, text: str) -> str:
        return omni_engine.compress_context(text)

    @skill_tool(name="recall_memory", description="检索本地长效记忆中的关键信息")
    def recall_memory(self) -> str:
        mems = omni_engine.memory.memory.get("long_term_facts", [])
        if not mems:
            return "记忆库目前为空。"
        return "🧠 检索到的长效记忆:\n" + "\n".join([f"- {m}" for m in mems[-10:]])
