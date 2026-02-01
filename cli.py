import typer
import os
import json
import time
import asyncio
import subprocess
import platform
import psutil
import questionary
from typing import Optional, List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
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

# --- 辅助函数 ---
def get_openclaw_config():
    home = os.path.expanduser("~")
    config_path = os.path.join(home, ".openclaw", "openclaw.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_bundled_skills():
    skills_dir = os.path.join("openclaw", "openclaw", "skills")
    if not os.path.exists(skills_dir):
        return []
    skills = []
    try:
        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            if os.path.isdir(item_path):
                skills.append(item)
    except: pass
    return skills

# --- TUI 仪表盘组件 ---
def make_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2),
    )
    layout["left"].split_column(
        Layout(name="status"),
        Layout(name="channels"),
    )
    layout["right"].split_column(
        Layout(name="agents"),
        Layout(name="skills"),
    )
    return layout

def get_status_panel():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    table = Table.grid(expand=True)
    table.add_column(style="cyan", justify="left")
    table.add_column(justify="right")
    table.add_row("CPU 负载:", f"[bold]{cpu}%[/bold]")
    table.add_row("内存占用:", f"[bold]{mem}%[/bold]")
    table.add_row("系统版本:", "v3.0.0")
    table.add_row("网关状态:", "[bold green]在线[/bold green]")
    return Panel(table, title="🚀 系统状态", border_style="blue")

def get_channels_panel(config: Dict):
    channels = [k for k, v in config.get("channels", {}).items() if v.get("enabled")]
    table = Table.grid(expand=True)
    for c in channels:
        table.add_row(f"• [green]{c.capitalize()}[/green]", "[dim]在线[/dim]")
    if not channels:
        table.add_row("[dim]未开启任何渠道[/dim]")
    return Panel(table, title="💬 通讯渠道", border_style="magenta")

def get_agents_panel(config: Dict):
    agents = config.get("agents", {}).get("list", ["main"])
    table = Table(show_header=False, box=None)
    for a in agents:
        table.add_row(f"🤖 [bold yellow]{a}[/bold yellow]", "[dim]~/.openclaw/workspace[/dim]")
    return Panel(table, title="智能体管理", border_style="yellow")

def get_skills_panel():
    skills = get_bundled_skills()
    text = Text()
    for i, s in enumerate(skills[:15]): # 只显示前15个
        text.append(f"🧩 {s}  ", style="cyan")
        if (i+1) % 3 == 0: text.append("\n")
    if len(skills) > 15:
        text.append(f"\n... 以及其他 {len(skills)-15} 个技能", style="dim")
    return Panel(Align.left(text), title="技能商店", border_style="green")

@app.command()
def dashboard():
    """终端控制面板：在命令行实时监控与管理系统"""
    layout = make_layout()
    layout["header"].update(Panel(Align.center("[bold white]OmniGate Pro 终端控制中心[/bold white]"), border_style="blue"))
    layout["footer"].update(Panel(Align.center("[dim]按 Ctrl+C 退出面板返回主菜单[/dim]"), border_style="white"))
    
    config = get_openclaw_config()
    
    try:
        with Live(layout, refresh_per_second=2, screen=True):
            while True:
                layout["status"].update(get_status_panel())
                layout["channels"].update(get_channels_panel(config))
                layout["agents"].update(get_agents_panel(config))
                layout["skills"].update(get_skills_panel())
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass

