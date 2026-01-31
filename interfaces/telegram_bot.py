import logging
import asyncio
from typing import Optional
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
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
logger = logging.getLogger(__name__)

class EduSenseBot:
    """
    EduSense Telegram Bot: 基于 Gateway 的教育垂直场景机器人
    """
    def __init__(self, token: str):
        self.token = token
        self.gateway = Gateway()
        self.app = ApplicationBuilder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """配置指令与消息处理器"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("tutor", self.tutor_command))
        self.app.add_handler(CommandHandler("exam", self.exam_command))
        self.app.add_handler(CommandHandler("writing", self.writing_command))
        
        # 处理普通文本消息
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 指令"""
        user = update.effective_user
        welcome_msg = (
            f"你好 {user.first_name}！🎓 我是 EduSense AI 助教。\n\n"
            "我可以为你提供以下服务：\n"
            "1. 💡 /tutor <问题> - 启发式学科辅导\n"
            "2. 📝 /exam <知识点> - 智能测评练习\n"
            "3. ✍️ /writing <内容> - 作文智能批改\n\n"
            "请直接发送你的问题或使用指令开始学习！"
        )
        await update.message.reply_text(welcome_msg)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 指令"""
        help_text = (
            "📖 EduSense 使用指南：\n\n"
            "• 直接发送数学题或学科名词进行辅导。\n"
            "• 使用 /exam 勾股定理 进行针对性练习。\n"
            "• 使用 /writing <作文内容> 获取批改建议。\n\n"
            "如有疑问，请随时咨询。"
        )
        await update.message.reply_text(help_text)

    async def tutor_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /tutor 指令"""
        query = " ".join(context.args)
        if not query:
            await update.message.reply_text("请输入你想了解的知识点，例如：/tutor 勾股定理")
            return
        
        await self._process_edu_task(update, "tutor", query)

    async def exam_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /exam 指令"""
        kp = " ".join(context.args)
        if not kp:
            await update.message.reply_text("请输入知识点名称，例如：/exam 拟人")
            return
        
        await self._process_edu_task(update, "exam", kp)

    async def writing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /writing 指令"""
        content = " ".join(context.args)
        if not content:
            await update.message.reply_text("请在指令后输入作文内容。")
            return
        
        await self._process_edu_task(update, "writing", content)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通文本消息，自动路由"""
        text = update.message.text
        # 默认使用智能助教模式
        await self._process_edu_task(update, "tutor", text)

    async def _process_edu_task(self, update: Update, mode: str, content: str):
        """统一调用 Gateway 处理教学任务"""
        try:
            # 发送正在思考的状态
            await update.message.reply_chat_action("typing")
            
            # 构建意图
            intent = ArtIntent(
                goals=[content],
                constraints={"style": "educational", "mode": mode}
            )
            
            # 执行
            # 注意：由于 Gateway 可能是同步的，在生产环境建议放入线程池
            loop = asyncio.get_event_loop()
            trace = await loop.run_in_executor(None, self.gateway.execute_intent, intent)
            
            # 格式化回复
            response = self._format_response(trace, mode)
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing TG task: {e}")
            await update.message.reply_text(f"抱歉，处理您的请求时出现错误：{str(e)}")

    def _format_response(self, trace, mode: str) -> str:
        """将执行轨迹格式化为友好的用户回复"""
        results = trace.get_all_results()
        
        if mode == "tutor":
            # 查找启发式回答
            for action_id, result in results.items():
                if "heuristic_tutor" in action_id:
                    return f"💡 *EduSense 启发式引导：*\n\n{result}"
            return "未能找到相关的辅导信息。"
            
        elif mode == "exam":
            for action_id, result in results.items():
                if "generate_quiz" in action_id:
                    q = result.get("question", {})
                    return (
                        f"📝 *针对性练习题：*\n\n"
                        f"{q.get('q', '暂无题目')}\n\n"
                        f"🏷️ 标签: {', '.join(q.get('tags', []))}\n"
                        f"⭐ 难度: {q.get('level', 1)}"
                    )
            return "未能生成练习题。"
            
        elif mode == "writing":
            rhetoric = {}
            suggestion = ""
            for action_id, result in results.items():
                if "detect_rhetoric" in action_id:
                    rhetoric = result
                if "evaluate_structure" in action_id:
                    suggestion = result.get("suggestion", "")
            
            resp = "✍️ *作文批改建议：*\n\n"
            if rhetoric:
                resp += "*修辞识别：*\n"
                for style, matches in rhetoric.items():
                    resp += f"- {style}: {', '.join(matches)}\n"
                resp += "\n"
            
            if suggestion:
                resp += f"*结构评价：*\n{suggestion}"
                
            return resp
            
        return "任务已完成。"

    def run(self):
        """启动机器人"""
        logger.info("EduSense Telegram Bot is starting...")
        self.app.run_polling()

if __name__ == "__main__":
    if not settings.TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
    else:
        bot = EduSenseBot(settings.TELEGRAM_BOT_TOKEN)
        bot.run()
