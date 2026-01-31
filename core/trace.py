from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Dict
import json

class ActionStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

@dataclass(frozen=True)
class TraceEntry:
    """
    TraceEntry 是单个执行事件的不可变记录。
    它记录了决策的路径、成本以及最终结果。
    """
    timestamp: str
    action_id: str
    status: ActionStatus
    payload: Any
    cost: float = 0.0
    unit: str = "USD"  # 计费单位
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionTrace:
    """
    ExecutionTrace 是系统的不可变账本。
    它是 artfish 运行时的主要产出，记录了从开始到结束的所有执行细节。
    """
    entries: List[TraceEntry] = field(default_factory=list)

    def add_entry(self, entry: TraceEntry):
        self.entries.append(entry)

    @property
    def total_cost(self) -> float:
        """商业统计：计算总成本"""
        return sum(e.cost for e in self.entries)

    def to_dict(self) -> List[Dict[str, Any]]:
        return [
            {
                **e.__dict__,
                "status": e.status.value
            } for e in self.entries
        ]

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
