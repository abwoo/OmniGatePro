import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Type

def skill_tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    装饰器：将类方法标记为可被 AI 调用的工具。
    """
    def decorator(func: Callable):
        func._is_skill_tool = True
        func._tool_name = name or func.__name__
        func._tool_description = description or (func.__doc__ or "").strip()
        
        # 获取参数签名
        sig = inspect.signature(func)
        func._tool_args = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            func._tool_args[param_name] = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                "default": param.default if param.default != inspect.Parameter.empty else None,
                "required": param.default == inspect.Parameter.empty
            }
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

class BaseSkill:
    """
    所有 Artfish 技能的基类。
    对齐 Clawdbot 的模块化插件设计。
    """
    name: str = "base_skill"
    description: str = "Base class for all skills"

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._scan_tools()

    def _scan_tools(self):
        """
        扫描类中所有被 @skill_tool 装饰的方法。
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "_is_skill_tool"):
                tool_name = attr._tool_name
                self._tools[tool_name] = attr

    def get_tools_metadata(self) -> List[Dict[str, Any]]:
        """
        返回该技能下所有工具的元数据，用于暴露给 MCP 或 LLM。
        """
        metadata = []
        for name, tool in self._tools.items():
            metadata.append({
                "name": f"{self.name}_{name}",
                "description": tool._tool_description,
                "parameters": tool._tool_args,
                "skill": self.name
            })
        return metadata

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        执行指定的工具。
        """
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not found in skill '{self.name}'")
        return self._tools[tool_name](**kwargs)
