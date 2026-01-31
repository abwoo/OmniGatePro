import logging
import asyncio
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from core.config import settings
from core.omni_engine import omni_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omni.bot")

class OmniBot:
    """
    OmniGate 极简版 Bot：智能手机级交互体验。
    """
    def __init__(self, token: str):
        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("menu", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle))

    async def post_init(self, application):
        await application.bot.set_my_commands([
            BotCommand("start", "主菜单"),
            BotCommand("menu", "快捷功能")
        ])

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        menu = (
            "📱 *OmniGate Pro - Clawdbot 增强插件*\n\n"
            "极简操作指令：\n"
            "- 直接发送任务 (如: `读取当前目录`)\n"
            "- 发送 `RUN: <命令>` 执行本地指令\n"
            "- 系统会自动为 Clawdbot 优化 Token"
        )
        await update.message.reply_text(menu, parse_mode='Markdown')

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        await update.message.reply_chat_action("typing")
        
        # 调用核心引擎执行
        res = await omni_engine.execute_task(user_input)
        await update.message.reply_text(f"✅ *执行结果:*\n\n{res}", parse_mode='Markdown')

    def run(self):
        self.app.post_init = self.post_init
        self.app.run_polling()

if __name__ == "__main__":
    TOKEN = settings.TELEGRAM_BOT_TOKEN or "8434211814:AAFUTWoELMEIio7O8zkKo9siFp233MUQt2A"
    OmniBot(TOKEN).run()
