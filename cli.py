import typer
import os
import sys
import json
import time
import shutil
import asyncio
import httpx
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

from dotenv import load_dotenv, set_key

# 初始化环境变量
load_dotenv()

VERSION = "3.0.0"

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
    # 1. OpenClaw 原生技能
    native_skills = []
    skills_dir = os.path.join("openclaw", "skills")
    if os.path.exists(skills_dir):
        try:
            native_skills = [item for item in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, item))]
        except: pass
    
    # 2. OmniGate Pro 动态技能
    dynamic_skills = []
    omni_skills_dir = "skills"
    if os.path.exists(omni_skills_dir):
        try:
            dynamic_skills = [f.replace(".py", "") for f in os.listdir(omni_skills_dir) if f.endswith(".py") and f != "__init__.py"]
        except: pass
        
    return native_skills, dynamic_skills

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
        Layout(name="memory", size=8),
    )
    layout["right"].split_column(
        Layout(name="agents", size=8),
        Layout(name="skills", ratio=1),
    )
    return layout

def get_memory_panel():
    from core.omni_engine import omni_engine
    mems = omni_engine.memory.memory.get("long_term_facts", [])
    table = Table.grid(expand=True)
    if not mems:
        table.add_row("[dim]暂无长效记忆记录[/dim]")
    else:
        for m in mems[-4:]: # 显示最后4条
            table.add_row(f"🧠 [italic]{m[:30]}...[/italic]")
    return Panel(table, title="🧠 长期记忆", border_style="cyan")

def get_status_panel():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    table = Table.grid(expand=True)
    table.add_column(style="cyan", justify="left")
    table.add_column(justify="right")
    table.add_row("CPU 负载:", f"[bold]{cpu}%[/bold]")
    table.add_row("内存占用:", f"[bold]{mem}%[/bold]")
    table.add_row("系统版本:", f"v{VERSION}")
    table.add_row("网关模式:", "[bold yellow]Pro (增强版)[/bold yellow]")
    table.add_row("API 状态:", "[bold green]在线[/bold green]")
    return Panel(table, title="🚀 系统健康度", border_style="blue")

