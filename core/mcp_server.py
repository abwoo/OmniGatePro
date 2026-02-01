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

@mcp.tool()
async def search_local_files(query: str, path: str = ".") -> str:
    """
    极速文件检索工具：在指定目录下快速查找包含关键词的文件。
    """
    import os
    results = []
    for root, dirs, files in os.walk(path):
        if "node_modules" in root or ".git" in root: continue
        for file in files:
            if query.lower() in file.lower():
                results.append(os.path.join(root, file))
        if len(results) > 10: break
    return "\n".join(results) if results else "未找到相关文件。"

if __name__ == "__main__":
    # 启动 MCP 服务器 (标准 IO 模式，方便 Clawdbot 挂载)
    mcp.run()
