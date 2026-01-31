from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class ArtIntent:
    """
    ArtIntent 将用户的原始创作欲望转化为结构化的声明对象。
    该类通过解耦意图与执行细节，确保系统仅处理经过验证的结构化输入。
    """
    goals: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    # 商业化字段：身份验证与配额控制
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    priority: int = 0  # 优先级，用于计费分级
