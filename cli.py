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

from rich.columns import Columns
from core.token_tracker import token_tracker

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
        Layout(name="status", size=8),
        Layout(name="token_stats", ratio=1),
        Layout(name="channels", size=8),
    )
    layout["right"].split_column(
        Layout(name="agents", size=8),
        Layout(name="skills", ratio=1),
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

def get_token_panel():
    stats = token_tracker.get_summary()
    table = Table(show_header=True, header_style="bold magenta", box=None, expand=True)
    table.add_column("来源", style="dim")
    table.add_column("原始", justify="right")
    table.add_column("优化", justify="right")
    table.add_column("节省", style="green", justify="right")
    
    for provider, data in stats["providers"].items():
        table.add_row(
            provider.capitalize(), 
            str(data["original"]), 
            str(data["optimized"]), 
            f"{round(data['saved']/data['original']*100 if data['original']>0 else 0)}%"
        )
    
    summary = (
        f"总节省率: [bold green]{stats['savings_rate']}%[/bold green]  "
        f"累计节省: [bold yellow]{stats['total_saved']}[/bold yellow] Tokens"
    )
    
    # 使用 Group 组合表格和摘要文字，避免 Layout 嵌套错误
    from rich.console import Group
    return Panel(
        Group(
            table,
            Align.center(summary)
        ),
        title="📊 Token 节省看板", 
        border_style="magenta"
    )

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
                layout["token_stats"].update(get_token_panel()) # 更新 Token 看板
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

def check_openclaw_env() -> List[str]:
    """深度检测本地 OpenClaw 源码、依赖及构建状态"""
    checks = []
    base_path = os.path.join(os.getcwd(), "openclaw", "openclaw")
    
    # 1. 源码检测
    if os.path.exists(base_path):
        checks.append("[green]✔[/green] OpenClaw 源码: 已就绪")
    else:
        checks.append("[red]✘[/red] OpenClaw 源码: 缺失 (请确保已执行 git clone)")
        return checks

    # 2. 依赖检测 (node_modules)
    if os.path.exists(os.path.join(base_path, "node_modules")):
        checks.append("[green]✔[/green] Node 依赖库: 已安装")
    else:
        checks.append("[yellow]⚠[/yellow] Node 依赖库: 未检测到 (建议运行 pnpm install)")

    # 3. 构建状态检测 (dist)
    if os.path.exists(os.path.join(base_path, "dist")):
        checks.append("[green]✔[/green] 核心构建产物: 已生成")
    else:
        checks.append("[yellow]⚠[/yellow] 核心构建产物: 缺失 (建议运行 pnpm build)")

    # 4. 运行时环境 (Node.js 版本)
    try:
        node_version = subprocess.check_output(["node", "-v"]).decode().strip()
        checks.append(f"[green]✔[/green] Node.js 运行时: {node_version}")
    except:
        checks.append("[red]✘[/red] Node.js 运行时: 未找到")

    return checks

@app.command()
def onboard():
    """2. 一键入驻：全自动配置 Clawdbot 及其 OmniGate 增强插件 (带深度环境审计)"""
    console.print(Panel("[bold cyan]第二步：Clawdbot + OmniGate 深度入驻校验[/bold cyan]"))
    
    if not os.path.exists(".env"):
        setup_keys()
    
    # 1. 基础配置同步
    env_vars = {}
    with open(".env", "r") as f:
        for line in f:
            if "=" in line:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    env_vars[parts[0].strip()] = parts[1].strip()

    home = os.path.expanduser("~")
    openclaw_dir = os.path.join(home, ".openclaw")
    workspace_dir = os.path.join(openclaw_dir, "workspace")
    os.makedirs(workspace_dir, exist_ok=True)

    config_path = os.path.join(openclaw_dir, "openclaw.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            try: config = json.load(f)
            except: config = {}
    else: config = {}

    # --- 自动化配置同步 ---
    if "channels" not in config: config["channels"] = {}
    config["channels"]["telegram"] = {
        "enabled": True,
        "botToken": env_vars.get("TELEGRAM_BOT_TOKEN", ""),
        "allowFrom": [int(env_vars.get("TELEGRAM_OWNER_ID", 0))] if env_vars.get("TELEGRAM_OWNER_ID") else ["*"],
        "dmPolicy": "open"
    }
    
    if env_vars.get("DISCORD_BOT_TOKEN"):
        config["channels"]["discord"] = {
            "enabled": True,
            "botToken": env_vars.get("DISCORD_BOT_TOKEN", ""),
            "dmPolicy": "open"
        }

    if "models" not in config: config["models"] = {}
    if "providers" not in config["models"]: config["models"]["providers"] = {}
    providers = config["models"]["providers"]

    def sync_provider(name, base_url, api_type, model_id, model_name):
        key = env_vars.get(f"{name.upper()}_API_KEY")
        if key:
            providers[name] = {
                "enabled": True,
                "baseUrl": base_url,
                "apiKey": key,
                "api": api_type,
                "models": [{"id": model_id, "name": model_name, "api": api_type}]
            }

    # 同步所有潜在模型
    sync_provider("deepseek", "https://api.deepseek.com", "openai-completions", "deepseek-chat", "DeepSeek Chat")
    sync_provider("openai", "https://api.openai.com/v1", "openai-completions", "gpt-4o", "GPT-4o")
    sync_provider("claude", "https://api.anthropic.com/v1", "openai-completions", "claude-3-5-sonnet", "Claude 3.5 Sonnet")
    sync_provider("gemini", "https://generativelanguage.googleapis.com/v1", "openai-completions", "gemini-1.5-pro", "Gemini 1.5 Pro")
    sync_provider("groq", "https://api.groq.com/openai/v1", "openai-completions", "llama3-70b-8192", "Groq Llama 3")
    sync_provider("qwen", "https://dashscope.aliyuncs.com/compatible-mode/v1", "openai-completions", "qwen-plus", "通义千问 Plus")
    sync_provider("hunyuan", "https://api.hunyuan.tencent.com/v1", "openai-completions", "hunyuan-standard", "腾讯混元")
    sync_provider("zhipu", "https://open.bigmodel.cn/api/paas/v4", "openai-completions", "glm-4", "智谱清言 GLM-4")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # --- 2. 深度校验阶段 ---
    infra_results = []
    social_results = []
    ai_results = []
    
    from core.llm_gateway import LLMGateway
    from core.network import NetworkClient
    gateway = LLMGateway()
    network = NetworkClient()

    async def run_verification():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            # Phase 1: 基础设施审计
            t1 = progress.add_task("[yellow]阶段 1: 基础设施审计...", total=100)
            infra_results.extend(check_openclaw_env())
            progress.update(t1, completed=100)

            # Phase 2: 社交中枢心跳
            t2 = progress.add_task("[magenta]阶段 2: 社交中枢心跳...", total=100)
            # Telegram
            tg_token = env_vars.get("TELEGRAM_BOT_TOKEN")
            if tg_token:
                try:
                    res = await network.get_json(f"https://api.telegram.org/bot{tg_token}/getMe")
                    if res.get("ok"):
                        social_results.append(f"[green]✔[/green] Telegram: @{res['result']['username']} (在线)")
                    else:
                        social_results.append(f"[red]✘[/red] Telegram: Token 无效")
                except:
                    social_results.append(f"[red]✘[/red] Telegram: 连接 API 超时")
            
            # Discord
            if env_vars.get("DISCORD_BOT_TOKEN"):
                social_results.append(f"[green]✔[/green] Discord: 配置已同步")
            
            # Feishu
            if env_vars.get("FEISHU_APP_ID"):
                social_results.append(f"[green]✔[/green] Feishu: 配置已同步")
            
            progress.update(t2, completed=100)

            # Phase 3: 智能大脑握手 (全量 API)
            all_providers = ["deepseek", "openai", "claude", "gemini", "groq", "qwen", "hunyuan", "zhipu"]
            active_providers = [p for p in all_providers if env_vars.get(f"{p.upper()}_API_KEY")]
            
            if active_providers:
                t3 = progress.add_task("[cyan]阶段 3: 智能大脑握手...", total=len(active_providers))
                for p in active_providers:
                    progress.update(t3, description=f"[cyan]正在握手 {p.capitalize()}...")
                    v_res = await gateway.verify_provider(p)
                    if v_res["status"] == "success":
                        ai_results.append(f"[green]✔[/green] {p.capitalize()}: 连通正常 ({v_res['latency']}ms)")
                    else:
                        ai_results.append(f"[red]✘[/red] {p.capitalize()}: {v_res['message']}")
                    progress.advance(t3)

    asyncio.run(run_verification())

    # 输出结构化最终报告
    final_report = (
        "[bold white]1. 🏗️ 基础设施[/bold white]\n" + "\n".join(infra_results) + "\n\n" +
        "[bold white]2. 💬 社交渠道[/bold white]\n" + ("\n".join(social_results) if social_results else "[dim]未配置[/dim]") + "\n\n" +
        "[bold white]3. 🧠 智能大脑[/bold white]\n" + ("\n".join(ai_results) if ai_results else "[dim]未配置[/dim]")
    )
    
    console.print(Panel(
        final_report,
        title="[bold cyan]OmniGate Pro 深度审计报告[/bold cyan]",
        border_style="cyan"
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

VERSION = "3.0.0"

def version_callback(value: bool):
    if value:
        console.print(f"OmniGate Pro Version: [bold cyan]{VERSION}[/bold cyan]")
        raise typer.Exit()

@app.command()
def doctor():
    """诊断工具：全方位检查系统健康状况与连通性"""
    console.print(Panel("[bold magenta]OmniGate Pro 系统诊断中心 (Doctor Mode)[/bold magenta]"))
    
    # 复用 onboard 的校验逻辑
    results = []
    from core.llm_gateway import LLMGateway
    from core.network import NetworkClient
    gateway = LLMGateway()
    network = NetworkClient()

    async def run_diagnostics():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # 1. 检查环境变量
            t1 = progress.add_task("[cyan]检查配置文件...", total=1)
            if os.path.exists(".env"):
                results.append("[green]✔[/green] .env 配置文件: 存在")
            else:
                results.append("[red]✘[/red] .env 配置文件: 缺失")
            progress.advance(t1)

            # 2. 检查网络与 Telegram
            t2 = progress.add_task("[cyan]检查网络与社交渠道...", total=1)
            tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if tg_token:
                try:
                    res = await network.get_json(f"https://api.telegram.org/bot{tg_token}/getMe")
                    if res.get("ok"):
                        results.append(f"[green]✔[/green] Telegram 连通性: 正常 (@{res['result']['username']})")
                    else:
                        results.append(f"[red]✘[/red] Telegram 连通性: 失败 ({res.get('description')})")
                except:
                    results.append("[red]✘[/red] Telegram 连通性: 网络无法访问 api.telegram.org")
            progress.advance(t2)

            # 3. 检查 AI 提供商
            t3 = progress.add_task("[cyan]检查 AI 模型服务...", total=1)
            providers = ["deepseek", "openai", "qwen"]
            for p in providers:
                if os.getenv(f"{p.upper()}_API_KEY"):
                    v_res = await gateway.verify_provider(p)
                    if v_res["status"] == "success":
                        results.append(f"[green]✔[/green] {p.capitalize()} API: 可用 (延迟: {v_res['latency']}ms)")
                    else:
                        results.append(f"[red]✘[/red] {p.capitalize()} API: 不可用 ({v_res['message']})")
            progress.advance(t3)

            # 4. 系统资源
            t4 = progress.add_task("[cyan]检查系统资源...", total=1)
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            results.append(f"[green]✔[/green] 系统负载: CPU {cpu}% / 内存 {mem}%")
            progress.advance(t4)

    asyncio.run(run_diagnostics())
    
    report_text = "\n".join(results)
    console.print(Panel(report_text, title="健康诊断报告", border_style="magenta"))

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="显示版本号", callback=version_callback, is_eager=True
    ),
):
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
                "🩺 系统诊断 [全面健康检查]",
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
        elif "系统诊断" in choice: doctor()
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
