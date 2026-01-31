import time
import uuid
import logging
from datetime import datetime
from typing import Optional, Any, List, Dict

from core.plan import ExecutionPlan, AtomicAction, Compiler
from core.trace import ExecutionTrace, TraceEvent, ActionStatus
from core.intent import ArtIntent
from core.context import ExecutionContext
from core.skill_manager import SkillManager

logger = logging.getLogger("artfish.gateway")

class Gateway:
    """
    Gateway 是 Artfish 引擎的中枢系统（对齐 Clawdbot Gateway）。
    它负责管理会话、调度技能 (Skills)、并处理执行轨迹。
    """
    def __init__(self, skills_dir: str = "skills"):
        self.skill_manager = SkillManager(skills_dir=skills_dir)
        self.skill_manager.load_skills()
        
        self.trace = ExecutionTrace()
        self._context = ExecutionContext()
        self._sessions: Dict[str, Dict] = {}

    def get_all_tools(self) -> List[Dict]:
        """返回所有可用的工具元数据"""
        return self.skill_manager.get_all_tools_metadata()

    def execute_intent(self, intent: ArtIntent) -> ExecutionTrace:
        """
        执行用户意图：编译计划并运行。
        """
        plan = Compiler.compile(intent)
        return self.run_plan(plan)

    def run_plan(self, plan: ExecutionPlan) -> ExecutionTrace:
        """
        执行预定义的计划。
        """
        # 验证计划
        is_valid, error = plan.validate()
        if not is_valid:
            raise ValueError(f"Invalid plan: {error}")

        execution_order = plan.get_execution_order()
        
        for action in execution_order:
            self._execute_action(action)
            
        return self.trace

    def _execute_action(self, action: AtomicAction):
        """
        执行单个动作，优先通过技能系统调度。
        """
        logger.info(f"Executing action: {action.action_id}")
        
        # 尝试从 action_id 或 backend_hint 解析技能和工具
        # 格式通常为: skillName_toolName
        parts = action.action_id.split('_')
        if len(parts) >= 2:
            skill_name = parts[0]
            tool_name = "_".join(parts[1:])
        else:
            # 默认回退到 system 技能（如果存在）
            skill_name = "system"
            tool_name = action.action_id

        try:
            # 注入依赖
            params = self._context.inject_dependencies(
                action.action_id, 
                action.dependencies, 
                action.parameters
            )
            
            # 逻辑调整：如果是教育场景且没有明确技能前缀，尝试分发给 tutor
            if skill_name == "action" or skill_name not in [s.name for s in self.skill_manager.list_skills()]:
                # 尝试探测术语来决定技能
                detected = self.skill_manager.execute("tutor", "recognize_terms", text=action.parameters.get("query", ""))
                if detected["subject"] != "unknown":
                    skill_name = "tutor"
                    tool_name = "heuristic_tutor"
                else:
                    skill_name = "tutor" # 默认回退到辅导技能
                    tool_name = "heuristic_tutor"

            # 执行工具
            result = self.skill_manager.execute(skill_name, tool_name, **params)
            
            # 记录轨迹
            event = TraceEvent(
                timestamp=datetime.now(),
                action_id=action.action_id,
                status=ActionStatus.COMPLETED,
                result_payload=result,
                metadata={"skill": skill_name, "tool": tool_name}
            )
            self._context.store_result(event)
            self.trace.add_event(event)
            
        except Exception as e:
            logger.error(f"Action {action.action_id} failed: {e}")
            event = TraceEvent(
                timestamp=datetime.now(),
                action_id=action.action_id,
                status=ActionStatus.FAIL,
                result_payload={"error": str(e)},
                metadata={"skill": skill_name, "tool": tool_name}
            )
            self.trace.add_event(event)
            raise e
