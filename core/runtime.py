import time
import uuid
from datetime import datetime
from typing import Optional, Any, List
from core.plan import ExecutionPlan, AtomicAction, Compiler
from core.trace import ExecutionTrace, TraceEvent, ActionStatus
from interfaces.backend import BackendAdapter
from core.intent import ArtIntent

# 导入数据库相关（可选）
try:
    from db.models import AgentExecution, ActionTrace, ExecutionStatus as DbStatus
    from sqlalchemy.orm import Session
    HAS_DB = True
except ImportError:
    HAS_DB = False

from concurrent.futures import ThreadPoolExecutor
from core.context import ExecutionContext

class Runtime:
    """
    Runtime 是 artfish 引擎的核心编排器。
    它负责加载执行计划，通过调度器分发任务，并全量记录执行轨迹（Lifecycle Management）。
    """
    def __init__(self, enable_parallel: bool = False, max_workers: int = 4, max_retries: int = 2):
        self._dispatcher = None # 后续由 register_backend 设置
        self.trace = ExecutionTrace()
        self._max_retries = max_retries
        self._enable_parallel = enable_parallel
        self._max_workers = max_workers
        self._context = ExecutionContext()
        self._backends = {}

    def register_backend(self, backend: BackendAdapter):
        self._backends[backend.name] = backend
        # 兼容旧代码，如果没有 dispatcher 则简单模拟
        if not self._dispatcher:
            class MockDispatcher:
                def __init__(self, backends): self.backends = backends
                def list_backends(self): return list(self.backends.keys())
                def get_backend(self, name): return self.backends.get(name)
            self._dispatcher = MockDispatcher(self._backends)

    def get_context(self):
        return self._context

    def compile(self, intent: ArtIntent, auto_dependencies: bool = False) -> ExecutionPlan:
        return Compiler.compile(intent, auto_dependencies=auto_dependencies)

    def run(self, plan: ExecutionPlan, intent: Optional[ArtIntent] = None, db_session: Optional[Any] = None, run_id: Optional[str] = None) -> ExecutionTrace:
        """
        按照计划顺序执行动作，并捕获所有状态变更。
        """
        active_run_id = run_id or str(uuid.uuid4())
        
        # 1. 验证计划
        is_valid, error = plan.validate()
        if not is_valid:
            raise ValueError(f"Invalid plan: {error}")

        # 2. 获取执行顺序
        execution_order = plan.get_execution_order()
        
        # 3. 执行逻辑
        if self._enable_parallel:
            self._run_parallel(execution_order)
        else:
            self._run_sequential(execution_order)
            
        return self.trace

    def _run_sequential(self, actions: List[AtomicAction]):
        for action in actions:
            self._execute_action_with_retry(action)

    def _run_parallel(self, actions: List[AtomicAction]):
        # 简化版并行：目前仅支持无依赖的并行，复杂DAG并行需更高级调度
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            executor.map(self._execute_action_with_retry, actions)

    def _execute_action_with_retry(self, action: AtomicAction):
        retries = 0
        success = False
        
        # 选择后端
        backend_name = action.backend_hint or list(self._backends.keys())[0]
        backend = self._backends.get(backend_name)
        
        while retries <= self._max_retries and not success:
            try:
                # 注入上下文依赖
                params = self._context.inject_dependencies(
                    action.action_id, 
                    action.dependencies, 
                    action.parameters
                )
                
                # 执行
                response = backend.execute(action) # 这里假设 backend.execute 能处理 AtomicAction
                
                # 记录结果到上下文
                from core.trace import TraceEvent, ActionStatus
                event = TraceEvent(
                    timestamp=datetime.now(),
                    action_id=action.action_id,
                    status=ActionStatus.COMPLETED,
                    result_payload=response.output,
                    cost=response.usage.cost,
                    metadata={"backend": backend_name, "retries": retries}
                )
                self._context.store_result(event)
                self.trace.add_event(event)
                success = True
                
            except Exception as e:
                retries += 1
                if retries > self._max_retries:
                    from core.trace import TraceEvent, ActionStatus
                    event = TraceEvent(
                        timestamp=datetime.now(),
                        action_id=action.action_id,
                        status=ActionStatus.FAILED,
                        result_payload={"error": str(e)},
                        metadata={"retries": retries-1}
                    )
                    self.trace.add_event(event)
