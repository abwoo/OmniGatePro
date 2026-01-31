import importlib
import inspect
import os
import logging
from typing import Dict, List, Type
from core.skill import BaseSkill

logger = logging.getLogger("artfish.skills")

class SkillManager:
    """
    技能管理器：负责技能的发现、加载和生命周期管理。
    对齐 Clawdbot 的 ClawHub 设计理念。
    """
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self._skills: Dict[str, BaseSkill] = {}
        
        # 确保技能目录存在
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            with open(os.path.join(self.skills_dir, "__init__.py"), "w") as f:
                pass

    def load_skills(self):
        """
        自动从 skills 目录加载所有技能。
        """
        logger.info(f"Scanning for skills in {self.skills_dir}...")
        
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"{self.skills_dir}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # 重新加载模块以防更新
                    importlib.reload(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseSkill) and 
                            obj is not BaseSkill):
                            
                            skill_instance = obj()
                            self._skills[skill_instance.name] = skill_instance
                            logger.info(f"Loaded skill: {skill_instance.name}")
                            
                except Exception as e:
                    logger.error(f"Failed to load skill from {module_name}: {e}")

    def get_skill(self, name: str) -> BaseSkill:
        return self._skills.get(name)

    def list_skills(self) -> List[BaseSkill]:
        return list(self._skills.values())

    def get_all_tools_metadata(self) -> List[Dict]:
        """
        汇总所有已加载技能的工具元数据。
        """
        all_metadata = []
        for skill in self._skills.values():
            all_metadata.extend(skill.get_tools_metadata())
        return all_metadata

    def execute(self, skill_name: str, tool_name: str, **kwargs):
        """
        分发执行请求到具体的技能工具。
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")
        return skill.execute_tool(tool_name, **kwargs)
