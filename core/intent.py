from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class ArtIntent:
    """
    ArtIntent 是用户意图的结构化表达。
    它包含了生成艺术作品所需的所有高层目标、约束条件以及商业上下文。
    """
    goals: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = "anonymous"
    metadata: Dict[str, Any] = field(default_factory=dict)
