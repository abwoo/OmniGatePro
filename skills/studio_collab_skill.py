from typing import List, Dict, Any, Optional
from core.skill import BaseSkill, skill_tool

class StudioCollabSkill(BaseSkill):
    """
    协作技能：实现 Agent 间的任务转交与项目管理
    """
    name = "studio_collab"
    description = "Collaborative studio skill for agent-to-agent interaction and project management."

    @skill_tool(description="将任务转交给另一个角色的 Agent")
    def handoff_task(self, task_id: str, target_role: str, context: Dict[str, Any]) -> str:
        return f"任务 {task_id} 已成功转交给角色 [{target_role}]。当前进度已同步至协作上下文。"

    @skill_tool(description="请求其他 Agent 对当前进展进行反馈")
    def request_agent_feedback(self, project_id: str, from_agent: str, query: str) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "status": "pending_feedback",
            "message": f"来自 Agent [{from_agent}] 的反馈请求已发出：{query}"
        }

    @skill_tool(description="同步项目状态到共享画布/上下文")
    def sync_project_state(self, project_id: str, updates: Dict[str, Any]) -> str:
        return f"项目 {project_id} 的最新状态已同步。更新项：{list(updates.keys())}"
