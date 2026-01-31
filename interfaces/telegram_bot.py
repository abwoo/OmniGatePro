import logging
import asyncio
import json
from typing import Optional, Dict, Any, List
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
from core.gateway import StudioGateway
from core.llm_gateway import LLMGateway
from core.custom_framework import CustomSkillFramework
from skills.utility_skills import UtilitySkills

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("artfish.studio.bot")

class ArtfishStudioBot:
    """
    Artfish Studio Telegram Bot: 
    集成了 5+ 实用技能、多模型 AI 网关、联网能力及自定义指令框架。
    """
    def __init__(self, token: str):
        self.token = token
        self.gateway = StudioGateway()
        self.llm_gateway = LLMGateway()
        self.custom_framework = CustomSkillFramework()
        self.utility = UtilitySkills()
        self.app = ApplicationBuilder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """配置核心与扩展指令处理器"""
        # 基础与艺术指令
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("tutor", self.tutor_command))
        self.app.add_handler(CommandHandler("critique", self.critique_command))
        self.app.add_handler(CommandHandler("collaborate", self.collaborate_command))
        
        # 扩展实用技能指令
        self.app.add_handler(CommandHandler("weather", self.weather_handler))
        self.app.add_handler(CommandHandler("exchange", self.exchange_handler))
        self.app.add_handler(CommandHandler("remind", self.remind_handler))
        self.app.add_handler(CommandHandler("translate", self.translate_handler))
        self.app.add_handler(CommandHandler("browse", self.browse_handler))
        
        # AI API 网关指令
        self.app.add_handler(CommandHandler("api", self.api_handler))
        self.app.add_handler(CommandHandler("stats", self.stats_handler))
        
        # 自定义框架指令
        self.app.add_handler(CommandHandler("add_cmd", self.add_custom_handler))
        self.app.add_handler(CommandHandler("list_cmds", self.list_custom_handler))
        
        # 交互反馈与消息路由
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

    # --- 基础指令实现 ---

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_msg = (
            f"🎨 *Artfish Studio v2.0* 现已上线！\n\n"
            "🚀 *核心功能：*\n"
            "• `/tutor` - 艺术导师\n"
            "• `/api` - 多模型 AI (OpenAI/Claude...)\n"
            "• `/weather`, `/exchange`, `/translate` - 实用工具\n"
            "• `/browse` - 实时联网抓取\n"
            "• `/add_cmd` - 自定义指令\n\n"
            "直接发送文字或指令开始体验吧！"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')

    # --- 实用技能处理器 (异步非阻塞) ---

    async def weather_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        city = " ".join(context.args) or "北京"
        res = await self.utility.get_weather(city)
        await update.message.reply_text(res, parse_mode='Markdown')

    async def exchange_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            amount = float(context.args[0])
            from_curr = context.args[1]
            to_curr = context.args[2]
            res = await self.utility.currency_convert(amount, from_curr, to_curr)
            await update.message.reply_text(res, parse_mode='Markdown')
        except (IndexError, ValueError):
            await update.message.reply_text("💡 用法：`/exchange 100 USD CNY`", parse_mode='Markdown')

    async def remind_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            seconds = int(context.args[0])
            task = " ".join(context.args[1:])
            res = await self.utility.set_reminder(task, seconds)
            await update.message.reply_text(res, parse_mode='Markdown')
        except (IndexError, ValueError):
            await update.message.reply_text("💡 用法：`/remind 60 休息一下`", parse_mode='Markdown')

    async def translate_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = " ".join(context.args)
        if not text:
            await update.message.reply_text("💡 用法：`/translate 内容`", parse_mode='Markdown')
            return
        res = await self.utility.translate_text(text)
        await update.message.reply_text(res, parse_mode='Markdown')

    async def browse_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        url = " ".join(context.args)
        if not url:
            await update.message.reply_text("💡 用法：`/browse https://example.com`", parse_mode='Markdown')
            return
        await update.message.reply_chat_action("typing")
        res = await self.utility.browse_web(url)
        await update.message.reply_text(res, parse_mode='Markdown')

    # --- AI API 接入层处理器 ---

    async def api_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("💡 用法：`/api <openai|claude|gemini> 内容`", parse_mode='Markdown')
            return
        
        provider = context.args[0].lower()
        prompt = " ".join(context.args[1:])
        user_id = str(update.effective_user.id)
        
        await update.message.reply_chat_action("typing")
        try:
            response = await self.llm_gateway.chat(provider, prompt, user_id)
            await update.message.reply_text(response.content)
        except Exception as e:
            await update.message.reply_text(f"❌ API 调用失败：{str(e)}")

    async def stats_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        report = self.llm_gateway.get_billing_report(user_id)
        await update.message.reply_text(report, parse_mode='Markdown')

    # --- 自定义框架处理器 ---

    async def add_custom_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            await update.message.reply_text("💡 用法：`/add_cmd 指令名 模板内容`", parse_mode='Markdown')
            return
        name = context.args[0]
        template = " ".join(context.args[1:])
        res = self.custom_framework.add_command(name, template)
        await update.message.reply_text(res)

    async def list_custom_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        res = self.custom_framework.list_custom_commands()
        await update.message.reply_text(res, parse_mode='Markdown')

    # --- 基础交互逻辑 ---

    async def tutor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        concept = " ".join(context.args) or "色彩理论"
        await self._execute_art_task(update, "art_tutor", "get_theory", concept=concept)

    async def critique_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        description = " ".join(context.args)
        if not description:
            await update.message.reply_text("请输入描述...")
            return
        await self._execute_art_task(update, "art_critique", "critique_concept", description=description)

    async def collaborate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [[InlineKeyboardButton("🎨 邀请艺术家", callback_query_data="invite_artist")]]
        await update.message.reply_text("开启协作模式：", reply_markup=InlineKeyboardMarkup(keyboard))

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("✅ 已成功邀请 Agent 加入。")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        # 检查是否为自定义指令的简写调用（例如输入 /hello 且已定义 hello）
        if text.startswith("/"):
            parts = text[1:].split()
            cmd_name = parts[0]
            if cmd_name in self.custom_framework.commands:
                res = self.custom_framework.execute_custom(cmd_name, parts[1:])
                await update.message.reply_text(res)
                return

        # 默认艺术辅导
        await self._execute_art_task(update, "art_tutor", "get_theory", concept=text)

    async def _execute_art_task(self, update: Update, skill: str, tool: str, **kwargs):
        try:
            await update.message.reply_chat_action("typing")
            result = await asyncio.to_thread(self.gateway.skill_manager.execute, skill, tool, **kwargs)
            res_text = f"💡 *建议：*\n\n{result}" if skill == "art_tutor" else str(result)
            await update.message.reply_text(res_text, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ 错误：{str(e)}")

    def run(self):
        logger.info("Artfish Studio Bot v2.0 is starting...")
        self.app.run_polling()

if __name__ == "__main__":
    TOKEN = settings.TELEGRAM_BOT_TOKEN or "8434211814:AAFUTWoELMEIio7O8zkKo9siFp233MUQt2A"
    bot = ArtfishStudioBot(TOKEN)
    bot.run()
