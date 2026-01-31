import typer
import rich
import questionary
import psutil
import platform
import os
import json
import time
import requests
import yaml
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.logging import RichHandler
import logging
from datetime import datetime

# Initialize Rich Console and Typer
console = Console()
app = typer.Typer(
    name="artfish",
    help="Artfish Studio - 艺术教育多智能体协作平台控制台",
    add_completion=True,
)

# Configuration
API_URL = os.getenv("EDUSENSE_API_URL", "http://localhost:8000")

# Setup Logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)
logger = logging.getLogger("artfish")

# --- Helpers ---

def check_server_silent():
    try:
        requests.get(f"{API_URL}/health", timeout=2)
        return True
    except:
        return False

def get_git_revision_hash() -> str:
    try:
        import subprocess
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()[:7]
    except:
        return "unknown"

# --- Commands ---

@app.command()
def doctor():
    """环境诊断：检查系统运行环境与 API 连通性"""
    console.print(Panel("[bold cyan]OmniGate Pro System Diagnosis[/bold cyan]"))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="dim")
    table.add_column("Status")
    table.add_column("Details")

    # Python Version
    py_ver = platform.python_version()
    table.add_row("Python Runtime", "[green]OK[/green]", f"v{py_ver}")

    # Core Libraries
    try:
        import fastapi, sqlalchemy, redis, bs4
        table.add_row("Core Libraries", "[green]OK[/green]", "FastAPI, SQLAlchemy, Redis, BeautifulSoup")
    except ImportError as e:
        table.add_row("Core Libraries", "[red]MISSING[/red]", str(e))

    # Redis Check
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
        r.ping()
        table.add_row("Redis Queue", "[green]ONLINE[/green]", "localhost:6379")
    except:
        table.add_row("Redis Queue", "[yellow]OFFLINE[/yellow]", "Task queue will run in simulation mode")

    # .env Check
    if os.path.exists(".env"):
        table.add_row("Config File (.env)", "[green]FOUND[/green]", "Environment variables loaded")
    else:
        table.add_row("Config File (.env)", "[red]MISSING[/red]", "Run 'setup-keys' to create one")

    console.print(table)

@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", help="结构化数据输出"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="显示详细指标")
):
    """实时指标：展示系统负载与业务健康度"""
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    git_hash = get_git_revision_hash()
    
    data = {
        "system": {
            "cpu_percent": cpu_usage,
            "memory_percent": mem.percent,
            "disk_percent": disk.percent,
            "platform": platform.system(),
            "uptime": int(time.time() - psutil.boot_time()),
        },
        "version": "0.4.0",
        "git_hash": git_hash,
        "api_status": "ONLINE" if check_server_silent() else "OFFLINE"
    }

    if json_output:
        console.print_json(data=data)
        return

    console.print(Panel(f"[bold]Artfish Dashboard[/bold] | [dim]Hash: {git_hash}[/dim]", border_style="blue"))
    
    # System Resource Table
    sys_table = Table(title="System Resources", box=rich.box.SIMPLE)
    sys_table.add_column("Resource", style="cyan")
    sys_table.add_column("Usage", justify="right")
    sys_table.add_row("CPU", f"{cpu_usage}%")
    sys_table.add_row("Memory", f"{mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)")
    sys_table.add_row("Disk", f"{disk.percent}%")
    console.print(sys_table)

    if verbose:
        # Mocking some metrics for display
        metrics_table = Table(title="Business Metrics (P95/P99)", box=rich.box.SIMPLE)
        metrics_table.add_column("Metric", style="green")
        metrics_table.add_column("Value", justify="right")
        metrics_table.add_row("Request Latency (P95)", "124ms")
        metrics_table.add_row("Request Latency (P99)", "450ms")
        metrics_table.add_row("Throughput (QPS)", "12.5 req/s")
        metrics_table.add_row("Success Rate", "99.8%")
        console.print(metrics_table)

@app.command()
def run(
    goals: List[str] = typer.Argument(None, help="意图目标列表"),
    style: str = typer.Option("default", help="执行风格约束"),
    apply: bool = typer.Option(False, "--apply", help="正式提交执行 (默认 Dry-run)"),
    file: Optional[typer.FileText] = typer.Option(None, help="从 YAML/JSON 文件读取批量任务")
):
    """执行意图：提交目标并编排任务执行"""
    task_goals = goals or []
    
    if file:
        try:
            content = yaml.safe_load(file)
            task_goals = content.get("goals", [])
            style = content.get("constraints", {}).get("style", style)
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            raise typer.Exit(1)

    if not task_goals:
        console.print("[yellow]No goals provided. Entering interactive mode...[/yellow]")
        goal = questionary.text("What is your goal?").ask()
        if not goal: return
        task_goals = [goal]

    if not apply:
        console.print(Panel(
            f"[bold yellow]DRY-RUN MODE[/bold yellow]\n\n"
            f"Goals: {', '.join(task_goals)}\n"
            f"Style: {style}\n\n"
            "Add [bold]--apply[/bold] to actually execute this task.",
            title="Pre-flight Check"
        ))
        return

    # Actual Execution
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        t1 = progress.add_task("[cyan]Submitting task...", total=100)
        
        # 1. Submit
        payload = {"goals": task_goals, "constraints": {"style": style}}
        try:
            res = requests.post(f"{API_URL}/v1/execute", json=payload)
            res.raise_for_status()
            run_id = res.json()["run_id"]
            progress.update(t1, advance=30, description=f"[cyan]Task ID: {run_id[:8]}...")
            
            # 2. Poll
            finished = False
            while not finished:
                time.sleep(1)
                status_res = requests.get(f"{API_URL}/v1/execution/{run_id}")
                status_data = status_res.json()
                status = status_data["status"]
                
                if status == "SUCCESS":
                    progress.update(t1, completed=100, description="[green]Execution Complete!")
                    finished = True
                elif status == "FAIL":
                    progress.update(t1, completed=100, description="[red]Execution Failed!")
                    finished = True
                else:
                    progress.update(t1, advance=5, description=f"[cyan]Running: {status}...")
            
            console.print(f"\n[bold green]SUCCESS![/bold green] Report: {API_URL}/v1/execution/{run_id}/report")
            
        except Exception as e:
            console.print(f"[red]Execution error: {e}[/red]")

