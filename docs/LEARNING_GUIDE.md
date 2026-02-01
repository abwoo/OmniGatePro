# OmniGate Pro 学习与操作手册

欢迎来到 **OmniGate Pro**！这是一个开源、自托管的 AI 智能体网关，以“消息优先+本地执行+自主行动”为核心逻辑，旨在作为 Clawdbot (OpenClaw) 的核心增强插件。

为了让你能够顺利掌握系统，我们建议按照以下顺序逐步操作。

---

## 🏗️ 第一阶段：环境初始化 (Basics)

在这一阶段，我们确保本地运行环境就绪。

### 1. 安装依赖
```powershell
# 安装核心依赖
pip install -r requirements.txt
# 以开发模式安装项目
pip install -e .
```

### 2. 系统自检
```powershell
# 运行环境诊断
omni doctor
```
*如果你看到 `Redis | OFFLINE`，请不要担心，系统会自动切换到本地模拟模式。*

---

## 🔌 第二阶段：Clawdbot 集成 (Clawdbot Integration)

OmniGate Pro 的核心价值在于为 Clawdbot 提供本地执行力。

### 1. 全自动入驻
运行此命令，系统会自动配置 OpenClaw 及其插件，绕过繁琐的 TUI 向导。
```powershell
omni onboard
```

### 2. 启动网关
启动 OmniGate 网关（包含 MCP 服务器和 REST API），让 Clawdbot 可以调用本地技能。
```powershell
omni gateway --verbose
```

---

## 🤖 第三阶段：智能体交互 (Agent Action)

你可以直接在终端下达指令，验证 Agent 的本地执行能力。

### 1. 执行本地任务
```powershell
omni agent --message "帮我检查当前系统的健康状况，并列出目录下的重要文件" --thinking high
```

### 2. 跨平台消息
```powershell
omni message send --to "+1234567890" --message "OmniGate Pro 已就绪"
```

---

## 🛠️ 进阶：自定义技能 (Custom Skills)

你可以通过在 `core/skills/` 目录下添加新的 Python 类来扩展系统的能力。每个技能都可以通过“指针”在 Clawdbot 中被动态调用。

---

## ❓ 常见问题排查 (Troubleshooting)

- **指令未找到**：如果 `omni` 指令无法运行，请确保已执行 `pip install -e .`。
- **端口占用**：如果网关启动失败，请检查 18789 端口是否被占用。
- **Token 压缩失效**：请确保在 OpenClaw 配置中正确挂载了 `omni.shrink` 指针。

---
**OmniGate Pro - 让 AI 助手更轻、更快、更智能**