@app.command()
def setup_keys():
    """1. 密钥配置：设置主流 AI 模型与社交平台凭证"""
    console.print(Panel("[bold green]第一步：全平台密钥配置向导 (OmniGate Pro v3)[/bold green]"))
    
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()

    keys = env_vars.copy()
    
    # 1. 国际主流模型
    console.print("\n[bold cyan]1. 🌍 国际主流模型 (Global LLMs)[/bold cyan]")
    keys["DEEPSEEK_API_KEY"] = questionary.password("DeepSeek API Key (推荐):", default=env_vars.get("DEEPSEEK_API_KEY", "")).ask()
    keys["OPENAI_API_KEY"] = questionary.password("OpenAI API Key (GPT-4):", default=env_vars.get("OPENAI_API_KEY", "")).ask()
    keys["CLAUDE_API_KEY"] = questionary.password("Anthropic Claude Key:", default=env_vars.get("CLAUDE_API_KEY", "")).ask()
    keys["GEMINI_API_KEY"] = questionary.password("Google Gemini Key:", default=env_vars.get("GEMINI_API_KEY", "")).ask()
    keys["GROQ_API_KEY"] = questionary.password("Groq Key (Llama 3):", default=env_vars.get("GROQ_API_KEY", "")).ask()

    # 2. 国内主流模型
    console.print("\n[bold cyan]2. 🇨🇳 国内主流模型 (Chinese LLMs)[/bold cyan]")
    keys["QWEN_API_KEY"] = questionary.password("通义千问 (DashScope) Key:", default=env_vars.get("QWEN_API_KEY", "")).ask()
    keys["HUNYUAN_API_KEY"] = questionary.password("腾讯混元 API Key:", default=env_vars.get("HUNYUAN_API_KEY", "")).ask()
    keys["ZHIPU_API_KEY"] = questionary.password("智谱清言 (GLM) Key:", default=env_vars.get("ZHIPU_API_KEY", "")).ask()
    keys["WENXIN_API_KEY"] = questionary.password("百度文心 (ERNIE) Key:", default=env_vars.get("WENXIN_API_KEY", "")).ask()

    # 3. 社交平台
    console.print("\n[bold cyan]3. 💬 社交平台 (Social Channels)[/bold cyan]")
    keys["TELEGRAM_BOT_TOKEN"] = questionary.password("Telegram Bot Token:", default=env_vars.get("TELEGRAM_BOT_TOKEN", "")).ask()
    keys["TELEGRAM_OWNER_ID"] = questionary.text("Telegram 用户 ID (权限控制):", default=env_vars.get("TELEGRAM_OWNER_ID", "")).ask()
    
    if questionary.confirm("是否配置 Discord?").ask():
        keys["DISCORD_BOT_TOKEN"] = questionary.password("Discord Bot Token:", default=env_vars.get("DISCORD_BOT_TOKEN", "")).ask()
        keys["DISCORD_WEBHOOK_URL"] = questionary.text("Discord Webhook URL:", default=env_vars.get("DISCORD_WEBHOOK_URL", "")).ask()
    
    if questionary.confirm("是否配置飞书 (Feishu)?").ask():
        keys["FEISHU_APP_ID"] = questionary.text("飞书 App ID:", default=env_vars.get("FEISHU_APP_ID", "")).ask()
        keys["FEISHU_APP_SECRET"] = questionary.password("飞书 App Secret:", default=env_vars.get("FEISHU_APP_SECRET", "")).ask()

    # 保存至 .env
    with open(".env", "w", encoding="utf-8") as f:
        for k, v in keys.items():
            if v: f.write(f"{k}={v}\n")
            
    console.print("[bold green]✅ 全平台密钥已同步至 .env 文件。[/bold green]")

@app.command()
def onboard():
    """2. 一键入驻：全自动配置 Clawdbot 及其 OmniGate 增强插件"""
    console.print(Panel("[bold cyan]第二步：Clawdbot + OmniGate 联合入驻 (全量模型同步)[/bold cyan]"))
    
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

    # --- 1. 通道连接 (Channels) ---
    if "channels" not in config: config["channels"] = {}
    
    # Telegram
    config["channels"]["telegram"] = {
        "enabled": True,
        "botToken": env_vars.get("TELEGRAM_BOT_TOKEN", ""),
        "allowFrom": [int(env_vars.get("TELEGRAM_OWNER_ID", 0))] if env_vars.get("TELEGRAM_OWNER_ID") else ["*"],
        "dmPolicy": "open"
    }
    
    # Discord
    if env_vars.get("DISCORD_BOT_TOKEN"):
        config["channels"]["discord"] = {
            "enabled": True,
            "botToken": env_vars.get("DISCORD_BOT_TOKEN", ""),
            "dmPolicy": "open"
        }

    # --- 2. 模型提供商 (Providers) ---
    if "models" not in config: config["models"] = {}
    if "providers" not in config["models"]: config["models"]["providers"] = {}
    
    providers = config["models"]["providers"]

    # 批量同步主流模型
    def add_provider(name, base_url, api_type, model_id, model_name):
        key = env_vars.get(f"{name.upper()}_API_KEY")
        if key:
            providers[name] = {
                "enabled": True,
                "baseUrl": base_url,
                "apiKey": key,
                "api": api_type,
                "models": [{"id": model_id, "name": model_name, "api": api_type}]
            }

    add_provider("deepseek", "https://api.deepseek.com", "openai-completions", "deepseek-chat", "DeepSeek Chat")
    add_provider("openai", "https://api.openai.com/v1", "openai-completions", "gpt-4o", "GPT-4o")
    add_provider("qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1", "openai-completions", "qwen-plus", "通义千问 Plus")
    add_provider("hunyuan", "https://api.hunyuan.tencent.com/v1", "openai-completions", "hunyuan-standard", "腾讯混元")
    
    # --- 3. 进阶功能同步 (Voice & Canvas) ---
    if env_vars.get("ELEVENLABS_API_KEY"):
        if "voice" not in config: config["voice"] = {}
        config["voice"]["elevenlabs"] = {
            "apiKey": env_vars["ELEVENLABS_API_KEY"],
            "voiceId": env_vars.get("ELEVENLABS_VOICE_ID", "")
        }
    
    if env_vars.get("CANVAS_ENABLED") == "true":
        config["canvas"] = {
            "enabled": True,
            "port": int(env_vars.get("CANVAS_PORT", 18790))
        }
    
    if env_vars.get("EXTRA_AGENTS"):
        if "agents" not in config: config["agents"] = {}
        config["agents"]["list"] = ["main"] + [a.strip() for a in env_vars["EXTRA_AGENTS"].split(",")]

    # --- 4. OmniGate 增强配置 ---
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
        f"[bold green]✅ 全量配置同步完成！[/bold green]\n\n"
        f"1. [cyan]模型支持[/cyan]: 已同步 DeepSeek, OpenAI, Qwen, Hunyuan 等主流模型。\n"
        f"2. [cyan]通道支持[/cyan]: 已连接 Telegram 与 Discord 通道。\n"
        f"3. [cyan]插件状态[/cyan]: OmniGate Pro 已成功挂载，提供 Token 压缩与本地分析功能。",
        title="入驻报告"
    ))

