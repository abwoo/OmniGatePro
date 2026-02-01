# OmniGate Pro 详细指令参考与功能指南

本手册提供 OmniGate Pro 系统的全量 CLI 指令说明、核心功能配置深度解析以及高级扩展开发指南。全文严格遵循无表情符号原则。

---

## 1. CLI 指令集详解

所有指令均通过 `python cli.py [指令]` 调用，或在交互式主菜单中选择。

### 1.1 setup-keys
*   **用途**: 初始化与更新系统密钥。
*   **参数说明**:
    *   `DEEPSEEK_API_KEY`: 系统默认推理引擎。
    *   `TELEGRAM_BOT_TOKEN`: 机器人身份标识。
    *   `HTTPS_PROXY`: 可选。配置格式为 `http://IP:PORT`，用于解决国内服务器无法访问 Telegram API 的问题。
*   **注意事项**: 配置完成后，密钥将加密存储于本地 `.env` 文件。

### 1.2 onboard
*   **用途**: 全自动化环境审计与配置文件生成。
*   **审计项**:
    *   **基础设施**: 检查 `~/.openclaw` 目录及 `workspace` 读写权限。
    *   **连通性**: 依次握手 DeepSeek、OpenAI 及 Telegram，测量延迟并确认有效性。
    *   **配置同步**: 自动将 `.env` 映射至 OpenClaw 的 `openclaw.json`。

### 1.3 run
*   **用途**: 启动增强网关并开启仪表盘。
*   **工作机制**:
    *   **端口管理**: 自动检测并释放 18789 (OpenClaw) 和 18799 (OmniGate API)。
    *   **Sidecar 模式**: 启动 Python FastAPI 服务作为 OpenClaw 的本地增强侧挂。
    *   **可视化监控**: 启动全屏 TUI 界面。

### 1.4 status
*   **用途**: 实时查看系统活跃状态。
*   **输出内容**: 端口占用情况、双引擎在线状态、最近 10 条后台日志。

### 1.5 doctor
*   **用途**: 深度故障排查。
*   **包含项目**: API 响应时间测试、系统 CPU/内存负载分析、环境变量冲突检测。

### 1.6 fix
*   **用途**: 一键修复环境问题。
*   **修复逻辑**: 自动重装依赖、清理残留进程、修复配置文件语法错误。

---

## 2. 核心增强功能深度解析

### 2.1 智能 Token 压缩 (Smart Shrinking)
*   **触发阈值**: 上下文长度 > 400 字符。
*   **压缩流程**:
    1.  提取并锁定保护项: 文件路径、API 密钥、代码块标记。
    2.  语义降噪: 移除重复的系统提示词与空白符。
    3.  中间历史摘要化: 仅保留关键名词与谓词。
    4.  尾部语境保留: 确保最新的 5-6 轮对话保持完整。

### 2.2 本地长效记忆 (Persistent Memory)
*   **存储路径**: `data/memory.json`。
*   **记忆提取**: 系统会自动识别如 "我的名字是..."、"我更喜欢..." 等陈述性语句并进行持久化。
*   **上下文注入**: 在每次向 LLM 发起请求前，系统会根据当前对话主题，从记忆库中检索出最相关的历史事实并注入 System Prompt。

### 2.3 动态插件开发 (MCP)
OmniGate Pro 允许开发者使用纯 Python 扩展 AI 的能力。
*   **基类**: `core.skill.BaseSkill`。
*   **装饰器**: `@skill_tool`。
*   **开发示例**:
    ```python
    from core.skill import BaseSkill, skill_tool
    
    class MyCustomSkill(BaseSkill):
        name = "custom_tool"
        description = "我的自定义工具"
        
        @skill_tool(name="do_something", description="执行特定任务")
        def do_something(self, param: str) -> str:
            return f"任务执行结果: {param}"
    ```
*   **加载方式**: 将脚本保存至 `skills/` 目录，系统启动时将自动识别并热加载。

---

## 3. 离线状态处理与系统自愈指南

当仪表盘或状态检查显示 OmniGate Pro 或 OpenClaw 处于“离线”状态时，请按照以下步骤进行处理。

### 3.1 识别离线组件
*   OmniGate Pro 离线: 通常意味着 Python FastAPI 后端服务未启动或被异常终止。
*   OpenClaw Gateway 离线: 意味着 Node.js 核心引擎未运行，此时 Telegram 等通讯渠道将失效。

### 3.2 自动自愈步骤
这是处理离线问题的首选方案：
1.  运行 `python cli.py fix`：系统会自动检测并清理导致服务无法启动的残留进程，并重新安装缺失的依赖。
2.  运行 `python cli.py run`：重新尝试联合启动双引擎。

### 3.3 手动排查步骤
如果自动自愈无效，请执行以下操作：
1.  检查端口占用: 运行 `openclaw gateway --port 18789 --verbose` (针对 OpenClaw) 或 `netstat -ano | findstr :18799` (针对 OmniGate)。
2.  查阅日志: 
    *   主引擎日志: `logs/openclaw.log`。
    *   API 日志: 观察控制台输出或 `logs/` 目录下的相关记录。
3.  环境变量校验: 运行 `python cli.py doctor`，确认 API Key 是否过期或代理是否失效。

### 3.4 彻底重置 (慎用)
如果系统由于配置冲突无法启动且无法通过 fix 修复，请运行 `python cli.py onboard` 强制重新生成所有配置文件。

---

## 4. 常见问题排查 (Troubleshooting)

### 3.1 端口占用错误
*   **现象**: 启动时提示端口被占用。
*   **解决**: 运行 `python cli.py fix`。系统将尝试定位并杀死占用 18789 或 18799 端口的进程。

### 3.2 Telegram 连接超时
*   **现象**: onboard 阶段 Telegram 校验失败。
*   **解决**: 
    1. 检查 `setup-keys` 中的代理配置是否正确。
    2. 尝试在终端运行 `ping api.telegram.org` 确认网络基础连通性。

### 3.3 插件未在仪表盘显示
*   **现象**: 新写的 Python 脚本没有出现在技能列表中。
*   **解决**: 
    1. 检查类是否继承自 `BaseSkill`。
    2. 检查文件名是否以 `.py` 结尾且不在 `__init__.py` 中。
    3. 查看 `logs/openclaw.log` 确认是否有 Python 语法错误导致加载失败。

---

## 5. 维护与更新
建议每周运行一次 `python cli.py fix` 以确保环境依赖保持最新，并定期备份 `data/memory.json` 以保护您的长效记忆数据。
