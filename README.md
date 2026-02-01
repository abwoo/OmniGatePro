# OmniGate Pro: Clawdbot 核心增强插件与网关系统

OmniGate Pro 是一款专为 OpenClaw (原 Clawdbot) 开发的高级增强补丁与网关中枢。本项目通过 Python 生态系统的深度集成，解决了原生 OpenClaw 在 Token 消耗过高、插件扩展复杂以及本地执行效率受限等方面的核心痛点。

---

## 1. 系统架构与原理

OmniGate Pro 并非 OpenClaw 的替代品，而是作为其“智能大脑”与“本地外挂”存在。

*   **中枢层 (OmniEngine)**: 负责语义分析、长效记忆检索及上下文智能压缩。
*   **网关层 (FastAPI Sidecar)**: 提供 RESTful 接口，支持异步任务卸载。
*   **通讯层 (MCP Server)**: 通过 Model Context Protocol 与 OpenClaw 实时桥接，动态注入 Python 技能。

---

## 2. OpenClaw 底层引擎详尽安装指南

在配置 OmniGate Pro 之前，必须确保 OpenClaw 核心引擎已在本地正确构建并能独立运行。

### 2.1 环境预检查
请依次在终端运行以下命令，确认环境满足要求：
*   **Node.js**: `node -v` (要求 v22.12.0 或更高)
*   **pnpm**: `pnpm -v` (要求 v10.x 或更高)
*   **Git**: `git --version`

### 2.2 安装与构建步骤
1.  **克隆源码**:
    ```bash
    git clone https://github.com/steipete/openclaw.git
    cd openclaw
    ```
2.  **安装依赖**:
    ```bash
    pnpm install
    ```
3.  **初次构建**:
    ```bash
    pnpm build
    ```
4.  **环境校验**:
    运行 `pnpm openclaw doctor` 检查是否有环境报错。

---

## 3. OmniGate Pro 安装与配置指南

### 3.1 环境准备
*   **Python**: 版本 >= 3.10
*   **虚拟环境 (推荐)**: 
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows
    ```

### 3.2 依赖安装
在项目根目录下运行：
```bash
pip install -r requirements.txt
```

### 3.3 密钥配置 (Step 1)
运行交互式配置工具：
```bash
python cli.py setup-keys
```
按照屏幕提示输入以下必要信息：
*   DeepSeek API Key (作为主要推理大脑)
*   Telegram Bot Token (作为交互入口)
*   HTTPS_PROXY (如果您的网络环境需要代理访问 Telegram)

### 3.4 环境入驻与同步 (Step 2)
运行自动化同步工具：
```bash
python cli.py onboard
```
此步骤将执行：
*   生成标准 `~/.openclaw/openclaw.json`。
*   校验各 API 服务商的连通性。
*   自动创建必要的本地工作目录。

---

## 4. 启动与运行 (Step 3)

### 4.1 联合启动模式
推荐使用以下指令一键拉起所有服务：
```bash
python cli.py run
```
该指令将自动执行以下操作：
1.  清理并释放 18789 (OpenClaw) 和 18799 (OmniGate) 端口。
2.  启动 OmniGate Pro 增强 API 服务。
3.  在后台拉起 OpenClaw Gateway 核心引擎。
4.  进入 TUI 可视化仪表盘，实时监控 Token 节省率与系统负载。

---

## 5. 核心增强特性

### 5.1 智能 Token 压缩 (Smart Shrinking)
针对 DeepSeek 模型深度优化。当上下文超过 400 字符时，系统将通过语义提取技术移除冗余对话，仅保留核心实体、文件路径及最新语境，大幅降低 API 账单成本。

### 5.2 本地长效记忆 (Persistent Memory)
利用 `data/memory.json` 实现跨会话记忆。Bot 会自动识别并存储用户的个人信息与偏好，在后续对话中自动唤醒相关记忆。

### 5.3 Python 动态插件 (Dynamic Skills)
无需重启 OpenClaw，只需将继承自 `BaseSkill` 的 Python 脚本存入 `skills/` 目录，Bot 即可通过 MCP 协议即时获得新技能。

---

## 6. 文档与支持
*   详细指令说明: [USAGE.md](USAGE.md)
*   常见问题排查: 参见 USAGE.md 中的故障排除章节。

---
OmniGate Pro - 为您的 AI 助手注入 Python 的无限可能。
