import logging
import asyncio
import json
import sys
import os
from typing import Optional, Dict, Any

# 将项目根目录添加到路径中，确保可以找到 core 和 skills 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
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
from core.agent import orchestrator
from skills.utility_skills import UtilitySkills

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
        self.utility = UtilitySkills()
        self.app = ApplicationBuilder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """配置指令与消息处理器"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("debate", self.debate_command))
        self.app.add_handler(CommandHandler("collab", self.collab_command))
        self.app.add_handler(CommandHandler("interact", self.interact_command))
        self.app.add_handler(CommandHandler("monitor", self.monitor_command))
        
        # 兼容旧指令作为快捷方式
        self.app.add_handler(CommandHandler("tutor", self.collab_command))
        self.app.add_handler(CommandHandler("critique", self.collab_command))
        
        # 实用工具指令
        self.app.add_handler(CommandHandler("weather", self.weather_command))
        self.app.add_handler(CommandHandler("translate", self.translate_command))
        
        # 处理普通文本消息
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

    async def post_init(self, application):
        """启动后的初始化：更新机器人指令菜单"""
        commands = [
            BotCommand("start", "开始使用"),
            BotCommand("collab", "多 Agent 协同创作"),
            BotCommand("debate", "启动专家辩论"),
            BotCommand("interact", "Agent 互动工坊"),
            BotCommand("weather", "查询天气"),
            BotCommand("monitor", "系统监控"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("✅ 机器人指令菜单已更新")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_msg = (
            "🎨 *Artfish Studio Pro 已上线*\n\n"
            "支持高度个性化的多 Agent 协作系统：\n"
            "- /collab <灵感>: 启动多 Agent 协同创作流\n"
            "- /debate <主题>: 启动专家 Agent 间的深度辩论\n"
            "- /interact <主题>: 启动 Agent 间的艺术互动工坊\n"
            "- /weather <城市>: 查询天气 (实用工具)\n"
            "- /monitor: 查看系统实时监控仪表盘"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    async def interact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        topic = " ".join(context.args)
        if not topic:
            await update.message.reply_text("💡 请输入互动讨论的主题。")
            return
            
        await update.message.reply_chat_action("typing")
        dialogue = await orchestrator.run_interaction(topic, ["tutor", "artist"], rounds=2)
        content = "\n\n".join(dialogue)
        await update.message.reply_text(f"🎭 *Agent 艺术互动记录：*\n\n{content}")

    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        city = " ".join(context.args) or "北京"
        res = await self.utility.get_weather(city)
        await update.message.reply_text(res)

    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = " ".join(context.args)
        if not text: return
        res = await self.utility.translate_text(text)
        await update.message.reply_text(res)

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
            "📊 *系统实时监控仪表盘*\n\n"
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

    def run(self):
        """启动机器人"""
        logger.info("Artfish Studio Bot is starting...")
        self.app.post_init = self.post_init # 注册初始化回调
        self.app.run_polling()

if __name__ == "__main__":
    # 优先从配置类读取 Token
    TOKEN = settings.TELEGRAM_BOT_TOKEN or "8434211814:AAFUTWoELMEIio7O8zkKo9siFp233MUQt2A"
    
    if not TOKEN or TOKEN.startswith("YOUR_"):
        logger.error("❌ 未检测到有效的 TELEGRAM_BOT_TOKEN。请在 .env 文件中配置或设置环境变量。")
    else:
        bot = ArtfishStudioBot(TOKEN)
        bot.run()
