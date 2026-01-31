from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

class ActionType(Enum):
    GENERATE = "generate"
    TRANSFORM = "transform"
    FILTER = "filter"
    COMPOSE = "compose"
    EXPORT = "export"

@dataclass(frozen=True)
class AtomicAction:
    action_id: str
    action_type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    backend_hint: Optional[str] = None

@dataclass
class ExecutionPlan:
    plan_id: str
    actions: List[AtomicAction] = field(default_factory=list)

    def validate(self) -> (bool, Optional[str]):
        # 简单的循环依赖检测和依赖存在性检查
        action_ids = {a.action_id for a in self.actions}
        for action in self.actions:
            for dep in action.dependencies:
                if dep not in action_ids:
                    return False, f"Action {action.action_id} depends on non-existent {dep}"
        return True, None

    def get_execution_order(self) -> List[AtomicAction]:
        # 拓扑排序 (Kahn's algorithm)
        in_degree = {a.action_id: 0 for a in self.actions}
        adj = {a.action_id: [] for a in self.actions}
        for a in self.actions:
            for dep in a.dependencies:
                adj[dep].append(a.action_id)
                in_degree[a.action_id] += 1
        
        queue = [a.action_id for a in self.actions if in_degree[a.action_id] == 0]
        order = []
        
        while queue:
            u_id = queue.pop(0)
            u = next(a for a in self.actions if a.action_id == u_id)
            order.append(u)
            for v_id in adj[u_id]:
                in_degree[v_id] -= 1
                if in_degree[v_id] == 0:
                    queue.append(v_id)
        
        return order

class Compiler:
    @staticmethod
    def compile(intent: 'ArtIntent', auto_dependencies: bool = False) -> ExecutionPlan:
        actions = []
        prev_id = None
        for i, goal in enumerate(intent.goals):
            action_id = f"action_{i}"
            # 简单的逻辑：如果包含 transform 则为 transform，否则为 generate
            a_type = ActionType.GENERATE
            if "transform" in goal.lower():
                a_type = ActionType.TRANSFORM
            elif "filter" in goal.lower():
                a_type = ActionType.FILTER
            
            deps = []
            if auto_dependencies and prev_id:
                deps = [prev_id]
            
            actions.append(AtomicAction(
                action_id=action_id,
                action_type=a_type,
                parameters={"goal": goal},
                dependencies=deps
            ))
            prev_id = action_id
            
        return ExecutionPlan(plan_id=str(uuid.uuid4()), actions=actions)
