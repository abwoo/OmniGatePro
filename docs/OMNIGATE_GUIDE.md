# OmniGate Pro: 全能 AI 智能体网关学习手册

欢迎使用 **OmniGate Pro**！这是一个开源、自托管的 AI 智能体网关，以“消息优先+本地执行+自主行动”为核心逻辑。

---

## 🛠️ 快速起步

### 1. 环境初始化
```powershell
pip install -r requirements.txt
python cli.py setup-keys
python cli.py doctor
```

### 2. 核心功能演示
体验 OmniGate 如何在本地执行任务、管理文件并与 Clawdbot 协同。
```powershell
$env:PYTHONPATH = "."; python demo_omni_pro.py
```

---

## 🏗️ 核心架构

- **网关 (OmniGateway)**: 统一处理来自 Telegram, Feishu, Discord 的消息。
- **智能体 (OmniAgent)**: 负责逻辑推理，决定何时调用本地技能。
- **技能 (Skills)**: 
    - `system`: 执行 shell 命令。
    - `file`: 管理本地文件。
- **Clawdbot 插件**: OmniGate 可作为 Clawdbot 的下游插件，承担本地繁重任务并优化 Token 消耗。

---

## 📱 极简操作流程 (Smartphone UX)

OmniGate 引入了 **标准化工作流 (Workflows)**，通过简单的 YAML 配置即可实现复杂的自动化：

1.  **定义工作流**: 在 `core/workflows/` 下创建一个 `.yaml` 文件。
2.  **一键执行**: 通过消息发送 `/run 工作流名称` 即可。

---

## 🔗 Clawdbot 集成指南

要将 OmniGate 接入 Clawdbot，请在 Clawdbot 的配置中添加以下指针：
- `omni.offload_task`: 将需要本地执行的任务交给 OmniGate。
- `omni.optimize_token`: 使用 OmniGate 的本地算法压缩超长上下文。

---
**OmniGate Pro - 让大模型具备真实行动力**
