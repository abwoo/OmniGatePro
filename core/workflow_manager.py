import yaml
import os
import logging
from typing import List, Dict, Any
from core.omni_engine import omni_orchestrator

logger = logging.getLogger("omni.workflows")

class WorkflowManager:
    """
    工作流管理器：支持基于 YAML 的标准化任务流 (Smartphone-like UX)。
    """
    def __init__(self, workflows_dir: str = "core/workflows"):
        self.workflows_dir = workflows_dir
        self.workflows: Dict[str, Dict] = {}
        self._load_workflows()

    def _load_workflows(self):
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)
        
        # 如果目录为空，创建一个默认示例
        if not os.listdir(self.workflows_dir):
            self._create_sample_workflow()

        for filename in os.listdir(self.workflows_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(os.path.join(self.workflows_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        data = yaml.safe_load(f)
                        if "name" in data:
                            self.workflows[data["name"]] = data
                    except Exception as e:
                        logger.error(f"Failed to load workflow {filename}: {e}")

    def _create_sample_workflow(self):
        sample = {
            "name": "system_check",
            "description": "一键进行系统环境自检与报告生成",
            "steps": [
                {"action": "system.get_info", "params": {}},
                {"action": "file.list", "params": {"path": "."}},
                {"action": "omni.speak", "params": {"template": "系统状态良好，当前工作目录包含 {data} 个文件。"}}
            ]
        }
        with open(os.path.join(self.workflows_dir, "sample.yaml"), 'w', encoding='utf-8') as f:
            yaml.dump(sample, f)
        # 立即加载到内存
        self.workflows[sample["name"]] = sample

    async def run_workflow(self, name: str) -> str:
        if name not in self.workflows:
            return f"错误：未找到工作流 '{name}'"
        
        workflow = self.workflows[name]
        logger.info(f"Starting workflow: {name}")
        
        # 依次执行步骤 (此处简化实现)
        results = []
        for step in workflow["steps"]:
            # 这里应通过 orchestrator 调度执行
            results.append(f"执行步骤: {step['action']}")
            
        return f"工作流 '{name}' 执行完毕：\n" + "\n".join(results)

# 全局实例
workflow_manager = WorkflowManager()
