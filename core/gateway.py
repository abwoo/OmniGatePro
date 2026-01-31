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

logger = logging.getLogger("artfish.studio.gateway")

class StudioGateway:
    """
    StudioGateway: Artfish Studio 的核心网关。
    支持多智能体协作协议 (Agent Collaboration Protocol)。
    """
    def __init__(self, skills_dir: str = "skills"):
        self.skill_manager = SkillManager(skills_dir=skills_dir)
        self.skill_manager.load_skills()
        
        self.trace = ExecutionTrace()
        self._context = ExecutionContext()
        self._active_projects: Dict[str, Dict] = {} # 存储活跃项目上下文

    def create_project(self, title: str, description: str) -> str:
        """创建一个新的艺术协作项目"""
        project_id = str(uuid.uuid4())[:8]
        self._active_projects[project_id] = {
            "title": title,
            "description": description,
            "agents": [],
            "canvas_state": {},
            "history": []
        }
        return project_id

    def join_agent(self, project_id: str, agent_id: str, role: str):
        """让一个 Agent 加入项目"""
        if project_id not in self._active_projects:
            raise ValueError(f"Project {project_id} not found")
        self._active_projects[project_id]["agents"].append({
            "id": agent_id,
            "role": role
        })
        logger.info(f"Agent {agent_id} joined project {project_id} as {role}")

    def execute_collaborative_task(self, project_id: str, from_agent: str, task_intent: ArtIntent):
        """
        执行一个协作任务。
        Agent 可以通过此方法向网关提交请求，网关根据技能系统路由到合适的处理逻辑。
        """
        # 1. 验证权限与项目
        if project_id not in self._active_projects:
            raise ValueError(f"Project {project_id} not found")
        
        # 2. 编译并运行
        plan = Compiler.compile(task_intent)
        trace = self.run_plan(plan)
        
        # 3. 更新项目历史
        self._active_projects[project_id]["history"].append({
            "agent": from_agent,
            "task": task_intent.goals,
            "result": trace.get_all_results(),
            "timestamp": datetime.now().isoformat()
        })
        
        return trace

    def run_plan(self, plan: ExecutionPlan) -> ExecutionTrace:
        """执行预定义的计划"""
        execution_order = plan.get_execution_order()
        for action in execution_order:
            self._execute_action(action)
        return self.trace

    def _execute_action(self, action: AtomicAction):
        """执行单个动作，优先通过艺术技能系统调度"""
        parts = action.action_id.split('_')
        if len(parts) >= 2:
            skill_name = parts[0]
            tool_name = "_".join(parts[1:])
        else:
            # 默认尝试艺术导师技能
            skill_name = "art_tutor"
            tool_name = "get_theory"

        try:
            params = self._context.inject_dependencies(
                action.action_id, 
                action.dependencies, 
                action.parameters
            )
            
            # 针对艺术教育场景的自动路由逻辑
            if skill_name == "action" or skill_name not in [s.name for s in self.skill_manager.list_skills()]:
                # 检查参数或目标中的关键字
                search_text = (str(params) + str(action.parameters)).lower()
                if any(k in search_text for k in ["critique", "review", "点评", "评审", "鉴赏"]):
                    skill_name = "art_critique"
                    tool_name = "critique_concept"
                elif any(k in search_text for k in ["color", "palette", "配色", "构图", "theory", "理论"]):
                    skill_name = "art_tutor"
                    tool_name = "suggest_color_palette" if "color" in search_text or "配色" in search_text else "get_theory"
                else:
                    skill_name = "art_tutor"
                    tool_name = "get_theory"

            result = self.skill_manager.execute(skill_name, tool_name, **params)
            
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

# 保持 Gateway 名称兼容性
Gateway = StudioGateway
