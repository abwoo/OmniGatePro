import asyncio
from core.omni_engine import omni_engine
from core.api_engine import api_engine
from rich.console import Console
from rich.panel import Panel

console = Console()

async def main():
    console.print(Panel.fit("OmniGate Pro - Clawdbot 插件验证演示", style="bold white on cyan"))

    # 1. 验证极致轻量化 Token 压缩
    console.print("\n[bold]1. 验证 Token 压缩 (节省成本):[/bold]")
    long_history = "用户: 帮我写个脚本\nAI: 好的，什么脚本？\n用户: Python 的爬虫脚本\nAI: 爬取哪个网站？"
    res_shrink = await api_engine.execute("clawdbot.shrink", context=long_history)
    console.print(f"原始长度: {len(long_history)} | 压缩后摘要: [green]{res_shrink.data['summary']}[/green]")

    # 2. 验证任务卸载 (本地执行)
    console.print("\n[bold]2. 验证任务卸载 (本地行动):[/bold]")
    # 模拟 Clawdbot 将“读取 config.py”的任务卸载给 OmniGate
    res_offload = await api_engine.execute("clawdbot.offload", task="RUN: echo 'Hello from Local Device'")
    console.print(f"本地执行结果: [yellow]{res_offload.data}[/yellow]")

    # 3. 验证智能手机级交互
    console.print("\n[bold]3. 验证极简交互逻辑:[/bold]")
    res_simple = await omni_engine.execute_task("帮我看看当前目录下有什么")
    console.print(f"Omni 响应: {res_simple[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
