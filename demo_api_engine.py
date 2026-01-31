import asyncio
import sys
import os

# 路径修复
sys.path.append(os.getcwd())

from core.api_engine import api_engine
from core.adapters.base import BaseAdapter, APIResponse

async def demo():
    console = Console()
    console.print(Panel("[bold cyan]Artfish Universal API Engine - Pointer Invocation Demo[/bold cyan]"))

    # 1. Simulate Telegram Call
    console.print("\n[bold]1. Simulating Pointer: [magenta]telegram.sendMessage[/magenta][/bold]")
    res_tg = await api_engine.execute("telegram.sendMessage", chat_id="demo_user", text="Greetings from Artfish Engine!")
    status_color = "green" if res_tg.status == "success" else "red"
    console.print(f"Status: [{status_color}]{res_tg.status}[/{status_color}]")
    if res_tg.error:
        console.print(f"Details: [dim]{res_tg.error}[/dim] (Expected if token/chat_id is invalid)")

    # 2. Simulate Discord Call
    console.print("\n[bold]2. Simulating Pointer: [magenta]discord.execute_webhook[/magenta][/bold]")
    res_dc = await api_engine.execute("discord.execute_webhook", 
                                      webhook_url="https://discord.com/api/webhooks/fake_id/fake_token", 
                                      content="Engine Alert Test")
    console.print(f"Status: [yellow]{res_dc.status}[/yellow]")
    console.print(f"Payload: {res_dc.data}")

    # 3. Dynamic Adapter Registration
    console.print("\n[bold]3. Dynamic Adapter Registration: [magenta]custom_ai[/magenta][/bold]")
    
    class CustomAIAdapter(BaseAdapter):
        @property
        def name(self) -> str: return "custom_ai"
        async def call(self, method, **kwargs):
            return APIResponse(status="success", data=f"Custom AI processed '{method}' with {kwargs}")

    api_engine.register_adapter(CustomAIAdapter())
    
    res_custom = await api_engine.execute("custom_ai.analyze_style", image="masterpiece.jpg")
    console.print(f"Result: [green]{res_custom.data}[/green]")

if __name__ == "__main__":
    from rich.console import Console
    from rich.panel import Panel
    asyncio.run(demo())
