import logging
import asyncio
import json
from typing import Optional, Dict, Any
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
from core.gateway import Gateway
from core.intent import ArtIntent

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("artfish.studio.bot")

class ArtfishStudioBot:
    """
    Artfish Studio Telegram Bot: 支持多 Agent 协作的艺术教育机器人
    """
    def __init__(self, token: str):
        self.token = token
        self.gateway = Gateway()
        self.app = ApplicationBuilder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """配置指令与消息处理器"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("tutor", self.tutor_command))
        self.app.add_handler(CommandHandler("critique", self.critique_command))
        self.app.add_handler(CommandHandler("collaborate", self.collaborate_command))
        
        # 处理回调查询（按钮点击）
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 处理普通文本消息
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 指令"""
        user = update.effective_user
        welcome_msg = (
            f"🎨 你好 {user.first_name}！欢迎来到 Artfish Studio 艺术创作室。\n\n"
            "我是一个支持多智能体协作的艺术助教，你可以：\n"
            "1. 💡 /tutor <概念> - 学习色彩理论或构图法则\n"
            "2. 🔍 /critique <构思> - 获取专业审美点评\n"
            "3. 🤝 /collaborate - 开启多 Agent 协同创作模式\n\n"
            "在这里，你的 AI Agent 可以与其他专家 Agent 共同完成艺术挑战！"
        )
        await update.message.reply_text(welcome_msg)

    async def tutor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """艺术理论辅导"""
        concept = " ".join(context.args) or "色彩理论"
        await self._execute_art_task(update, "art_tutor", "get_theory", concept=concept)

    async def critique_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """作品点评"""
        description = " ".join(context.args)
        if not description:
            await update.message.reply_text("请在指令后输入你的作品构思或描述，例如：/critique 晨曦中的森林")
            return
        await self._execute_art_task(update, "art_critique", "critique_concept", description=description)

    async def collaborate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """开启多 Agent 协作"""
        keyboard = [
            [
                InlineKeyboardButton("🎨 邀请创作 Agent", callback_query_data="invite_artist"),
                InlineKeyboardButton("🧐 邀请评审 Agent", callback_query_data="invite_critic"),
            ],
            [InlineKeyboardButton("✅ 提交至工作台", callback_query_data="submit_project")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🚀 已开启多智能体协同模式。请选择要加入项目的 Agent 角色：", reply_markup=reply_markup)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮点击"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "invite_artist":
            await query.edit_message_text("✅ 创作 Agent [Artist-Bot] 已加入项目。它将负责风格实现。")
        elif query.data == "invite_critic":
            await query.edit_message_text("✅ 评审 Agent [Critic-Bot] 已加入项目。它将负责审美把关。")
        elif query.data == "submit_project":
            await query.edit_message_text("🌟 项目已提交至 Artfish 工作台！多 Agent 协作流正在启动...")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """普通消息路由"""
        text = update.message.text
        # 默认路由到导师技能
        await self._execute_art_task(update, "art_tutor", "get_theory", concept=text)

    async def _execute_art_task(self, update: Update, skill: str, tool: str, **kwargs):
        """执行艺术任务并反馈"""
        try:
            await update.message.reply_chat_action("typing")
            
            # 直接通过 Gateway 的 SkillManager 执行（多 Agent 协作的基础）
            result = self.gateway.skill_manager.execute(skill, tool, **kwargs)
            
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
    # 使用提供的 Token
    TOKEN = "8434211814:AAFUTWoELMEIio7O8zkKo9siFp233MUQt2A"
    bot = ArtfishStudioBot(TOKEN)
    bot.run()
