from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.omni_engine import omni_engine
from core.api_engine import api_engine
from core.token_tracker import token_tracker
import uvicorn
import os
import psutil
import platform
import json

app = FastAPI(title="OmniGate Pro REST API", description="Clawdbot 增强插件后端接口")

# --- 数据模型 ---
class TaskRequest(BaseModel):
    task: str

class ContextRequest(BaseModel):
    context: str
    provider: str = "deepseek"
    scene: str = "general"

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
    native_skills = []
    native_dir = os.path.join("openclaw", "skills")
    if os.path.exists(native_dir):
        try:
            native_skills = [{"id": item, "type": "native"} for item in os.listdir(native_dir) if os.path.isdir(os.path.join(native_dir, item))]
        except: pass
    
    dynamic_skills = []
    dynamic_dir = "skills"
    if os.path.exists(dynamic_dir):
        try:
            dynamic_skills = [{"id": f.replace(".py", ""), "type": "omni_pro"} for f in os.listdir(dynamic_dir) if f.endswith(".py") and f != "__init__.py"]
        except: pass
        
    return native_skills + dynamic_skills

# --- API 接口 ---
@app.get("/api/status")
async def get_status():
    config = get_openclaw_config()
    token_stats = token_tracker.get_summary()
    return {
        "cpu": psutil.cpu_percent(),
        "mem": psutil.virtual_memory().percent,
        "platform": platform.system(),
        "version": "v3.0.0",
        "agents": config.get("agents", {}).get("list", ["main"]),
        "channels": [k for k, v in config.get("channels", {}).items() if v.get("enabled")],
        "skills_count": len(get_bundled_skills()),
        "token_savings_rate": token_stats["savings_rate"],
        "total_saved": token_stats["total_saved"]
    }

@app.get("/api/token/stats")
async def get_token_stats():
    return JSONResponse(content=token_tracker.get_summary())

@app.get("/api/skills")
async def get_skills():
    return JSONResponse(content=get_bundled_skills())

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
    summary = omni_engine.compress_context(req.context, provider=req.provider, scene=req.scene)
    return {"status": "success", "summary": summary}

@app.get("/health")
async def health():
    return {"status": "online", "mode": "lightweight"}

def run_api(port: int = 18789):
    # 注入环境变量以便内部逻辑读取
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        k, v = parts[0].strip(), parts[1].strip()
                        os.environ[k] = v
                    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    run_api()
