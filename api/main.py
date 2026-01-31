from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import os
import logging

from core.config import settings

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("artfish.api")

app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.VERSION,
    description="Artfish Runtime Engine API - High-performance intent execution platform."
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error", "message": str(exc) if settings.DEBUG else "Please contact support"}
    )

# CORS Support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: Get Database Session (Lazy Import)
def get_db():
    from db.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Data Models
class IntentRequest(BaseModel):
    goals: List[str]
    constraints: Dict[str, Any] = {}
    priority: int = 0
    backend_config: Optional[Dict[str, Any]] = None

class ExecutionResponse(BaseModel):
    run_id: str
    status: str
    message: str

# --- API Routes ---

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Artfish Runtime Engine is Online",
        "docs": "/docs",
        "version": settings.VERSION,
        "status": "healthy"
    }

@app.get("/health", summary="Health Check", description="Verify the server is running.")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION
    }

@app.post("/v1/execute", response_model=ExecutionResponse, summary="Submit Task", description="Submit a new intent execution task.")
async def execute_intent(
    request: IntentRequest, 
    db: Any = Depends(get_db)
):
    from db.models import AgentExecution, ExecutionStatus
    from core.worker import run_agent_task_celery
    
    run_id = str(uuid.uuid4())
    try:
        execution = AgentExecution(
            run_id=run_id,
            status=ExecutionStatus.PENDING,
            intent_snapshot=request.model_dump(),
            start_time=None
        )
        db.add(execution)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during task submission: {e}")
        raise HTTPException(status_code=500, detail="Failed to record task in database")

    # Submit Task
    run_agent_task_celery.delay(run_id, request.model_dump())
    
    return {
        "run_id": run_id,
        "status": "accepted",
        "message": "Task has been accepted and queued."
    }

@app.get("/v1/execution/{run_id}", summary="Get Task Status", description="Retrieve the current status of an execution task.")
async def get_execution_status(
    run_id: str, 
    db: Any = Depends(get_db)
):
    from db.models import AgentExecution
    execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
        
    return {
        "run_id": execution.run_id,
        "status": execution.status.value,
        "start_time": execution.start_time,
        "end_time": execution.end_time,
        "actions_count": len(execution.actions)
    }

@app.get("/v1/execution/{run_id}/report", summary="Download Report", description="Download the execution report (PDF or JSON).")
async def download_report(
    run_id: str, 
    type: str = "pdf", 
    db: Any = Depends(get_db)
):
    from db.models import AgentExecution
    execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    ext = "pdf" if type == "pdf" else "json"
    prefix = "report" if type == "pdf" else "trace"
    file_path = os.path.join(settings.EXPORT_DIR, f"{prefix}_{run_id}.{ext}")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not ready")
    
    return FileResponse(file_path, filename=f"artfish_{run_id}.{ext}")

if __name__ == "__main__":
    import uvicorn
    # Initialize DB only when running as main
    from db.session import init_db
    init_db()
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=8000)
