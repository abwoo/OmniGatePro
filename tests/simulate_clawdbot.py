import asyncio
import json
from core.api_engine import api_engine
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class ClawdbotMasterSimulation:
    """
    模拟 Clawdbot 主控程序的工作逻辑。
    演示如何通过指针调度 OmniGate 插件。
    """
    def __init__(self):
        # 模拟 Clawdbot 的配置文件
        self.config = {
            "name": "Clawdbot-Master",
            "plugins": {
                "local_executor": "clawdbot.offload",
                "optimizer": "clawdbot.shrink"
            }
        }
        self.history = []

    async def handle_user_query(self, user_input: str):
        console.print(f"\n[bold blue]用户消息:[/bold blue] {user_input}")
        
        # 1. 模拟逻辑判断：是否为本地执行任务
        if any(keyword in user_input for keyword in ["运行", "执行", "RUN:", "文件", "读取"]):
            console.print("[dim]Master: 检测到本地任务，正在卸载给 OmniGate 插件...[/dim]")
            pointer = self.config["plugins"]["local_executor"]
            res = await api_engine.execute(pointer, task=user_input)
            
            if res.status == "success":
                console.print(Panel(str(res.data), title="OmniGate 本地执行反馈", border_style="green"))
            else:
                console.print(f"[red]错误: {res.error}[/red]")

        # 2. 模拟 Token 优化判断：历史记录过长
        if len(self.history) > 3:
            console.print("[dim]Master: 对话过长，正在调用 OmniGate 进行 Token 压缩...[/dim]")
            pointer = self.config["plugins"]["optimizer"]
            ctx = "\n".join(self.history)
            res = await api_engine.execute(pointer, context=ctx)
            
            if res.status == "success":
                compressed = res.data["summary"]
                console.print(f"[green]Token 已节省！压缩后的上下文摘要: {compressed}[/green]")
                self.history = [compressed] # 替换为摘要，节省云端 Token

        # 3. 记录到历史
        self.history.append(f"User: {user_input}")

async def run_test_suite():
    console.print(Panel.fit("Clawdbot x OmniGate 深度集成测试 (模拟环境)", style="bold white on magenta"))
    master = ClawdbotMasterSimulation()

    # 测试场景 1: 本地命令执行
    await master.handle_user_query("RUN: echo '集成测试开始'")
    
    # 测试场景 2: 文件读取
    await master.handle_user_query("帮我读取一下 README.md 的内容")

    # 测试场景 3: 模拟长对话触发 Token 优化
    queries = [
        "你好",
        "你是谁？",
        "你能做什么？",
        "告诉我今天的日期"
    ]
    for q in queries:
        await master.handle_user_query(q)

if __name__ == "__main__":
    asyncio.run(run_test_suite())
