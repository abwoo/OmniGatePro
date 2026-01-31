from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class ArtIntent:
    """
    Structured representation of user intent.
    Contains high-level goals and constraints for the generation task.
    """
    goals: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
