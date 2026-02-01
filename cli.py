import typer
import os
import json
import time
import asyncio
import subprocess
import platform
import psutil
import questionary
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from questionary import Separator

app = typer.Typer(help="OmniGate Pro - Clawdbot 轻量化核心增强插件")
console = Console()

# --- 核心逻辑说明 ---
# 教程链条 (Tutorial Chain):
# 1. DeepSeek API -> 提供推理大脑 (LLM)
# 2. Telegram Bot -> 提供交互界面 (UI)
# 3. OmniGate Pro -> 作为 Clawdbot 插件，实现:
#    - [网关功能] 桥接 DeepSeek 与 Telegram
#    - [Token 压缩] 自动精简上下文，大幅降低 API 费用
#    - [本地卸载] 让 Clawdbot 具备执行本地 Shell 指令的能力

@app.command()
def setup_keys():
    """1. 密钥配置：设置 DeepSeek、Telegram 及其他社交平台凭证"""
    console.print(Panel("[bold green]第一步：全平台密钥配置向导[/bold green]"))
    
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()

    keys = {}
    console.print("\n[bold]1. 大模型核心 (DeepSeek)[/bold]")
    keys["DEEPSEEK_API_KEY"] = questionary.password("请输入 DeepSeek API Key:", default=env_vars.get("DEEPSEEK_API_KEY", "")).ask()
    
    console.print("\n[bold]2. 聊天平台 (多端支持)[/bold]")
    keys["TELEGRAM_BOT_TOKEN"] = questionary.password("请输入 Telegram Bot Token:", default=env_vars.get("TELEGRAM_BOT_TOKEN", "")).ask()
    keys["TELEGRAM_OWNER_ID"] = questionary.text("请输入您的 Telegram 用户 ID (权限锁定):", default=env_vars.get("TELEGRAM_OWNER_ID", "")).ask()
    
    # 扩展：支持 Discord 和 飞书 (OmniGate 独有简化配置)
    if questionary.confirm("是否配置 Discord Bot?").ask():
        keys["DISCORD_BOT_TOKEN"] = questionary.password("请输入 Discord Bot Token:").ask()
    
    if questionary.confirm("是否配置飞书 (Feishu) App?").ask():
        keys["FEISHU_APP_ID"] = questionary.text("请输入飞书 App ID:").ask()
        keys["FEISHU_APP_SECRET"] = questionary.password("请输入飞书 App Secret:").ask()

    with open(".env", "w") as f:
        for k, v in keys.items():
            if v: f.write(f"{k}={v}\n")
            
    console.print("[bold green]✅ 全平台密钥已同步。[/bold green]")

