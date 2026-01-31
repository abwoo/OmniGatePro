from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class AtomicAction:
    """
    AtomicAction 是执行系统中的最小工作单元。
    它代表了一个将被 BackendAdapter 处理的具体操作。
    """
    action_id: str
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionPlan:
    """
    ExecutionPlan 是由 Compiler 编译生成的动作序列或有向无环图 (DAG)。
    它作为 Runtime 执行的蓝图，定义了任务的执行顺序。
    """
    actions: List[AtomicAction] = field(default_factory=list)

class Compiler:
    """
    Compiler 负责将抽象的 ArtIntent 转换为具体的 ExecutionPlan。
    它封装了将高层目标映射到原子操作的业务逻辑。
    """
    @staticmethod
    def compile(intent: 'ArtIntent') -> ExecutionPlan:
        # 教学演示：将每个目标简单映射为一个生成动作
        actions = []
        for i, goal in enumerate(intent.goals):
            actions.append(AtomicAction(
                action_id=f"action_{i:03d}",
                action_type="generate_artifact",
                params={"goal": goal, **intent.constraints}
            ))
        return ExecutionPlan(actions=actions)
