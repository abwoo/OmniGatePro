"""
ExecutionContext: 执行上下文管理。

这个模块实现了执行上下文，用于存储和管理操作执行过程中的
中间状态和结果。这是实现操作间数据传递和状态查询的核心。
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from .trace import TraceEntry, ActionStatus


@dataclass
class ActionResult:
    """
    操作结果：封装操作的执行结果。
    
    包含操作ID、执行状态、结果数据和元数据，用于在操作间传递数据。
    """
    action_id: str
    """操作ID"""
    
    status: ActionStatus
    """执行状态"""
    
    result_payload: Optional[Any] = None
    """结果负载"""
    
    error_message: Optional[str] = None
    """错误信息"""
    
    timestamp: Optional[str] = None
    """完成时间戳"""
    
    cost: float = 0.0
    """执行成本"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """元数据"""
    
    def is_successful(self) -> bool:
        """检查操作是否成功"""
        return self.status == ActionStatus.SUCCESS
    
    def get_result(self, key: Optional[str] = None) -> Any:
        """
        获取结果数据。
        
        Args:
            key: 可选的键，如果提供则返回result_payload中的特定值
            
        Returns:
            结果数据或特定键的值
        """
        if not self.result_payload:
            return None
        
        if key and isinstance(self.result_payload, dict):
            return self.result_payload.get(key)
        
        return self.result_payload


class ExecutionContext:
    """
    执行上下文：管理执行过程中的状态和结果。
    
    提供操作结果的存储、查询和传递功能，使得依赖的操作
    可以访问其依赖操作的结果。
    """
    
    def __init__(self):
        """初始化执行上下文"""
        self._results: Dict[str, ActionResult] = {}
        """操作结果字典，key为action_id"""
    
    def store_result(self, entry: TraceEntry) -> None:
        """
        存储操作结果。
        
        Args:
            entry: 追踪条目，包含操作的执行结果
        """
        # 如果 status 是 FAIL，payload 可能包含错误信息
        error_msg = None
        if entry.status == ActionStatus.FAIL and isinstance(entry.payload, dict):
            error_msg = entry.payload.get("error")

        result = ActionResult(
            action_id=entry.action_id,
            status=entry.status,
            result_payload=entry.payload,
            error_message=error_msg,
            timestamp=entry.timestamp,
            cost=entry.cost,
            metadata=entry.metadata
        )
        self._results[entry.action_id] = result
    
    def get_result(self, action_id: str) -> Optional[ActionResult]:
        """
        获取操作结果。
        
        Args:
            action_id: 操作ID
            
        Returns:
            操作结果，如果不存在则返回None
        """
        return self._results.get(action_id)
    
    def has_result(self, action_id: str) -> bool:
        """检查是否有指定操作的结果"""
        return action_id in self._results
    
    def get_dependency_results(self, dependency_ids: List[str]) -> Dict[str, ActionResult]:
        """
        获取多个依赖操作的结果。
        
        Args:
            dependency_ids: 依赖操作ID列表
            
        Returns:
            操作ID到结果的映射字典
        """
        results = {}
        for dep_id in dependency_ids:
            result = self.get_result(dep_id)
            if result:
                results[dep_id] = result
        return results
    
    def inject_dependencies(self, action_id: str, dependencies: List[str], 
                           parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        将依赖操作的结果注入到操作参数中。
        
        这个方法会：
        1. 获取所有依赖操作的结果
        2. 将结果注入到parameters中，使用特定的键名
        
        Args:
            action_id: 当前操作ID
            dependencies: 依赖操作ID列表
            parameters: 原始操作参数
            
        Returns:
            注入依赖结果后的参数字典
        """
        # 复制原始参数
        enriched_params = parameters.copy()
        
        # 获取依赖结果
        dep_results = self.get_dependency_results(dependencies)
        
        # 注入依赖结果
        for dep_id, result in dep_results.items():
            # 使用标准化的键名注入结果
            enriched_params[f"_dep_{dep_id}"] = result.result_payload
            enriched_params[f"_dep_{dep_id}_status"] = result.status.value
            enriched_params[f"_dep_{dep_id}_success"] = result.is_successful()
        
        # 注入所有依赖结果的汇总
        if dep_results:
            enriched_params["_dependencies"] = {
                dep_id: {
                    "status": result.status.value,
                    "success": result.is_successful(),
                    "result": result.result_payload
                }
                for dep_id, result in dep_results.items()
            }
        
        return enriched_params
    
    def get_all_results(self) -> Dict[str, ActionResult]:
        """获取所有操作结果"""
        return self._results.copy()
    
    def clear(self) -> None:
        """清空所有结果"""
        self._results.clear()
    
    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return f"ExecutionContext(results={len(self._results)})"