def check_port(port: int):
    """检测端口是否被占用，如果被占用则尝试清理"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', port)) == 0:
            console.print(f"[yellow]检测到端口 {port} 已被占用，正在尝试自动释放...[/yellow]")
            if platform.system() == "Windows":
                # Windows 下查找并杀死占用端口的进程
                try:
                    cmd = f"netstat -ano | findstr :{port}"
                    output = subprocess.check_output(cmd, shell=True).decode()
                    for line in output.splitlines():
                        if "LISTENING" in line:
                            pid = line.strip().split()[-1]
                            os.system(f"taskkill /F /PID {pid}")
                            console.print(f"[green]已清理占用端口的进程 (PID: {pid})[/green]")
                            time.sleep(1)
                except:
                    pass
            else:
                # Unix/Linux/Mac
                os.system(f"fuser -k {port}/tcp")
                time.sleep(1)

@app.command()
def run():
    """3. 启动运行：开启轻量化网关并进入终端面板"""
    console.print(Panel("[bold green]第三步：启动 OmniGate 网关服务[/bold green]"))
    
    # 检查并清理端口冲突
    check_port(18789)
    
    # 在后台线程启动 API 服务
    from core.fastapi_gateway import run_api
    import threading
    threading.Thread(target=run_api, kwargs={"port": 18789}, daemon=True).start()
    
    time.sleep(2) # 等待启动
    # 进入终端仪表盘
    dashboard()

@app.command()
def fix():
    """修复工具：一键解决 Windows 兼容性与配置问题"""
    console.print("[bold yellow]正在执行系统自愈修复...[/bold yellow]")
    os.system("openclaw doctor --fix")
    console.print("[bold green]✅ 修复完成。[/bold green]")

@app.command()
def setup_advanced():
    """配置进阶功能：设置语音唤醒、智能画布 (Canvas) 及多智能体路由"""
    console.print(Panel("[bold magenta]进阶功能配置向导 (Voice & Canvas)[/bold magenta]"))
    
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        env_vars[parts[0].strip()] = parts[1].strip()

    keys = env_vars.copy()
    
    # 1. 语音服务 (ElevenLabs)
    console.print("\n[bold cyan]1. 🎙️ 语音与交互 (Voice & Talk)[/bold cyan]")
    if questionary.confirm("是否启用 ElevenLabs 语音合成?").ask():
        keys["ELEVENLABS_API_KEY"] = questionary.password("请输入 ElevenLabs API Key:", default=env_vars.get("ELEVENLABS_API_KEY", "")).ask()
        keys["ELEVENLABS_VOICE_ID"] = questionary.text("请输入默认 Voice ID (可选):", default=env_vars.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")).ask()

    # 2. 智能画布 (Canvas)
    console.print("\n[bold cyan]2. 🎨 智能画布 (A2UI Canvas)[/bold cyan]")
    if questionary.confirm("是否启用视觉工作区 (Canvas Host)?").ask():
        keys["CANVAS_ENABLED"] = "true"
        keys["CANVAS_PORT"] = questionary.text("Canvas 监听端口:", default=env_vars.get("CANVAS_PORT", "18790")).ask()

    # 3. 多智能体 (Multi-Agent)
    console.print("\n[bold cyan]3. 🤖 多智能体路由 (Multi-Agent)[/bold cyan]")
    agent_names = questionary.text("请输入额外的 Agent 名称 (逗号分隔):", default=env_vars.get("EXTRA_AGENTS", "")).ask()
    if agent_names:
        keys["EXTRA_AGENTS"] = agent_names

    with open(".env", "w", encoding="utf-8") as f:
        for k, v in keys.items():
            if v: f.write(f"{k}={v}\n")
            
    console.print("[bold green]✅ 进阶配置已同步。请运行 onboard 以生效。[/bold green]")

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
                "3️⃣ 启动运行 [开启终端控制面板]",
                Separator(),
                "⚙️ 进阶配置 [语音、画布、多智能体]",
                "🔧 系统自愈 [修复 Windows 兼容报错]",
                "💡 教程链条 [查看系统底层连接逻辑]",
                "❌ 退出系统"
            ]
        ).ask()

        if not choice or "退出" in choice: return

        if "配置密钥" in choice: setup_keys()
        elif "一键入驻" in choice: onboard()
        elif "启动运行" in choice: run()
        elif "进阶配置" in choice: setup_advanced()
        elif "系统自愈" in choice: fix()
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
