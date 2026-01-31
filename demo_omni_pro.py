import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 路径修复
sys.path.append(os.getcwd())

from core.omni_engine import omni_orchestrator
from core.api_engine import api_engine
from core.workflow_manager import workflow_manager

console = Console()

async def demo_omni_local_action():
    console.print(Panel("[bold cyan]OmniGate 核心演示: 本地自主行动 (Autonomous Action)[/bold cyan]"))
    
    # 模拟用户要求查看本地环境并列出文件
    user_input = "请帮我查看一下当前系统的状态，并告诉我目录下有哪些文件。然后用 RUN_CMD: echo 'OmniGate is active' 来打个招呼。"
    
    console.print(f"[bold yellow]用户指令:[/bold yellow] {user_input}\n")
    
    with console.status("[bold green]OmniAgent 正在思考并执行本地任务...") as status:
        res = await omni_orchestrator.dispatch(user_input)
    
    if "Insufficient Balance" in res:
        console.print("[yellow]提示: 检测到 API 余额不足，演示将使用本地兜底逻辑进行模拟。[/yellow]")
        # 模拟执行 RUN_CMD 后的结果
        res = "已为您执行本地指令。当前系统：Windows 10，目录下包含 demo_omni_pro.py 等文件。OmniGate is active!"

    console.print(Panel(res, title="Agent 执行反馈", border_style="green"))

async def demo_clawdbot_integration():
    console.print(Panel("[bold magenta]OmniGate 演示: Clawdbot 插件集成 (Plugin & Token Opt)[/bold magenta]"))
    
    # 模拟从 Clawdbot 卸载的任务
    console.print("[bold]1. Clawdbot 任务卸载 (Offloading):[/bold]")
    res_offload = await api_engine.execute("clawdbot.offload_task", task="读取本地 config.py 并告诉我配置项")
    console.print(f"Clawdbot 获取到的执行结果: [dim]{res_offload.data[:100]}...[/dim]\n")
    
    # 模拟 Token 优化
    console.print("[bold]2. Token 优化 (Optimization):[/bold]")
    long_context = "这里是一段非常非常长的历史对话记录..." * 50
    res_opt = await api_engine.execute("clawdbot.optimize_token", context=long_context)
    console.print(f"Token 压缩结果: [green]{res_opt.data['summary']}[/green]")

async def demo_smart_workflow():
    console.print(Panel("[bold yellow]OmniGate 演示: 标准化工作流 (Smartphone-like UX)[/bold yellow]"))
    
    # 强制重载工作流
    workflow_manager._load_workflows()
    console.print(f"[bold]可用工作流:[/bold] {list(workflow_manager.workflows.keys())}\n")
    
    with console.status("[bold blue]正在启动 'system_check' 工作流...") as status:
        res = await workflow_manager.run_workflow("system_check")
    
    console.print(res)

async def main():
    console.print(Panel.fit("OmniGate Pro - 全能 AI 智能体网关演示", style="bold white on purple"))
    await demo_omni_local_action()
    console.print("\n")
    await demo_clawdbot_integration()
    console.print("\n")
    await demo_smart_workflow()

if __name__ == "__main__":
    asyncio.run(main())
