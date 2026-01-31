import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

# 路径修复
sys.path.append(os.getcwd())

from core.orchestrator_pro import discussion_room, multimodal_creator
from core.gateway_pro import pro_gateway

console = Console()

async def demo_discussion():
    console.print(Panel("[bold cyan]场景 1: 多智能体艺术讨论室 (Collaborative Discussion)[/bold cyan]"))
    prompt = "如何将中国传统水墨画与赛博朋克视觉风格融合？"
    console.print(f"[bold]讨论主题:[/bold] {prompt}\n")
    
    with console.status("[bold yellow]正在召集专家 Agent 进行讨论...") as status:
        dialogue = await discussion_room.start_session("demo_user", prompt)
        
    # 格式化输出对话
    for line in dialogue.split("\n\n"):
        if "Agent" in line:
            console.print(Panel(line, border_style="blue"))
        else:
            console.print(line)

async def demo_debate():
    console.print(Panel("[bold magenta]场景 2: 专家学术辩论 (Expert Debate)[/bold magenta]"))
    topic = "AI 生成艺术是否剥夺了人类艺术家的原创性？"
    console.print(f"[bold]辩论主题:[/bold] {topic}\n")
    
    with console.status("[bold red]正在启动正反方辩论流...") as status:
        res = await pro_gateway.handle_request("demo_user", "debate", {"topic": topic})
    
    if res["status"] == "success":
        for i, speech in enumerate(res["data"]):
            role = "正方 (Pro)" if i == 0 else "反方 (Con)"
            color = "green" if i == 0 else "red"
            console.print(Panel(speech, title=role, border_style=color))

async def demo_multimodal():
    console.print(Panel("[bold green]场景 3: 协同创作工作流 (Creative Workflow)[/bold green]"))
    theme = "失落的亚特兰蒂斯"
    console.print(f"[bold]创作主题:[/bold] {theme}\n")
    
    with console.status("[bold cyan]Agent 正在协同构思...") as status:
        work = await multimodal_creator.create_collaborative_work(theme)
    
    table = Table(title="协同创作成果清单", box=None)
    table.add_column("环节", style="bold yellow")
    table.add_column("内容", style="dim")
    
    table.add_row("艺术理论 (Tutor)", str(work["theory"]))
    table.add_row("视觉构思 (Artist)", str(work["visual_prompt"]))
    table.add_row("审美优化 (Critic)", str(work["optimization"]))
    
    console.print(table)

async def demo_interaction():
    console.print(Panel("[bold yellow]场景 4: Agent 艺术互动工坊 (Mutual Interaction)[/bold yellow]"))
    topic = "极简主义在未来数字艺术中的地位"
    console.print(f"[bold]互动主题:[/bold] {topic}\n")
    
    with console.status("[bold green]Agent 们正在相互交流灵感...") as status:
        # 启动 2 轮互动，由导师和艺术家参与
        dialogue = await orchestrator.run_interaction(topic, ["tutor", "artist"], rounds=2)
    
    for speech in dialogue:
        console.print(speech)
        await asyncio.sleep(0.5) # 模拟对话停顿

async def main():
    console.print(Panel.fit("Artfish Studio Pro - 本地 Agent 协作演示", style="bold white on blue"))
    
    # 注册 Agent (确保已注册)
    from core.agents.art_agents import TutorAgent, ArtistAgent, CriticAgent
    orchestrator.register_agent(TutorAgent())
    orchestrator.register_agent(ArtistAgent())
    orchestrator.register_agent(CriticAgent())

    await demo_discussion()
    console.print("\n")
    await demo_debate()
    console.print("\n")
    await demo_multimodal()
    console.print("\n")
    await demo_interaction()

if __name__ == "__main__":
    from core.agent import orchestrator
    asyncio.run(main())