@app.command()
def onboard():
    """2. 一键入驻：全自动配置 Clawdbot 及其 OmniGate 增强插件"""
    console.print(Panel("[bold cyan]第二步：Clawdbot + OmniGate 联合入驻[/bold cyan]"))
    
    if not os.path.exists(".env"):
        setup_keys()
    
    # 读取环境变量
    env_vars = {}
    with open(".env", "r") as f:
        for line in f:
            if "=" in line:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    env_vars[parts[0].strip()] = parts[1].strip()

    # 路径准备
    home = os.path.expanduser("~")
    openclaw_dir = os.path.join(home, ".openclaw")
    workspace_dir = os.path.join(openclaw_dir, "workspace")
    os.makedirs(workspace_dir, exist_ok=True)

    # 读取现有配置
    config_path = os.path.join(openclaw_dir, "openclaw.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            try: config = json.load(f)
            except: config = {}
    else: config = {}

    # --- OpenClaw 基础功能：通道连接 ---
    if "channels" not in config: config["channels"] = {}
    
    # Telegram
    config["channels"]["telegram"] = {
        "enabled": True,
        "botToken": env_vars.get("TELEGRAM_BOT_TOKEN", ""),
        "allowFrom": [int(env_vars.get("TELEGRAM_OWNER_ID", 0))] if env_vars.get("TELEGRAM_OWNER_ID") else ["*"],
        "dmPolicy": "open"
    }
    
    # Discord (OmniGate 自动化同步)
    if env_vars.get("DISCORD_BOT_TOKEN"):
        config["channels"]["discord"] = {
            "enabled": True,
            "botToken": env_vars.get("DISCORD_BOT_TOKEN", ""),
            "dmPolicy": "open"
        }

    # --- OmniGate 核心增强：DeepSeek 优化模型 ---
    if "models" not in config: config["models"] = {}
    if "providers" not in config["models"]: config["models"]["providers"] = {}
    config["models"]["providers"]["deepseek"] = {
        "baseUrl": "https://api.deepseek.com",
        "apiKey": env_vars.get("DEEPSEEK_API_KEY", ""),
        "api": "openai-completions",
        "models": [
            {
                "id": "deepseek-chat", 
                "name": "DeepSeek Chat (Omni Optimized)", 
                "api": "openai-completions",
                "contextWindow": 64000,
                "maxTokens": 4096
            }
        ]
    }

    # --- OmniGate 独有功能：Python MCP 插件注册 ---
    # 这让 Clawdbot 具备了执行本地任务、Token 压缩、深度性能分析的能力
    mcp_config = {
        "mcpServers": {
            "omnigate": {
                "command": "python",
                "args": [os.path.abspath("core/mcp_server.py")],
                "env": {"PYTHONPATH": os.path.abspath(".")}
            }
        }
    }
    mcp_path = os.path.join(workspace_dir, "mcp.json")
    with open(mcp_path, "w", encoding="utf-8") as f:
        json.dump(mcp_config, f, indent=2, ensure_ascii=False)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    console.print(Panel(
        f"[bold green]✅ 联合入驻成功！[/bold green]\n\n"
        f"1. [cyan]Clawdbot[/cyan]: 已连接 Telegram/Discord 通道。\n"
        f"2. [cyan]OmniGate[/cyan]: 已成功挂载 MCP 插件，提供 [bold]Token 压缩[/bold] 与 [bold]Python 工具箱[/bold]。\n"
        f"3. [cyan]DeepSeek[/cyan]: 已优化为默认对话大脑。",
        title="入驻报告"
    ))

@app.command()
def run():
    """3. 启动运行：开启轻量化网关与可视化面板"""
    console.print(Panel("[bold green]第三步：启动 OmniGate 网关服务[/bold green]"))
    
    # 自动打开浏览器
    import webbrowser
    import threading
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:18789")
    threading.Thread(target=open_browser, daemon=True).start()
    
    from core.fastapi_gateway import run_api
    run_api(port=18789)

@app.command()
def fix():
    """修复工具：一键解决 Windows 兼容性与配置问题"""
    console.print("[bold yellow]正在执行系统自愈修复...[/bold yellow]")
    os.system("openclaw doctor --fix")
    console.print("[bold green]✅ 修复完成。[/bold green]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """OmniGate Pro - 标准化流程控制台"""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold white]OmniGate Pro 🦞 Clawdbot 极简插件中心[/bold white]\n"
            "[dim]目标：更轻量、更省钱、更易用[/dim]",
            border_style="blue", expand=False
        ))
        
        choice = questionary.select(
            "请按照 1-2-3 标准化流程操作:",
            choices=[
                "1️⃣ 配置密钥 [设置 DeepSeek/Telegram]",
                "2️⃣ 一键入驻 [关联 Clawdbot 插件系统]",
                "3️⃣ 启动运行 [开启可视化管理面板]",
                Separator(),
                "🔧 系统自愈 [修复 Windows 兼容报错]",
                "💡 教程链条 [查看系统底层连接逻辑]",
                "❌ 退出系统"
            ]
        ).ask()

        if not choice or "退出" in choice: return

        if "配置密钥" in choice: ctx.invoke(setup_keys)
        elif "一键入驻" in choice: ctx.invoke(onboard)
        elif "启动运行" in choice: ctx.invoke(run)
        elif "系统自愈" in choice: ctx.invoke(fix)
        elif "教程链条" in choice:
            console.print(Panel(
                "🔗 [bold]OmniGate Pro 逻辑链接说明[/bold]\n\n"
                "1. [cyan]DeepSeek[/cyan] 是你的 AI 大脑，负责理解指令。\n"
                "2. [cyan]Telegram[/cyan] 是你的手机端入口，负责接收消息。\n"
                "3. [cyan]OmniGate[/cyan] 则是连接两者的『智能中继站』：\n"
                "   - 它会拦截消息，在发送给 DeepSeek 前进行 [bold]Token 压缩[/bold] (省钱)。\n"
                "   - 它会让 DeepSeek 能够调用 [bold]本地工具[/bold] (如运行脚本、查文件)。\n"
                "   - 它通过 [bold]MCP 协议[/bold] 深度嵌入 Clawdbot，使其运行更流程。",
                title="逻辑关系"
            ))
            time.sleep(5)
            ctx.invoke(main)

if __name__ == "__main__":
    app()
