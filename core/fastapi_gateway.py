from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.omni_engine import omni_engine
import uvicorn

app = FastAPI(title="OmniGate REST API", description="Clawdbot Lightweight Plugin Bridge")

class TaskRequest(BaseModel):
    task: str

class ContextRequest(BaseModel):
    context: str

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
    uvicorn.run(app, host="127.0.0.1", port=port)

if __name__ == "__main__":
    run_api()
