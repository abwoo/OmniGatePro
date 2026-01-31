from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Dict, Optional
import json

class ActionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAIL = "fail"
    COMPLETED = "completed"

@dataclass(frozen=True)
class TraceEvent:
    timestamp: datetime
    action_id: str
    status: ActionStatus
    result_payload: Any
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionTrace:
    events: List[TraceEvent] = field(default_factory=list)

    def add_event(self, event: TraceEvent):
        self.events.append(event)

    def get_action_result(self, action_id: str) -> Optional[Dict[str, Any]]:
        for event in reversed(self.events):
            if event.action_id == action_id:
                return {
                    "status": event.status.value,
                    "result_payload": event.result_payload,
                    "metadata": event.metadata
                }
        return None

    def get_all_results(self) -> Dict[str, Any]:
        results = {}
        for event in self.events:
            results[event.action_id] = event.result_payload
        return results

    def get_events_by_action(self, action_id: str) -> List[TraceEvent]:
        return [e for e in self.events if e.action_id == action_id]

    def get_statistics(self) -> Dict[str, Any]:
        total_actions = len({e.action_id for e in self.events})
        completed = len({e.action_id for e in self.events if e.status in [ActionStatus.SUCCESS, ActionStatus.COMPLETED]})
        failed = len({e.action_id for e in self.events if e.status == ActionStatus.FAIL})
        
        return {
            "total_events": len(self.events),
            "total_actions": total_actions,
            "completed_actions": completed,
            "failed_actions": failed,
            "success_rate": (completed / total_actions * 100) if total_actions > 0 else 0,
            "duration_seconds": 0.0,
            "status_counts": {}
        }

    def to_json(self) -> str:
        data = []
        for e in self.events:
            d = e.__dict__.copy()
            d["status"] = e.status.value
            d["timestamp"] = e.timestamp.isoformat()
            data.append(d)
        return json.dumps(data, indent=2, ensure_ascii=False)
