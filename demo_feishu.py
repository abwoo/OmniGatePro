import asyncio
import sys
import os
from rich.console import Console
from rich.panel import Panel

# 路径修复
sys.path.append(os.getcwd())

from core.api_engine import api_engine

console = Console()

async def demo_feishu_push():
    console.print(Panel("[bold cyan]场景 4: 跨平台成果推送 (Feishu/Lark Integration)[/bold cyan]"))
    
    # 模拟协作结果
    result_summary = "🎨 Artfish Studio Pro 协作完成：构思了一幅融合水墨与赛博风格的《数字黄山》。"
    
    console.print(f"[bold]待推送内容:[/bold] {result_summary}\n")
    
    with console.status("[bold green]正在通过指针调用 feishu.send_text...") as status:
        res = await api_engine.execute("feishu.send_text", 
                                       receive_id="art_group_001", 
                                       content=result_summary)
    
    if res.status == "success":
        console.print(f"✅ [bold green]推送成功![/bold green] 返回数据: {res.data}")
    else:
        console.print(f"❌ [bold red]推送失败:[/bold red] {res.error}")

if __name__ == "__main__":
    asyncio.run(demo_feishu_push())
