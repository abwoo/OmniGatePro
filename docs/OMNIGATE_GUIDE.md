# OmniGate Pro: Clawdbot (OpenClaw) 插件集成与学习手册

本手册将引导你如何基于 **OpenClaw** (Clawdbot) 运行环境，挂载 OmniGate Pro 插件，实现极致轻量化、Token 节省与低学习成本的目标。

---

## 🛠️ 第一步：运行基础环境 (The Foundation)

OmniGate Pro 是 **OpenClaw** 的增强插件。因此，你首先需要运行 OpenClaw。

1.  **克隆并启动 OpenClaw**:
    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    # 启动 OpenClaw 网关
    openclaw gateway --port 18789
    ```

---

## 🔌 第二步：挂载 OmniGate 插件 (Plugin Integration)

OmniGate 提供了两种接入方式：**MCP (推荐)** 和 **REST API**。

### 方式 A: 通过 MCP 接入 (最快、最省 Token)
OpenClaw 原生支持 MCP (Model Context Protocol)。你可以将 OmniGate 作为一个本地 Tool 挂载。

1.  **启动 OmniGate MCP 服务器**:
    ```powershell
    python core/mcp_server.py
    ```
2.  **在 OpenClaw 中配置**:
    在 OpenClaw 的 `workspace` 配置中，添加一个新的 MCP 源，指向上述脚本。Clawdbot 即可获得 `offload_task` 和 `shrink_context` 两个超级技能。

### 方式 B: 通过 REST API 接入 (轻量级网关模式)
如果你希望 OmniGate 作为一个独立的 Sidecar 运行：

1.  **启动 REST 网关**:
    ```powershell
    python core/fastapi_gateway.py
    ```
2.  **调用接口**: Clawdbot 可以通过 HTTP POST `http://127.0.0.1:18789/shrink` 来压缩长上下文。

---

## � 三大核心功能详解

### 1. 极致轻量化 (Lightweight)
- **运行要求**: 核心引擎仅需 **~50MB RAM**。
- **优化点**: 移除了所有重型库和冗余逻辑，仅保留 `OmniEngine` 进行本地任务调度。这使得主控端 (OpenClaw) 和插件端都能在极低配置的设备上流畅运行。

### 2. Token 节省器 (Token Optimizer)
- **原理**: 当检测到历史记录过长时，主控端会通过 `omni.shrink` 指针调用插件。
- **效果**: 通过本地摘要算法，将长对话背景压缩至精炼摘要，从而节省 **50% - 80%** 的云端 Token 费用。

### 3. 智能手机级 UX (Low Learning Cost)
- **标准化流程**: 采用“意图直达”逻辑。你无需记忆复杂的终端命令，直接在聊天软件中描述任务，系统会自动识别并执行。
- **低门槛操作**: 通过统一的 `/menu` 快捷指令管理所有本地任务，让学习成本降至最低。

---

## � 联调测试流程

1.  启动 **OpenClaw**。
2.  启动 **OmniGate MCP Server** 或 **FastAPI Gateway**。
3.  在聊天框发送：`帮我查看当前系统的负载，并压缩一下之前的对话。`
4.  观察控制台输出，确认任务已成功卸载执行并节省了 Token。

---
**OmniGate Pro - 让 Clawdbot 拥有本地执行的“手”与节省开支的“脑”。**
