from mcp.server.fastmcp import FastMCP
from core.omni_engine import omni_engine
import logging

# 初始化 MCP 服务器 - 命名为 omni-plugin
mcp = FastMCP("OmniGate-Plugin")

logger = logging.getLogger("omni.mcp")

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
    Token 优化器：压缩超长对话上下文，节省云端 Token 消耗。
    """
    logger.info("MCP Shrinking context")
    return omni_engine.compress_context(context)

@mcp.resource("omni://system-info")
async def get_system_status() -> str:
    """获取本地系统运行状态资源"""
    res = await omni_engine.skills["system"].execute("get_info")
    return str(res.get("data", "Unknown"))

if __name__ == "__main__":
    # 启动 MCP 服务器 (标准 IO 模式，方便 Clawdbot 挂载)
    mcp.run()
