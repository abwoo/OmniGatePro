from celery import Celery
from core.config import settings
import logging
import os

# Initialize Celery
# If FORCE_SYNC_EXECUTION is True, we configure Celery to be memory-based and eager
if settings.FORCE_SYNC_EXECUTION:
    broker_url = 'memory://'
    result_backend = 'cache+memory://'
else:
    broker_url = settings.REDIS_URL
    result_backend = settings.REDIS_URL

celery_app = Celery(
    "artfish",
    broker=broker_url,
    backend=result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
)

if settings.FORCE_SYNC_EXECUTION:
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True
    )

logger = logging.getLogger("artfish.worker")

@celery_app.task(name="artfish.run_agent_task", bind=True, max_retries=3)
def run_agent_task_celery(self, run_id: str, intent_data: dict):
    """
    Execute Agent task asynchronously using Celery.
    """
    from db.session import SessionLocal
    from core.intent import ArtIntent
    from core.plan import Compiler
    from core.gateway import Gateway
    from core.exporter import Exporter
    from db.models import AgentExecution, ExecutionStatus
    
    logger.info(f"Celery task started for run_id: {run_id}")
    db = SessionLocal()
    try:
        # 1. Reconstruct Intent
        intent = ArtIntent(
            goals=intent_data["goals"],
            constraints=intent_data["constraints"],
            priority=intent_data["priority"]
        )
        
        # 2. Compile Plan
        plan = Compiler.compile(intent)
        
        # 3. Run Gateway
        gateway = Gateway()
        trace = gateway.run_plan(plan)
        
        # 4. Export Results
        json_path = os.path.join(settings.EXPORT_DIR, f"trace_{run_id}.json")
        pdf_path = os.path.join(settings.EXPORT_DIR, f"report_{run_id}.pdf")
        Exporter.export_json(trace, json_path)
        Exporter.export_pdf(trace, pdf_path)
        
        # 5. Update Status
        execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
        if execution:
            execution.status = ExecutionStatus.SUCCESS
            db.commit()
        
        return {"status": "success", "run_id": run_id}
        
    except Exception as e:
        logger.error(f"Task {run_id} failed: {str(e)}", exc_info=True)
        # Update DB status to FAIL
        try:
            execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
            if execution:
                execution.status = ExecutionStatus.FAIL
                db.commit()
        except Exception as e:
            logger.error(f"Failed to record error status in DB: {e}")
        # In eager mode, we don't want to retry or raise, just log
        if not settings.FORCE_SYNC_EXECUTION:
            raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
