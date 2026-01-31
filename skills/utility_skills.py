import asyncio
from typing import Dict, Any, Optional
from core.skill import BaseSkill, skill_tool
from core.network import NetworkClient
from core.config import settings

class UtilitySkills(BaseSkill):
    """
    实用工具技能集：天气、汇率、提醒、翻译、文件分析
    """
    name = "utility_skills"
    description = "A collection of practical utility skills like weather, currency, etc."

    def __init__(self):
        super().__init__()
        self.network = NetworkClient()

    @skill_tool(description="查询指定城市的天气状况")
    async def get_weather(self, city: str) -> str:
        # 优先使用配置中的 API Key
        api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
        if not api_key:
            return "❌ 天气服务未配置 API Key。"
        
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        try:
            data = await self.network.get_json(url, params)
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"🌤️ {city}当前天气：{desc}，气温 {temp}°C。"
        except Exception as e:
            return f"❌ 无法获取 {city} 的天气信息：{str(e)}"

    @skill_tool(description="进行实时汇率转换")
    async def currency_convert(self, amount: float, from_curr: str, to_curr: str) -> str:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        try:
            data = await self.network.get_json(url)
            rate = data["rates"].get(to_curr.upper())
            if not rate:
                return f"❌ 未找到目标货币 {to_curr}。"
            
            converted = amount * rate
            return f"💱 {amount} {from_curr.upper()} ≈ {converted:.2f} {to_curr.upper()} (汇率: {rate})"
        except Exception as e:
            return f"❌ 汇率转换失败：{str(e)}"

    @skill_tool(description="设置一个提醒事项")
    async def set_reminder(self, task: str, seconds: int) -> str:
        async def run_reminder():
            await asyncio.sleep(seconds)
            # 提醒逻辑：在实际 Bot 中会触发消息推送
            print(f"🔔 提醒：{task}")

        asyncio.create_task(run_reminder())
        return f"✅ 已为您设置提醒：'{task}'，将在 {seconds} 秒后通知您。"

    @skill_tool(description="翻译指定文本")
    async def translate_text(self, text: str, target_lang: str = "zh") -> str:
        url = f"https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        try:
            data = await self.network.get_json(url, params)
            translated = "".join([part[0] for part in data[0]])
            return f"🌐 翻译结果 ({target_lang})：\n{translated}"
        except Exception as e:
            return f"❌ 翻译失败：{str(e)}"
