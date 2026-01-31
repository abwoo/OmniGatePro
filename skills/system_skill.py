import os
import subprocess
from core.skill import BaseSkill, skill_tool

class SystemSkill(BaseSkill):
    name = "system"
    description = "Provides access to the local filesystem and shell commands."

    @skill_tool(description="Read the contents of a file.")
    def read_file(self, path: str) -> str:
        if not os.path.exists(path):
            return f"Error: File '{path}' not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @skill_tool(description="Write content to a file.")
    def write_file(self, path: str, content: str) -> str:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to '{path}'."

    @skill_tool(description="Execute a shell command.")
    def run_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error (Exit Code {result.returncode}): {result.stderr}"
        except Exception as e:
            return f"Exception: {str(e)}"

    @skill_tool(description="List files in a directory.")
    def list_dir(self, path: str = ".") -> str:
        try:
            files = os.listdir(path)
            return "\n".join(files)
        except Exception as e:
            return f"Error: {str(e)}"
