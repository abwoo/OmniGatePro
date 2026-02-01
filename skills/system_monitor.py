from core.skill import BaseSkill, skill_tool
import psutil
import platform
import datetime

class SystemMonitorSkill(BaseSkill):
    """
    系统监控技能：提供深度的本地硬件状态分析。
    """
    name = "system_monitor"
    description = "Monitor local hardware performance and system info"

    @skill_tool(name="get_health", description="获取系统健康度综合评估")
    def get_health(self) -> str:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        
        status = "良好" if cpu < 70 and mem < 80 else "负载较高"
        return f"🖥️ 系统健康评估: {status}\n- CPU: {cpu}%\n- 内存: {mem}%\n- 启动时间: {boot_time}\n- 平台: {platform.system()} {platform.release()}"

    @skill_tool(name="list_processes", description="列出当前高负载进程")
    def list_processes(self, top_n: int = 5) -> str:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                procs.append(p.info)
            except: continue
        
        top_procs = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:top_n]
        res = "🔥 高负载进程列表:\n"
        for p in top_procs:
            res += f"- {p['name']} (PID: {p['pid']}): {p['cpu_percent']}%\n"
        return res
