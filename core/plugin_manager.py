import yaml
import logging
import os
from typing import Dict, Any, List, Callable
from core.skill import BaseSkill, skill_tool

logger = logging.getLogger("artfish.core.plugin_manager")

class CustomCommandManager(BaseSkill):
    """
    用户自定义功能扩展框架。
    允许通过 plugins/custom_commands.yaml 动态添加指令。
    """
    name = "custom_manager"
    description = "Manages user-defined custom commands and plugins."

    def __init__(self, config_path: str = "plugins/custom_commands.yaml"):
        super().__init__()
        self.config_path = config_path
        self._commands: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump({"hello": {"template": "你好！这是一个自定义指令示例。"}}, f)
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._commands = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load custom commands: {e}")

    @skill_tool(description="执行自定义指令")
    def execute_custom(self, command_name: str, args: List[str] = []) -> str:
        if command_name not in self._commands:
            return f"❌ 未找到自定义指令：{command_name}"
        
        config = self._commands[command_name]
        template = config.get("template", "指令执行成功。")
        
        # 简单变量替换
        result = template.format(args=" ".join(args))
        return result

    def register_command(self, name: str, template: str):
        """动态注册新指令"""
        self._commands[name] = {"template": template}
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self._commands, f)
        return f"✅ 指令 /{name} 注册成功。"
