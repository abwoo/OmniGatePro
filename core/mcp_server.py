from mcp.server.fastmcp import FastMCP
from core.omni_engine import omni_engine
from core.skill_manager import SkillManager
import logging
import os
import sys

# 初始化 MCP 服务器 - 命名为 omni-plugin
mcp = FastMCP("OmniGate-Plugin")

logger = logging.getLogger("omni.mcp")

# 初始化技能管理器
skill_manager = SkillManager(skills_dir="skills")
skill_manager.load_skills()

# --- 核心工具 (始终保留) ---

@mcp.tool()
async def offload_task(task: str) -> str:
    """
    将复杂的本地任务卸载给 OmniGate 执行。
    支持: 运行 shell 命令 (RUN: xxx), 读取/写入文件。
    """
    logger.info(f"MCP Offloading task: {task}")
    return await omni_engine.execute_task(task)

@mcp.tool()
async def shrink_context(context: str) -> str:
    """
    Token 优化器：使用 Omni 语义压缩算法优化超长对话上下文，节省 40-70% Token。
    """
    logger.info("MCP Shrinking context")
    return omni_engine.compress_context(context)

# --- 动态工具发现与注册 ---

def register_dynamic_tools():
    """将 SkillManager 加载的技能动态注册到 MCP"""
    tools_metadata = skill_manager.get_all_tools_metadata()
    for meta in tools_metadata:
        skill_name = meta["skill"]
        tool_name = meta["raw_name"]
        full_name = meta["name"]
        description = meta["description"]
        
        # 定义一个闭包来处理调用
        def create_tool_func(s_name, t_name):
            async def dynamic_tool_func(**kwargs):
                logger.info(f"Dynamic Tool Call: {s_name}.{t_name}")
                return skill_manager.execute(s_name, t_name, **kwargs)
            return dynamic_tool_func

        # 使用 FastMCP 的内部机制注册 (如果是动态的)
        # 注意：FastMCP 通常使用装饰器，这里我们手动模拟
        mcp.tool(name=full_name, description=description)(create_tool_func(skill_name, tool_name))
        logger.info(f"Successfully registered dynamic tool: {full_name}")

# 执行动态注册
register_dynamic_tools()

@mcp.resource("omni://system-info")
async def get_system_status() -> str:
    """获取本地系统运行状态资源"""
    res = await omni_engine.skills["system"].execute("get_info")
    return str(res.get("data", "Unknown"))

@mcp.tool()
async def analyze_system_performance() -> str:
    """
    深度性能分析工具：利用 Python psutil 库提供比 Node.js 更精准的硬件负载分析。
    """
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return (
        f"📊 系统深度负载报告:\n"
        f"- CPU 占用: {cpu}%\n"
        f"- 内存: 已用 {mem.percent}% (剩余 {mem.available // 1024**2}MB)\n"
        f"- 磁盘: 已用 {disk.percent}%"
    )

if __name__ == "__main__":
    # 启动 MCP 服务器 (标准 IO 模式，方便 Clawdbot 挂载)
    mcp.run()
