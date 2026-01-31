from celery import Celery
from core.config import settings
import logging
import os

# 初始化 Celery
celery_app = Celery(
    "artfish",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# 配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
)

logger = logging.getLogger("artfish.worker")

@celery_app.task(name="artfish.run_agent_task", bind=True, max_retries=3)
def run_agent_task_celery(self, run_id: str, intent_data: dict):
    """
    使用 Celery 异步执行 Agent 任务。
    """
    from db.session import SessionLocal
    from core.intent import ArtIntent
    from core.plan import Compiler
    from core.runtime import Runtime
    from interfaces.factory import BackendFactory
    from core.exporter import Exporter
    from db.models import AgentExecution, ExecutionStatus, UserAccount
    from datetime import datetime

    logger.info(f"Celery task started for run_id: {run_id}")
    db = SessionLocal()
    try:
        # 1. 重建意图
        intent = ArtIntent(
            goals=intent_data["goals"],
            constraints=intent_data["constraints"],
            user_id=intent_data["user_id"],
            priority=intent_data["priority"]
        )
        
        # 2. 编译计划
        plan = Compiler.compile(intent)
        
        # 3. 运行引擎
        # 商业化：从 intent_data 中获取用户自定义的 backend_config
        backend_config = intent_data.get("backend_config") or {"type": "mock"}
        backend = BackendFactory.create_backend(backend_config)
        
        runtime = Runtime(backend)
        trace = runtime.run(plan, intent=intent, db_session=db, run_id=run_id)
        
        # 4. 导出结果
        json_path = os.path.join(settings.EXPORT_DIR, f"trace_{run_id}.json")
        pdf_path = os.path.join(settings.EXPORT_DIR, f"report_{run_id}.pdf")
        Exporter.export_json(trace, json_path)
        Exporter.export_pdf(trace, pdf_path, user_id=intent.user_id)
        
        # 5. 商业化：扣费逻辑
        user = db.query(UserAccount).filter(UserAccount.user_id == intent.user_id).first()
        if user:
            user.balance -= trace.total_cost
            user.total_spent += trace.total_cost
            db.commit()
            logger.info(f"Deducted {trace.total_cost:.4f} USD from {user.user_id}. Remaining: {user.balance:.4f}")
        
        return {"status": "success", "run_id": run_id, "cost": trace.total_cost}
        
    except Exception as e:
        logger.error(f"Task {run_id} failed: {str(e)}", exc_info=True)
        # 更新数据库状态为失败
        try:
            execution = db.query(AgentExecution).filter(AgentExecution.run_id == run_id).first()
            if execution:
                execution.status = ExecutionStatus.FAIL
                db.commit()
        except Exception as e:
            logger.error(f"Failed to record error status in DB: {e}")
            # 即使数据库更新失败，也要让 Celery 知道任务失败了
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
