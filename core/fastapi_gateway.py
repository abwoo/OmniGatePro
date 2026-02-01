from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from core.omni_engine import omni_engine
from core.api_engine import api_engine
import uvicorn
import os
import psutil
import platform

app = FastAPI(title="OmniGate Pro Dashboard", description="可视化管理面板")

# 模拟模板数据（实际生产环境建议使用独立前端）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniGate Pro | 可视化面板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .glass { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="bg-slate-50 min-h-screen text-slate-900">
    <nav class="glass sticky top-0 z-50 border-b border-slate-200 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="bg-blue-600 p-2 rounded-lg text-white">
                <i class="fas fa-gateway"></i>
            </div>
            <h1 class="text-xl font-bold tracking-tight text-blue-600">OmniGate <span class="text-slate-400">Pro</span></h1>
        </div>
        <div class="flex items-center space-x-4">
            <span class="flex items-center text-sm font-medium text-green-600">
                <span class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                网关在线
            </span>
            <button onclick="window.location.reload()" class="p-2 hover:bg-slate-100 rounded-full transition-colors">
                <i class="fas fa-sync-alt text-slate-500"></i>
            </button>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto p-6 space-y-8">
        <!-- 状态概览 -->
        <section class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p class="text-slate-500 text-sm font-medium mb-1">CPU 负载</p>
                <h2 class="text-3xl font-bold text-slate-800">{{ cpu }}%</h2>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-4">
                    <div class="bg-blue-500 h-1.5 rounded-full" style="width: {{ cpu }}%"></div>
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p class="text-slate-500 text-sm font-medium mb-1">内存占用</p>
                <h2 class="text-3xl font-bold text-slate-800">{{ mem }}%</h2>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-4">
                    <div class="bg-blue-500 h-1.5 rounded-full" style="width: {{ mem }}%"></div>
                </div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p class="text-slate-500 text-sm font-medium mb-1">系统版本</p>
                <h2 class="text-3xl font-bold text-slate-800">v3.0.0</h2>
                <p class="text-xs text-slate-400 mt-4">基于 OpenClaw 核心增强</p>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <p class="text-slate-500 text-sm font-medium mb-1">活跃适配器</p>
                <h2 class="text-3xl font-bold text-slate-800">{{ adapters_count }}</h2>
                <p class="text-xs text-slate-400 mt-4">Telegram, Discord, Feishu 等</p>
            </div>
        </section>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- 快捷任务 -->
            <section class="lg:col-span-2 space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
                        <h3 class="font-bold flex items-center">
                            <i class="fas fa-terminal mr-2 text-blue-500"></i>
                            任务控制台
                        </h3>
                    </div>
                    <div class="p-6 space-y-4">
                        <div class="flex space-x-3">
                            <input id="task-input" type="text" placeholder="输入任务指令，例如: RUN: ls" 
                                   class="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none transition-all">
                            <button onclick="runTask()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-3 rounded-xl shadow-lg shadow-blue-200 transition-all flex items-center">
                                <i class="fas fa-paper-plane mr-2"></i> 执行
                            </button>
                        </div>
                        <div id="task-result" class="hidden bg-slate-900 text-green-400 p-4 rounded-xl font-mono text-sm min-h-[100px] whitespace-pre-wrap"></div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:border-blue-200 transition-all group">
                        <i class="fas fa-shield-halved text-2xl text-blue-500 mb-4"></i>
                        <h4 class="font-bold text-lg mb-2">权限管理</h4>
                        <p class="text-slate-500 text-sm mb-4">管理 Telegram 用户白名单与授权代码。</p>
                        <button class="text-blue-600 font-semibold text-sm group-hover:underline">前往配置 →</button>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:border-blue-200 transition-all group">
                        <i class="fas fa-bolt text-2xl text-yellow-500 mb-4"></i>
                        <h4 class="font-bold text-lg mb-2">极速模式</h4>
                        <p class="text-slate-500 text-sm mb-4">跳过 TS 检查直接启动 OpenClaw。</p>
                        <button class="text-blue-600 font-semibold text-sm group-hover:underline">立即启动 →</button>
                    </div>
                </div>
            </section>

            <!-- 配置预览 -->
            <section class="space-y-6">
                <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div class="px-6 py-4 border-b border-slate-100">
                        <h3 class="font-bold flex items-center">
                            <i class="fas fa-key mr-2 text-blue-500"></i>
                            API 状态
                        </h3>
                    </div>
                    <div class="p-6 space-y-4">
                        {% for key, status in env_status.items() %}
                        <div class="flex justify-between items-center">
                            <span class="text-sm font-medium text-slate-600">{{ key }}</span>
                            {% if status %}
                            <span class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold">已配置</span>
                            {% else %}
                            <span class="bg-red-100 text-red-700 text-xs px-2 py-1 rounded-full font-bold">未配置</span>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="bg-gradient-to-br from-blue-600 to-blue-700 p-6 rounded-2xl shadow-xl text-white">
                    <h3 class="font-bold text-lg mb-2">Clawdbot 插件模式</h3>
                    <p class="text-blue-100 text-sm mb-6">OmniGate 目前作为 Clawdbot 的核心增强插件运行，已自动接管本地技能与 Token 压缩。</p>
                    <a href="/docs" target="_blank" class="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-bold transition-all block text-center">
                        查看开发者 API 文档
                    </a>
                </div>
            </section>
        </div>
    </main>

    <script>
        async function runTask() {
            const input = document.getElementById('task-input');
            const resultDiv = document.getElementById('task-result');
            const task = input.value;
            if (!task) return;

            resultDiv.classList.remove('hidden');
            resultDiv.innerText = '正在执行...';

            try {
                const response = await fetch('/offload', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task: task})
                });
                const data = await response.json();
                resultDiv.innerText = data.data || data.detail || '执行成功';
            } catch (err) {
                resultDiv.innerText = '发生错误: ' + err.message;
            }
        }
    </script>
</body>
</html>
"""

class TaskRequest(BaseModel):
    task: str

class ContextRequest(BaseModel):
    context: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 读取环境变量状态
    env_keys = ["DEEPSEEK_API_KEY", "TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "CLAUDE_API_KEY"]
    env_status = {key: bool(os.getenv(key)) for key in env_keys}
    
    return HTML_TEMPLATE.replace("{{ cpu }}", str(psutil.cpu_percent()))\
                        .replace("{{ mem }}", str(psutil.virtual_memory().percent))\
                        .replace("{{ adapters_count }}", str(len(api_engine._adapters)))\
                        .replace("{% for key, status in env_status.items() %}", "")\
                        .replace("{% endfor %}", "") # 简单替换，不使用真正的 Jinja 以避免额外依赖

@app.post("/offload")
async def offload(req: TaskRequest):
    """任务卸载接口"""
    try:
        result = await omni_engine.execute_task(req.task)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/shrink")
async def shrink(req: ContextRequest):
    """Token 压缩接口"""
    summary = omni_engine.compress_context(req.context)
    return {"status": "success", "summary": summary}

@app.get("/health")
async def health():
    return {"status": "online", "mode": "lightweight"}

def run_api(port: int = 18789):
    # 注入环境变量以便仪表盘显示
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    os.environ[k.strip()] = v.strip()
                    
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    run_api()