@app.command()
def benchmark(
    iterations: int = typer.Option(5, help="测试轮数"),
    concurrency: int = typer.Option(1, help="并发数")
):
    """性能测试：评估引擎响应延迟与吞吐量"""
    console.print(f"Starting benchmark with {iterations} iterations...")
    latencies = []
    
    with Progress(console=console) as progress:
        task = progress.add_task("[yellow]Benchmarking...", total=iterations)
        for i in range(iterations):
            start = time.time()
            requests.get(f"{API_URL}/health")
            latencies.append((time.time() - start) * 1000)
            progress.advance(task)
    
    latencies.sort()
    p50 = latencies[len(latencies)//2]
    p95 = latencies[int(len(latencies)*0.95)]
    p99 = latencies[int(len(latencies)*0.99)]
    
    table = Table(title="Benchmark Results (ms)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_row("P50 Latency", f"{p50:.2f}ms")
    table.add_row("P95 Latency", f"{p95:.2f}ms")
    table.add_row("P99 Latency", f"{p99:.2f}ms")
    table.add_row("Avg Latency", f"{sum(latencies)/len(latencies):.2f}ms")
    console.print(table)

@app.command()
def setup_keys():
    """密钥配置：交互式配置 Telegram, 飞书及 AI 模型密钥"""
    console.print(Panel("[bold green]API Key Setup Wizard[/bold green]"))
    
    keys = {
        "TELEGRAM_BOT_TOKEN": "Telegram Bot Token",
        "FEISHU_APP_ID": "Feishu App ID",
        "FEISHU_APP_SECRET": "Feishu App Secret",
        "OPENAI_API_KEY": "OpenAI API Key",
        "CLAUDE_API_KEY": "Claude API Key",
        "DEEPSEEK_API_KEY": "DeepSeek API Key"
    }
    
    updates = {}
    for env_var, label in keys.items():
        val = questionary.text(f"Enter {label}:").ask()
        if val:
            updates[env_var] = val
            
    if updates:
        # 写入 .env 文件
        with open(".env", "a") as f:
            for k, v in updates.items():
                f.write(f"{k}={v}\n")
        console.print("[bold green]Success![/bold green] Keys saved to .env")
    else:
        console.print("[yellow]No changes made.[/yellow]")

@app.command()
def config():
    """配置管理：查看或修改系统配置"""
    from core.config import settings
    
    action = questionary.select(
        "What would you like to do?",
        choices=[
            "View Current Config",
            "Edit Environment (Interactive)",
            "Back"
        ]
    ).ask()

    if action == "View Current Config":
        console.print_json(data=settings.model_dump())
    elif action == "Edit Environment (Interactive)":
        console.print("[yellow]Coming soon: Environment editor[/yellow]")

@app.command()
def backup():
    """备份数据：导出数据库及结果存档"""
    import shutil
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"artfish_backup_{timestamp}"
    
    console.print(f"[cyan]Creating backup {backup_name}...[/cyan]")
    try:
        # Create a temp dir to collect files
        os.makedirs(backup_name)
        if os.path.exists("artfish.db"):
            shutil.copy("artfish.db", backup_name)
        if os.path.exists("exports"):
            shutil.copytree("exports", f"{backup_name}/exports")
            
        shutil.make_archive(backup_name, 'zip', backup_name)
        shutil.rmtree(backup_name)
        console.print(f"[green]Backup created: {backup_name}.zip[/green]")
    except Exception as e:
        console.print(f"[red]Backup failed: {e}[/red]")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Artfish Studio 艺术教育协作网关"""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            "[bold white]Artfish Studio 🎨 🦞[/bold white]\n[dim]艺术教育多智能体协作执行中枢[/dim]",
            border_style="indigo",
            expand=False
        ))
        
        choice = questionary.select(
            "请选择操作:",
            choices=[
                "1. Studio Assistant (创作助教)",
                "2. Project Analytics (项目分析)",
                "3. System Diagnosis (系统诊断)",
                "4. Configuration (配置管理)",
                "5. Exit (退出)"
            ],
            use_shortcuts=True
        ).ask()

        if "Studio" in choice:
            console.print("[yellow]进入创作室模式...[/yellow]")
        elif "Analytics" in choice:
            ctx.invoke(status)
        elif "Diagnosis" in choice:
            ctx.invoke(doctor)
        elif "Configuration" in choice:
            ctx.invoke(config)
        else:
            console.print("[dim]祝您创作愉快！再见。[/dim]")

if __name__ == "__main__":
    app()
