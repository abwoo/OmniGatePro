import yaml
import logging
import re
from typing import Dict, Any, List, Optional
from core.skill import BaseSkill, skill_tool

logger = logging.getLogger("artfish.core.custom_framework")

class CustomSkillFramework(BaseSkill):
    """
    用户自定义功能扩展框架。
    支持基于 YAML 配置的指令扩展，包含安全校验与参数沙箱处理。
    """
    name = "custom_framework"
    description = "Framework for defining personal commands via config."

    def __init__(self, config_path: str = "custom_commands.yaml"):
        super().__init__()
        self.config_path = config_path
        self.commands: Dict[str, Any] = self._load_commands()

    def _load_commands(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f) or {}
                # 简单验证
                validated = {}
                for name, cfg in content.items():
                    if isinstance(cfg, dict) and "template" in cfg:
                        validated[name] = cfg
                return validated
        except FileNotFoundError:
            logger.info(f"Custom config {self.config_path} not found, starting fresh.")
            return {}
        except Exception as e:
            logger.error(f"Failed to parse custom commands: {e}")
            return {}

    def _save_commands(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.commands, f, allow_unicode=True)
        except Exception as e:
            logger.error(f"Failed to save custom commands: {e}")

    @skill_tool(description="执行自定义扩展指令")
    def execute_custom(self, cmd_name: str, args: List[str]) -> str:
        """
        在受控环境中执行自定义逻辑。
        """
        cmd_cfg = self.commands.get(cmd_name)
        if not cmd_cfg:
            return f"❌ 指令 /{cmd_name} 未定义。"

        template = cmd_cfg.get("template", "")
        
        # 安全沙箱：限制可用的变量替换
        # 目前仅支持 {args} (全部参数) 和 {1}, {2}... (特定位置参数)
        result = template
        try:
            # 替换全量参数
            result = result.replace("{args}", " ".join(args))
            
            # 替换位置参数
            for i, val in enumerate(args):
                result = result.replace(f"{{{i+1}}}", val)
                
            # 清理未匹配的占位符，防止信息泄露
            result = re.sub(r"\{\d+\}", "", result)
            
            return f"✨ [自定义扩展]：\n{result}"
        except Exception as e:
            logger.error(f"Error executing custom command {cmd_name}: {e}")
            return "❌ 自定义指令执行时发生内部错误。"

    @skill_tool(description="添加或更新自定义指令。用法：/add_cmd cmd_name template")
    def add_command(self, name: str, template: str) -> str:
        """支持在线动态添加指令"""
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            return "❌ 错误：指令名称仅能包含字母、数字和下划线。"
        
        if len(template) > 500:
            return "❌ 错误：模板内容过长（最大 500 字符）。"

        self.commands[name] = {"template": template}
        self._save_commands()
        return f"✅ 自定义指令 /{name} 已就绪。模板内容：\n`{template}`"

    @skill_tool(description="列出所有自定义指令")
    def list_custom_commands(self) -> str:
        if not self.commands:
            return "📋 当前暂无自定义指令。使用 /add_cmd 创建一个吧！"
        
        names = "\n".join([f"- /{n}" for n in self.commands.keys()])
        return f"📜 *当前自定义指令列表*：\n{names}"
