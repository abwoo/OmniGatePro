import asyncio
import sys
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import MCP SDK
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: 'mcp' library not found. Please run: pip install mcp")
    sys.exit(1)

# Import Artfish Core
from core.config import settings
from core.gateway import Gateway
from core.intent import ArtIntent

# Initialize FastMCP - Optimized for stdio (Claude Desktop default)
# 对齐 Clawdbot: Artfish Gateway as an MCP Server
mcp = FastMCP("Artfish")
gateway = Gateway()

# --- 动态注册 Skills 为 MCP Tools ---

def register_skills():
    """
    将 Gateway 中加载的所有技能动态注册为 MCP 工具。
    """
    for skill in gateway.skill_manager.list_skills():
        for tool_meta in skill.get_tools_metadata():
            tool_name = tool_meta["name"]
            
            # 创建一个闭包来处理工具调用
            def create_tool_func(s_name, t_name):
                async def tool_func(**kwargs):
                    return gateway.skill_manager.execute(s_name, t_name, **kwargs)
                return tool_func

            # 注册到 FastMCP
            mcp.add_tool(
                create_tool_func(tool_meta["skill"], tool_meta["raw_name"]),
                name=tool_name,
                description=tool_meta["description"]
            )

register_skills()

# --- 核心任务执行工具 ---

@mcp.tool()
async def execute_task(goals: List[str], style: str = "default") -> str:
    """
    Execute a complex generative task or workflow based on a list of goals.
    Artfish will plan and orchestrate multiple skills to achieve the goals.
    """
    try:
        # 1. Setup Intent
        intent = ArtIntent(
            goals=goals,
            constraints={"style": style},
            priority=10
        )
        
        # 2. Run via Gateway
        trace = gateway.execute_intent(intent)
        
        # 3. Format Result
        results = trace.get_all_results()
        summary = {
            "status": "SUCCESS",
            "task_count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(summary, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error executing task: {str(e)}"

@mcp.resource("artfish://status")
def get_system_status() -> str:
    """Get the current health and configuration of the Artfish Gateway."""
    return json.dumps({
        "engine": "Artfish Gateway",
        "version": settings.VERSION,
        "mode": "MCP Plugin",
        "skills": [s.name for s in gateway.skill_manager.list_skills()],
        "status": "healthy"
    }, indent=2)

if __name__ == "__main__":
    # Ensure stdio transport for Claude Desktop
    mcp.run(transport="stdio")