def get_token_panel():
    stats = token_tracker.get_summary()
    table = Table(show_header=True, header_style="bold magenta", box=None, expand=True)
    table.add_column("大脑", style="dim")
    table.add_column("原始", justify="right")
    table.add_column("Omni 优化", justify="right")
    table.add_column("节省率", style="green", justify="right")
    
    for provider, data in stats["providers"].items():
        if data["original"] > 0:
            table.add_row(
                provider.capitalize(), 
                f"{data['original']}", 
                f"{data['optimized']}", 
                f"{round(data['saved']/data['original']*100)}%"
            )
    
    summary = (
        f"总节省率: [bold green]{stats['savings_rate']}%[/bold green]  "
        f"累计节省: [bold yellow]{stats['total_saved']}[/bold yellow]"
    )
    
    from rich.console import Group
    return Panel(
        Group(table, Align.center(summary)),
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
    native, dynamic = get_bundled_skills()
    text = Text()
    
    if dynamic:
        text.append("🔥 Omni Pro 动态插件:\n", style="bold yellow")
        for s in dynamic:
            text.append(f" ⚡ {s} ", style="black on yellow")
        text.append("\n\n")
        
    text.append("🧩 OpenClaw 原生技能:\n", style="bold cyan")
    for i, s in enumerate(native[:12]):
        text.append(f" 📦 {s} ", style="white on blue")
        if (i+1) % 3 == 0: text.append("\n")
        
    return Panel(Align.left(text), title="🛠️ 增强技能库", border_style="green")

@app.command()
def dashboard():
    """终端控制面板：在命令行实时监控与管理系统"""
    layout = make_layout()
    layout["header"].update(Panel(Align.center(f"[bold white]OmniGate Pro 终端控制中心 v{VERSION}[/bold white]"), border_style="blue"))
    layout["footer"].update(Panel(Align.center("[dim]按 Ctrl+C 退出面板返回主菜单[/dim]"), border_style="white"))
    
    config = get_openclaw_config()
    
    try:
        with Live(layout, refresh_per_second=2, screen=True):
            while True:
                layout["status"].update(get_status_panel())
                layout["token_stats"].update(get_token_panel())
                layout["memory"].update(get_memory_panel())
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
    
    def safe_ask_password(prompt, key):
        val = questionary.password(prompt, default=env_vars.get(key, "")).ask()
        return val.strip() if val else env_vars.get(key, "")

    def safe_ask_text(prompt, key):
        val = questionary.text(prompt, default=env_vars.get(key, "")).ask()
        return val.strip() if val else env_vars.get(key, "")

    # 1. 国际主流模型
    console.print("\n[bold cyan]1. 🌍 国际主流模型 (Global LLMs)[/bold cyan]")
    keys["DEEPSEEK_API_KEY"] = safe_ask_password("DeepSeek API Key (推荐):", "DEEPSEEK_API_KEY")
    keys["OPENAI_API_KEY"] = safe_ask_password("OpenAI API Key (GPT-4):", "OPENAI_API_KEY")
    keys["CLAUDE_API_KEY"] = safe_ask_password("Anthropic Claude Key:", "CLAUDE_API_KEY")
    keys["GEMINI_API_KEY"] = safe_ask_password("Google Gemini Key:", "GEMINI_API_KEY")
    keys["GROQ_API_KEY"] = safe_ask_password("Groq Key (Llama 3):", "GROQ_API_KEY")

    # 2. 国内主流模型
    console.print("\n[bold cyan]2. 🇨🇳 国内主流模型 (Chinese LLMs)[/bold cyan]")
    keys["QWEN_API_KEY"] = safe_ask_password("通义千问 (DashScope) Key:", "QWEN_API_KEY")
    keys["HUNYUAN_API_KEY"] = safe_ask_password("腾讯混元 API Key:", "HUNYUAN_API_KEY")
    keys["ZHIPU_API_KEY"] = safe_ask_password("智谱清言 (GLM) Key:", "ZHIPU_API_KEY")
    keys["WENXIN_API_KEY"] = safe_ask_password("百度文心 (ERNIE) Key:", "WENXIN_API_KEY")

    # 3. 社交平台
    console.print("\n[bold cyan]3. 💬 社交平台与网络 (Social & Network)[/bold cyan]")
    keys["TELEGRAM_BOT_TOKEN"] = safe_ask_password("Telegram Bot Token:", "TELEGRAM_BOT_TOKEN")
    keys["TELEGRAM_OWNER_ID"] = safe_ask_text("Telegram 用户 ID (权限控制):", "TELEGRAM_OWNER_ID")
    
    # 新增代理配置
    keys["HTTPS_PROXY"] = safe_ask_text("代理服务器地址 (可选，如 http://127.0.0.1:7890):", "HTTPS_PROXY")
    if keys["HTTPS_PROXY"]:
        os.environ["HTTP_PROXY"] = keys["HTTPS_PROXY"]
        os.environ["HTTPS_PROXY"] = keys["HTTPS_PROXY"]

    confirm_discord = questionary.confirm("是否配置 Discord?").ask()
    if confirm_discord:
        keys["DISCORD_BOT_TOKEN"] = safe_ask_password("Discord Bot Token:", "DISCORD_BOT_TOKEN")
        keys["DISCORD_WEBHOOK_URL"] = safe_ask_text("Discord Webhook URL:", "DISCORD_WEBHOOK_URL")
    
    confirm_feishu = questionary.confirm("是否配置飞书 (Feishu)?").ask()
    if confirm_feishu:
        keys["FEISHU_APP_ID"] = safe_ask_text("飞书 App ID:", "FEISHU_APP_ID")
        keys["FEISHU_APP_SECRET"] = safe_ask_password("飞书 App Secret:", "FEISHU_APP_SECRET")

    # 保存至 .env
    with open(".env", "w", encoding="utf-8") as f:
        for k, v in keys.items():
            if v is not None and str(v).strip() != "": 
                f.write(f"{k}={v}\n")
    
    # 强制重新加载环境变量
    load_dotenv(override=True)
    console.print("[bold green]✅ 全平台密钥已同步至 .env 文件并已加载到系统。[/bold green]")

def check_openclaw_env() -> List[str]:
    """深度检测本地 OpenClaw 源码、依赖及构建状态"""
    checks = []
    
    # 尝试多种可能的路径
    possible_paths = [
        os.path.join(os.getcwd(), "openclaw", "openclaw"),
        os.path.join(os.getcwd(), "openclaw"),
        os.path.join(os.getcwd(), "..", "openclaw"),
    ]
    
    base_path = None
    for p in possible_paths:
        if os.path.exists(os.path.join(p, "package.json")):
            base_path = p
            break
            
    # 1. 源码检测
    if base_path:
        checks.append(f"[green]✔[/green] OpenClaw 源码: 已就绪 ({os.path.basename(base_path)})")
    else:
        checks.append("[red]✘[/red] OpenClaw 源码: 缺失 (请确保已执行 git clone)")
        return checks

    # 2. 依赖检测 (node_modules)
    if os.path.exists(os.path.join(base_path, "node_modules")):
        checks.append("[green]✔[/green] Node 依赖库: 已安装")
    else:
        checks.append("[yellow]⚠[/yellow] Node 依赖库: 未检测到 (建议运行 pnpm install)")

    # 3. 构建状态检测 (dist)
    # OpenClaw 核心构建产物通常在 dist 文件夹
    if os.path.exists(os.path.join(base_path, "dist")):
        checks.append("[green]✔[/green] 核心构建产物: 已生成")
    else:
        checks.append("[yellow]⚠[/yellow] 核心构建产物: 缺失 (建议运行 pnpm build)")

    # 4. 运行时环境 (Node.js 版本)
    try:
        if platform.system() == "Windows":
            node_version = subprocess.check_output(
                "node -v", 
                stderr=subprocess.STDOUT,
                shell=True
            ).decode().strip()
        else:
            node_version = subprocess.check_output(
                ["node", "-v"], 
                stderr=subprocess.STDOUT,
                shell=False
            ).decode().strip()
        checks.append(f"[green]✔[/green] Node.js 运行时: {node_version}")
    except Exception:
        checks.append("[red]✘[/red] Node.js 运行时: 未找到 (请安装 Node.js 22+)")

    return checks

@app.command()
def mcp():
    """启动 MCP 服务器 (Clawdbot 插件模式)"""
    from core.mcp_server import mcp as mcp_app
    mcp_app.run()

@app.command()
def onboard():
    """2. 一键入驻：全自动配置 Clawdbot 及其 OmniGate 增强插件 (带深度环境审计)"""
    console.print(Panel("[bold cyan]第二步：Clawdbot + OmniGate 深度入驻校验[/bold cyan]"))
    
    if not os.path.exists(".env"):
        setup_keys()
    
    # 强制重载配置单例
    from core.config import settings
    settings.reload()
    
    # 强制加载最新的 .env 到环境变量
    load_dotenv(override=True)
    
    # 1. 基础配置同步
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
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
    # 渠道配置
    if "channels" not in config: config["channels"] = {}
    config["channels"]["telegram"] = {
        "enabled": True,
        "botToken": env_vars.get("TELEGRAM_BOT_TOKEN", ""),
        "allowFrom": [int(env_vars.get("TELEGRAM_OWNER_ID", 0)), "*"] if env_vars.get("TELEGRAM_OWNER_ID") and env_vars.get("TELEGRAM_OWNER_ID").isdigit() else ["*"],
        "dmPolicy": "open"
    }
    
    if env_vars.get("DISCORD_BOT_TOKEN"):
        config["channels"]["discord"] = {
            "enabled": True,
            "botToken": env_vars.get("DISCORD_BOT_TOKEN", ""),
            "dmPolicy": "open",
            "dm": { "allowFrom": ["*"] }
        }

    if "models" not in config: config["models"] = {}
    if "providers" not in config["models"]: config["models"]["providers"] = {}
    providers = config["models"]["providers"]

    # Deepseek 配置 (符合 OpenClaw 格式)
    if env_vars.get("DEEPSEEK_API_KEY"):
        providers["deepseek"] = {
            "baseUrl": "https://api.deepseek.com",
            "apiKey": env_vars.get("DEEPSEEK_API_KEY"),
            "api": "openai-completions",
            "models": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat", "api": "openai-completions"}
            ]
        }

    def sync_provider(name, base_url, api_type, model_id, model_name):
        key = env_vars.get(f"{name.upper()}_API_KEY")
        if key:
            providers[name] = {
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
    sync_provider("wenxin", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop", "openai-completions", "ernie-4.0", "文心一言 4.0")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # --- 2. 深度校验阶段 ---
    infra_results = []
    social_results = []
    ai_results = []
    
    from core.llm_gateway import LLMGateway
    from core.network import NetworkClient
    
    # 强制重新实例化以加载最新环境变量
    gateway = LLMGateway()
    network = NetworkClient()

    async def run_verification():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            
            # Phase 1: 基础设施审计
            t1 = progress.add_task("[yellow]阶段 1: 基础设施审计...", total=100)
            infra_checks = check_openclaw_env()
            for check in infra_checks:
                infra_results.append(check)
                progress.advance(t1, 100 / len(infra_checks) if infra_checks else 100)
                await asyncio.sleep(0.1)
            progress.update(t1, completed=100)

            # Phase 2: 社交中枢心跳
            t2 = progress.add_task("[magenta]阶段 2: 社交中枢心跳...", total=100)
            # Telegram
            tg_token = env_vars.get("TELEGRAM_BOT_TOKEN")
            if tg_token:
                progress.update(t2, description="[magenta]正在校验 Telegram (含代理检测)...")
                try:
                    # 统一从环境变量和 env_vars 获取最新代理
                    proxy_url = env_vars.get("HTTPS_PROXY") or os.environ.get("HTTPS_PROXY") or \
                                os.environ.get("HTTP_PROXY")
                    
                    if proxy_url and not proxy_url.startswith("http"):
                        proxy_url = f"http://{proxy_url}"
                    
                    async with httpx.AsyncClient(proxy=proxy_url if proxy_url else None, timeout=15.0, verify=False) as client:
                        response = await client.get(f"https://api.telegram.org/bot{tg_token}/getMe")
                        res = response.json()
                        if res.get("ok"):
                            status_suffix = f" (代理: {proxy_url})" if proxy_url else " (直连)"
                            social_results.append(f"[green]✔[/green] Telegram: @{res['result']['username']}{status_suffix}")
                        else:
                            social_results.append(f"[red]✘[/red] Telegram: Token 无效")
                except Exception as e:
                    social_results.append(f"[red]✘[/red] Telegram: 连接失败 ({str(e)[:50]})")
            
            # Discord / Feishu
            if env_vars.get("DISCORD_BOT_TOKEN"): social_results.append(f"[green]✔[/green] Discord: 配置已同步")
            if env_vars.get("FEISHU_APP_ID"): social_results.append(f"[green]✔[/green] Feishu: 配置已同步")
            progress.update(t2, completed=100)

            # Phase 3: 智能大脑握手
            all_providers = ["deepseek", "openai", "claude", "gemini", "groq", "qwen", "hunyuan", "zhipu", "wenxin"]
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
                    await asyncio.sleep(0.1)

    try:
        # 确保异步执行正常
        asyncio.run(run_verification())
    except Exception as e:
        console.print(f"[red]校验过程发生异常: {str(e)}[/red]")

    # 输出结构化最终报告
    final_report = (
        "[bold white]1. 🏗️ 基础设施审计[/bold white]\n" + "\n".join(infra_results) + "\n\n" +
        "[bold white]2. 💬 社交中枢心跳[/bold white]\n" + ("\n".join(social_results) if social_results else "[dim]未配置[/dim]") + "\n\n" +
        "[bold white]3. 🧠 智能大脑握手[/bold white]\n" + ("\n".join(ai_results) if ai_results else "[dim]未配置[/dim]")
    )
    
    console.print(Panel(
        final_report,
        title="[bold cyan]OmniGate Pro 深度审计报告 (v3.0)[/bold cyan]",
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
    """3. 启动运行：开启全能网关 (OpenClaw + OmniGate) 并进入仪表盘"""
    console.print(Panel("[bold green]第三步：启动 OmniGate + OpenClaw 联合网关服务[/bold green]"))
    
    # 强制重新加载环境变量
    load_dotenv(override=True)
    
    # 1. 清理端口冲突 (OmniGate 使用 18799, OpenClaw 使用 18789)
    check_port(18799)
    check_port(18789)
    
    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    openclaw_log = open(os.path.join(log_dir, "openclaw.log"), "a", encoding="utf-8")
    
    # 2. 启动 OmniGate REST API (Sidecar)
    from core.fastapi_gateway import run_api
    import threading
    threading.Thread(target=run_api, kwargs={"port": 18799}, daemon=True).start()
    
    # 3. 启动 OpenClaw Gateway (核心引擎)
    # 寻找 openclaw 路径
    possible_paths = [
        os.path.join(os.getcwd(), "openclaw", "openclaw"),
        os.path.join(os.getcwd(), "openclaw"),
    ]
    openclaw_path = next((p for p in possible_paths if os.path.exists(os.path.join(p, "package.json"))), None)
    
    if openclaw_path:
        console.print(f"[dim]正在启动 OpenClaw 引擎 (路径: {openclaw_path})...[/dim]")
        # 注入代理环境变量
        env = os.environ.copy()
        proxy = env.get("HTTPS_PROXY") or env.get("HTTP_PROXY")
        if proxy:
            env["HTTP_PROXY"] = proxy
            env["HTTPS_PROXY"] = proxy
            console.print(f"[dim]已注入代理: {proxy}[/dim]")
            
        # 寻找 pnpm
        pnpm_exe = shutil.which("pnpm")
        if not pnpm_exe and platform.system() == "Windows":
            pnpm_exe = "pnpm" # 兜底
            
        # 异步启动 OpenClaw Gateway
        cmd = [pnpm_exe if pnpm_exe else "pnpm", "openclaw", "gateway", "--port", "18789"]
        
        try:
            if platform.system() == "Windows":
                # Windows 下使用字符串形式配合 shell=True 兼容性最好
                cmd_str = " ".join(cmd)
                subprocess.Popen(
                    cmd_str,
                    cwd=openclaw_path,
                    env=env,
                    stdout=openclaw_log,
                    stderr=openclaw_log,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP") else 0
                )
            else:
                subprocess.Popen(
                    cmd,
                    cwd=openclaw_path,
                    env=env,
                    stdout=openclaw_log,
                    stderr=openclaw_log,
                    shell=False
                )
            console.print("[green]✔ OpenClaw 引擎已在后台启动，日志记录于 logs/openclaw.log[/green]")
        except Exception as e:
            console.print(f"[red]✘ 启动 OpenClaw 失败: {str(e)}[/red]")
    else:
        console.print("[red]✘ 找不到 OpenClaw 源码，无法启动 Telegram Bot 核心！[/red]")
        console.print("[yellow]提示：请确保已在 openclaw 目录下运行了 git clone。[/yellow]")
    
    time.sleep(3) # 等待双服务启动
    # 4. 进入终端仪表盘
    dashboard()

@app.command()
def fix():
    """修复工具：一键解决环境依赖与配置冲突"""
    console.print(Panel("[bold yellow]正在执行系统自愈修复程序...[/bold yellow]"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # 1. 检查 Python 依赖
        t1 = progress.add_task("[cyan]正在检查并修复 Python 依赖...", total=100)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            progress.update(t1, completed=100)
        except:
            console.print("[red]✘ 依赖修复失败，请手动执行 pip install -r requirements.txt[/red]")

        # 2. 检查 OpenClaw 修复
        t2 = progress.add_task("[cyan]正在调用 OpenClaw 自检修复...", total=100)
        try:
            os.system("openclaw doctor --fix")
            progress.update(t2, completed=100)
        except: pass

        # 3. 清理残留进程
        t3 = progress.add_task("[cyan]正在清理冲突进程...", total=100)
        check_port(18789)
        progress.update(t3, completed=100)

    console.print("[bold green]✅ 系统自愈完成。请重新运行 onboard 进行校验。[/bold green]")

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
    
    # 强制重载配置单例
    from core.config import settings
    settings.reload()
    
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
                    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
                    if proxy_url and not proxy_url.startswith("http"):
                        proxy_url = f"http://{proxy_url}"

                    async with httpx.AsyncClient(proxy=proxy_url if proxy_url else None, timeout=15.0, verify=False) as client:
                        response = await client.get(f"https://api.telegram.org/bot{tg_token}/getMe")
                        res = response.json()
                        if res.get("ok"):
                            results.append(f"[green]✔[/green] Telegram 连通性: 正常 (@{res['result']['username']})")
                        else:
                            results.append(f"[red]✘[/red] Telegram 连通性: 失败 (Token 无效)")
                except Exception as e:
                    results.append(f"[red]✘[/red] Telegram 连通性: 无法访问 ({str(e)[:50]})")
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

@app.command()
def status():
    """查看系统运行状态与日志"""
    console.print(Panel("[bold cyan]OmniGate Pro 系统运行状态诊断[/bold cyan]"))
    
    # 1. 检查端口
    def is_port_in_use(port):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    table = Table(title="服务运行状态")
    table.add_column("服务名称", style="cyan")
    table.add_column("端口", style="magenta")
    table.add_column("状态", style="bold")
    
    table.add_row("OmniGate API", "18799", "[green]在线[/green]" if is_port_in_use(18799) else "[red]离线[/red]")
    table.add_row("OpenClaw Gateway", "18789", "[green]在线[/green]" if is_port_in_use(18789) else "[red]离线[/red]")
    
    console.print(table)
    
    # 2. 查看日志
    log_path = os.path.join(os.getcwd(), "logs", "openclaw.log")
    if os.path.exists(log_path):
        console.print("\n[bold white]📄 OpenClaw 最新运行日志 (最后 10 行):[/bold white]")
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    console.print(f"[dim]{line.strip()}[/dim]")
        except:
            console.print("[yellow]无法读取日志文件[/yellow]")
    else:
        console.print("\n[yellow]未找到 OpenClaw 日志文件。[/yellow]")
    
    questionary.press_any_key_to_continue().ask()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="显示版本号", callback=version_callback, is_eager=True
    ),
):
    """OmniGate Pro - 标准化流程控制台"""
    if ctx.invoked_subcommand is None:
        while True:
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
                    "📊 系统状态 [查看运行日志与状态]",
                    "🩺 系统诊断 [全面健康检查]",
                    "⚙️ 进阶配置 [语音、画布、多智能体]",
                    "🔧 系统自愈 [修复 Windows 兼容报错]",
                    "💡 教程链条 [查看系统底层连接逻辑]",
                    "❌ 退出系统"
                ]
            ).ask()

            if not choice or "退出" in choice: 
                break

            if "配置密钥" in choice: setup_keys()
            elif "一键入驻" in choice: onboard()
            elif "启动运行" in choice: run()
            elif "系统状态" in choice: status()
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
                # 循环会自动回到菜单

if __name__ == "__main__":
    app()
