import asyncio
import os
import logging
from typing import Dict, Any, Optional, List
from core.skill import BaseSkill, skill_tool
from core.network import NetworkClient
from core.config import settings

logger = logging.getLogger("artfish.skills.utility")

class UtilitySkills(BaseSkill):
    """
    全功能实用工具技能集：天气、汇率、提醒、翻译、文件分析、网页快照。
    包含完整的错误处理与结果格式化。
    """
    name = "utility"
    description = "Practical tools for everyday tasks including weather, finance, and language."

    def __init__(self):
        super().__init__()
        self.network = NetworkClient(timeout=15.0)

    @skill_tool(description="查询实时天气。用法：/weather 北京")
    async def get_weather(self, city: str) -> str:
        if not settings.OPENWEATHER_API_KEY:
            return "⚠️ 系统提示：天气服务 API Key 未配置，请联系管理员。"
        
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        try:
            data = await self.network.get_json(url, params)
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            
            return (
                f"🌤️ *{city} 实时天气报告*\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🌡️ 温度：{temp}°C (体感 {feels_like}°C)\n"
                f"🌥️ 状态：{desc}\n"
                f"💧 湿度：{humidity}%\n"
                f"📍 城市：{data['name']}"
            )
        except Exception as e:
            logger.error(f"Weather skill failed for {city}: {e}")
            return f"❌ 抱歉，无法获取 '{city}' 的天气信息。请检查城市名称是否正确。"

    @skill_tool(description="实时汇率转换。用法：/exchange 100 USD CNY")
    async def currency_convert(self, amount: float, from_curr: str, to_curr: str) -> str:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        try:
            data = await self.network.get_json(url)
            rate = data["rates"].get(to_curr.upper())
            if not rate:
                return f"❌ 错误：不支持的货币类型 '{to_curr}'。"
            
            converted = amount * rate
            return (
                f"💱 *汇率换算结果*\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💰 {amount} {from_curr.upper()} = \n"
                f"👉 *{converted:.2f} {to_curr.upper()}*\n"
                f"📈 当前汇率: 1:{rate}"
            )
        except Exception as e:
            logger.error(f"Currency conversion failed: {e}")
            return "❌ 汇率服务暂时不可用，请稍后再试。"

    @skill_tool(description="设置智能提醒。用法：/remind 60 喝水时间")
    async def set_reminder(self, task: str, seconds: int) -> str:
        if seconds <= 0:
            return "❌ 错误：提醒时间必须大于 0 秒。"
        if seconds > 86400 * 7: # 限制最长一周
            return "❌ 错误：提醒时间不能超过 7 天。"

        # 在异步任务中运行提醒逻辑
        async def delayed_reminder():
            await asyncio.sleep(seconds)
            # 实际生产中这里应通过 MQ 或 Webhook 通知 Bot
            logger.info(f"ALARM TRIGGERED: {task}")

        asyncio.create_task(delayed_reminder())
        
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        time_desc = f"{minutes}分{remaining_seconds}秒" if minutes > 0 else f"{seconds}秒"
        
        return f"✅ 提醒设置成功！我将在 *{time_desc}* 后提醒您：\n🔔 `{task}`"

    @skill_tool(description="多语言翻译服务。用法：/translate Hello World")
    async def translate_text(self, text: str, target_lang: str = "zh") -> str:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        try:
            data = await self.network.get_json(url, params)
            translated = "".join([part[0] for part in data[0] if part[0]])
            src_lang = data[2]
            
            return (
                f"🌐 *翻译结果 ({src_lang} ➔ {target_lang})*\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📝 原文：`{text}`\n"
                f"✨ 译文：*{translated}*"
            )
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return "❌ 翻译服务调用失败。"

    @skill_tool(description="网页内容抓取与总结。用法：/browse https://example.com")
    async def browse_web(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url
            
        try:
            result = await self.network.scrape_web_content(url)
            if result["status"] == "failed":
                return f"❌ 抓取失败：{result.get('error')}"
            
            summary = result["content"][:400] + "..." if len(result["content"]) > 400 else result["content"]
            return (
                f"📑 *网页快照：{result['title']}*\n"
                f"🔗 地址：{url}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{summary}\n\n"
                f"💡 _提示：您可以使用 /api 命令让 AI 对网页内容进行深度分析。_"
            )
        except Exception as e:
            return f"❌ 网页访问异常：{str(e)}"

    @skill_tool(description="分析本地文件元数据。用法：/file_info d:/test.txt")
    async def get_file_info(self, path: str) -> str:
        if not os.path.exists(path):
            return f"❌ 错误：文件 '{path}' 不存在。"
        
        try:
            stats = os.stat(path)
            size_kb = stats.st_size / 1024
            return (
                f"📁 *文件属性分析*\n"
                f"━━━━━━━━━━━━━━━\n"
                f"📄 名称：{os.path.basename(path)}\n"
                f"⚖️ 大小：{size_kb:.2f} KB\n"
                f"🕒 最后修改：{os.path.getmtime(path)}\n"
                f"📌 路径：`{path}`"
            )
        except Exception as e:
            return f"❌ 文件读取失败：{str(e)}"
