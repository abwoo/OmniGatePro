import logging
import asyncio
import json
import sys
import os
from typing import Optional, Dict, Any

# 将项目根目录添加到路径中，确保可以找到 core 和 skills 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from core.config import settings
from core.gateway_pro import pro_gateway
from core.orchestrator_pro import discussion_room, multimodal_creator

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("artfish.studio.bot")

class ArtfishStudioBot:
    """
    Artfish Studio Pro Telegram Bot: 高度可扩展的多 Agent 智能系统
    """
    def __init__(self, token: str):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """配置指令与消息处理器"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("debate", self.debate_command))
        self.app.add_handler(CommandHandler("collab", self.collab_command))
        self.app.add_handler(CommandHandler("monitor", self.monitor_command))
        
        # 处理普通文本消息
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_msg = (
            "🎨 *Artfish Studio Pro 已上线*\n\n"
            "支持高度个性化的多 Agent 协作系统：\n"
            "- /debate <主题>: 启动专家 Agent 间的深度辩论\n"
            "- /collab <灵感>: 启动多 Agent 协同创作流\n"
            "- /monitor: 查看系统实时监控仪表盘"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def debate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = " ".join(context.args)
        if not topic:
            await update.message.reply_text("💡 请输入辩论主题。")
            return
        
        await update.message.reply_chat_action("typing")
        res = await pro_gateway.handle_request(str(update.effective_user.id), "debate", {"topic": topic})
        
        if res["status"] == "success":
            content = "\n\n---\n\n".join(res["data"])
            await update.message.reply_text(f"⚖️ *专家辩论结果：*\n\n{content}", parse_mode='Markdown')

    async def collab_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        prompt = " ".join(context.args)
        if not prompt:
            await update.message.reply_text("💡 请输入创作灵感。")
            return
            
        await update.message.reply_chat_action("typing")
        dialogue = await discussion_room.start_session(str(update.effective_user.id), prompt)
        await update.message.reply_text(f"🤝 *多 Agent 协作讨论记录：*\n\n{dialogue}")

    async def monitor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = pro_gateway.get_dashboard_data()
        msg = (
            "� *系统实时监控仪表盘*\n\n"
            f"• 总请求数: {data['requests_per_minute']}\n"
            f"• 平均延迟: {data['avg_latency_ms']}ms\n"
            f"• 错误率: {data['error_rate']}\n"
            f"• 熔断器状态: {data['circuit_breaker']}\n"
            f"• 活跃 Agent: {', '.join(data['active_agents'])}"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 默认触发讨论室
        await self.collab_command(update, context)

    async def _execute_art_task(self, update: Update, skill: str, tool: str, **kwargs):
        """执行艺术任务并反馈（非阻塞异步执行）"""
        try:
            await update.message.reply_chat_action("typing")
            
            # 使用 asyncio.to_thread 防止同步执行阻塞事件循环
            result = await asyncio.to_thread(
                self.gateway.skill_manager.execute, 
                skill, 
                tool, 
                **kwargs
            )
            
            # 格式化回复
            response = self._format_studio_response(skill, tool, result)
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Studio Bot Error: {e}")
            await update.message.reply_text(f"❌ 协作过程中出现小插曲：{str(e)}")

    def _format_studio_response(self, skill: str, tool: str, result: Any) -> str:
        """针对艺术场景格式化回复"""
        if skill == "art_tutor":
            return f"💡 *艺术导师建议：*\n\n{result}"
        elif skill == "art_critique":
            res = result
            return (
                f"🧐 *专业评审报告：*\n\n"
                f"📊 综合评分: {res['overall_score']:.1f}\n"
                f"📝 详细反馈: {res['expert_feedback']}\n"
                f"💡 改进方向: {res['improvement_tip']}"
            )
        return f"✅ 任务执行成功：\n{json.dumps(result, indent=2, ensure_ascii=False)}"

    def run(self):
        """启动机器人"""
        logger.info("Artfish Studio Bot is starting...")
        self.app.run_polling()

if __name__ == "__main__":
    # 优先从配置类读取 Token
    TOKEN = settings.TELEGRAM_BOT_TOKEN or "8434211814:AAFUTWoELMEIio7O8zkKo9siFp233MUQt2A"
    
    if not TOKEN or TOKEN.startswith("YOUR_"):
        logger.error("❌ 未检测到有效的 TELEGRAM_BOT_TOKEN。请在 .env 文件中配置或设置环境变量。")
    else:
        bot = ArtfishStudioBot(TOKEN)
        bot.run()
