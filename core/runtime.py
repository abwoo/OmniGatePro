import time
import uuid
from datetime import datetime
from typing import Optional
from core.plan import ExecutionPlan
from core.trace import ExecutionTrace, TraceEntry, ActionStatus
from interfaces.backend import BackendAdapter
from core.intent import ArtIntent

# 导入数据库相关（可选）
try:
    from db.models import AgentExecution, ActionTrace, ExecutionStatus as DbStatus
    from sqlalchemy.orm import Session
    HAS_DB = True
except ImportError:
    HAS_DB = False

class Runtime:
    """
    Runtime 是 artfish 引擎的核心编排器。
    它负责加载执行计划，通过调度器分发任务，并全量记录执行轨迹（Lifecycle Management）。
    """
    def __init__(self, backend: BackendAdapter):
        self.backend = backend
        self.trace = ExecutionTrace()
        self.max_retries = 2  # 商业化：默认重试次数

    def run(self, plan: ExecutionPlan, intent: Optional[ArtIntent] = None, db_session: Optional[Any] = None, run_id: Optional[str] = None) -> ExecutionTrace:
        """
        按照计划顺序执行动作，并捕获所有状态变更。
        """
        active_run_id = run_id or str(uuid.uuid4())
        execution_record = None

        # 1. 数据库初始化或获取记录
        if HAS_DB and db_session and intent:
            # 尝试查找现有记录（由 API 预创建）
            execution_record = db_session.query(AgentExecution).filter(AgentExecution.run_id == active_run_id).first()
            
            if not execution_record:
                execution_record = AgentExecution(
                    run_id=active_run_id,
                    user_id=intent.user_id,
                    status=DbStatus.RUNNING,
                    intent_snapshot=intent.__dict__,
                    plan_snapshot={"actions_count": len(plan.actions)},
                    start_time=datetime.utcnow()
                )
                db_session.add(execution_record)
            else:
                # 更新现有记录
                execution_record.status = DbStatus.RUNNING
                execution_record.start_time = datetime.utcnow()
                
            db_session.commit()

        for action in plan.actions:
            retries = 0
            success = False
            last_error = None
            start_time = datetime.now()
            
            while retries <= self.max_retries and not success:
                try:
                    attempt_start_time = datetime.now()
                    response = self.backend.execute(action)
                    result = response.output
                    usage = response.usage
                    
                    # 成功记录
                    duration_ms = (datetime.now() - attempt_start_time).total_seconds() * 1000
                    cost = usage.cost
                    
                    entry = TraceEntry(
                        timestamp=datetime.now().isoformat(),
                        action_id=action.action_id,
                        status=ActionStatus.SUCCESS,
                        payload=result,
                        cost=cost,
                        metadata={
                            "retries": retries,
                            "duration_ms": duration_ms,
                            "model": usage.model_name,
                            "tokens": usage.total_tokens
                        }
                    )
                    success = True
                    self.trace.add_entry(entry)

                    # 2. 数据库更新动作记录
                    if HAS_DB and db_session and execution_record:
                        action_record = ActionTrace(
                            execution_id=execution_record.id,
                            action_id=action.action_id,
                            action_type=action.action_type,
                            status=DbStatus.SUCCESS,
                            input_params=action.params,
                            output_payload=result,
                            cost=cost,
                            duration_ms=duration_ms,
                            finished_at=datetime.utcnow()
                        )
                        db_session.add(action_record)
                        execution_record.total_cost += cost
                        db_session.commit()
                    
                except Exception as e:
                    last_error = str(e)
                    retries += 1
                    if retries > self.max_retries:
                        # 最终失败记录
                        entry = TraceEntry(
                            timestamp=datetime.now().isoformat(),
                            action_id=action.action_id,
                            status=ActionStatus.FAIL,
                            payload={"error": last_error},
                            metadata={"final_attempt": True, "total_retries": retries - 1}
                        )
                        self.trace.add_entry(entry)

                        # 3. 数据库记录失败动作
                        if HAS_DB and db_session and execution_record:
                            action_record = ActionTrace(
                                execution_id=execution_record.id,
                                action_id=action.action_id,
                                action_type=action.action_type,
                                status=DbStatus.FAIL,
                                input_params=action.params,
                                error_message=last_error,
                                finished_at=datetime.utcnow()
                            )
                            db_session.add(action_record)
                            db_session.commit()
        
        # 4. 完成执行记录
        if HAS_DB and db_session and execution_record:
            execution_record.status = DbStatus.SUCCESS if all(e.status == ActionStatus.SUCCESS for e in self.trace.entries) else DbStatus.FAILED
            execution_record.end_time = datetime.utcnow()
            db_session.commit()

        return self.trace
