import subprocess
import os
import platform
import asyncio
from typing import Any, Dict
from core.skills.base import BaseSkill

class SystemSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "system"

    @property
    def description(self) -> str:
        return "执行系统命令、查询环境信息、控制本地进程"

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        if action == "run_command":
            cmd = kwargs.get("command")
            if not cmd:
                return self.format_result("error", error="Missing 'command' parameter")
            
            try:
                # 异步执行系统命令
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                return self.format_result("success", data={
                    "stdout": stdout.decode().strip(),
                    "stderr": stderr.decode().strip(),
                    "exit_code": process.returncode
                })
            except Exception as e:
                return self.format_result("error", error=str(e))
        
        elif action == "get_info":
            return self.format_result("success", data={
                "os": platform.system(),
                "release": platform.release(),
                "cwd": os.getcwd(),
                "user": os.getlogin() if platform.system() != "Windows" else os.environ.get("USERNAME")
            })

        return self.format_result("error", error=f"Unknown action: {action}")

class FileSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "file"

    @property
    def description(self) -> str:
        return "本地文件读写、目录管理、搜索"

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path")
        if not path:
            return self.format_result("error", error="Missing 'path' parameter")
        
        # 转换为绝对路径并进行基础安全检查（防止跳出工作目录，虽然是自托管但也要有基础防护）
        # abs_path = os.path.abspath(path)
        
        try:
            if action == "read":
                if not os.path.exists(path):
                    return self.format_result("error", error="File not found")
                with open(path, 'r', encoding='utf-8') as f:
                    return self.format_result("success", data=f.read())
            
            elif action == "write":
                content = kwargs.get("content", "")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return self.format_result("success", data=f"File written to {path}")
            
            elif action == "list":
                if not os.path.isdir(path):
                    return self.format_result("error", error="Not a directory")
                return self.format_result("success", data=os.listdir(path))
                
        except Exception as e:
            return self.format_result("error", error=str(e))

        return self.format_result("error", error=f"Unknown action: {action}")
