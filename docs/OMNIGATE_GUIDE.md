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

## 📱 智能手机级交互 (Low Learning Cost)

OmniGate 追求极致的低学习门槛。即使在终端操作，我们也遵循“标准化菜单”逻辑：

1.  **启动机器人后**，点击菜单或输入 `/start`。
2.  **常用动作一键触发**：
    - 直接输入需求（如“查一下当前的磁盘空间”），Agent 会自动将其转换为 `RUN: df -h` 并执行。
    - 无需记忆复杂的 API 参数，系统会自动通过“指针”进行分发。

---

## 🏗️ 核心逻辑：Clawdbot 的“手”与“加速器”

OmniGate 的底层逻辑是 **Clawdbot 的本地扩展层**：
- **云端 (Clawdbot)**: 负责复杂的策略决策与高层逻辑。
- **本地 (OmniGate)**: 负责具体的执行（Shell, File）与数据压缩（Token Saver）。

这种架构确保了即使在 **512MB 内存** 的设备上，Clawdbot 也能通过 OmniGate 实现高效的本地任务处理。

---

## 🔗 Clawdbot 集成指南

要将 OmniGate 接入 Clawdbot，请在 Clawdbot 的配置中添加以下指针：
- `omni.offload_task`: 将需要本地执行的任务交给 OmniGate。
- `omni.optimize_token`: 使用 OmniGate 的本地算法压缩超长上下文。

---
**OmniGate Pro - 让大模型具备真实行动力**
