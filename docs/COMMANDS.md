# 📖 OmniGate Pro: Clawdbot 极简增强插件手册

OmniGate Pro 定位为 **Clawdbot (OpenClaw) 的核心插件**。它的主要目标是：**更轻量、更省钱、更易用**。

---

## 🔗 核心逻辑链条 (Tutorial Chain)

为了让你理解系统是如何工作的，请看下面的逻辑链条：

1.  **🧠 大脑 (DeepSeek)**: 
    - 你在 DeepSeek 官网获取 API Key。它负责所有的思考和文字生成。
2.  **📱 界面 (Telegram)**: 
    - 你在 @BotFather 申请 Token。它是你在手机上和 AI 说话的窗口。
3.  **🦞 中枢 (OmniGate Pro)**: 
    - 它是连接大脑和界面的“智能插件”。
    - **Token 压缩**: 当你和 AI 聊得很久时，上下文会变长。OmniGate 会在后台自动压缩这些文字，只把精华发给 DeepSeek，从而帮你节省 60%-90% 的费用。
    - **本地执行**: 它让云端的 DeepSeek 能够通过“插件口”操作你这台电脑上的文件和命令。

---

## �️ 详细功能指南

如果您想了解技能如何触发、智能体如何管理，请跳转至：
👉 **[OmniGate Pro 功能操作详解](FEATURES_GUIDE.md)**

---

## �🚀 标准化操作流程 (TUI Style)

我们设计了像智能手机一样简单的 **1-2-3 流程**。你只需要运行 `omni` 指令，并按照顺序点击：

### 1️⃣ 第一步：配置密钥 (`omni setup-keys`)
输入你的 DeepSeek Key 和 Telegram Token。这些信息会加密保存在本地 `.env` 文件中。

### 2️⃣ 第二步：一键入驻 (`omni onboard`)
这是最关键的一步。它会自动：
- 关联 DeepSeek 和 Telegram。
- 将 OmniGate 作为一个“技能包”挂载到 Clawdbot。
- 锁定你的 Telegram ID，防止别人恶意调用你的机器人。

### 3️⃣ 第三步：启动运行 (`omni run`)
点击后，系统会：
- 开启后台网关服务。
- **自动打开浏览器**，展示可视化控制面板。
- 你可以在面板上看到 CPU 占用和 API 状态。

### ⚙️ 进阶功能配置 (`omni setup-advanced`)
针对高级用户，支持配置以下 OpenClaw 核心特性：
- **🎙️ 语音交互**: 集成 ElevenLabs API，开启 Talk Mode 实时对话。
- **🎨 智能画布**: 启用 A2UI 可视化工作区，让 AI 渲染 HTML/图表。
- **🤖 多智能体**: 快速增加隔离的 Agent 实例，实现不同场景的专业路由。

---

## � 终端控制面板 (TUI Dashboard)

启动后，您可以进入全新的 **TUI 智能控制中心**：
- **🚀 系统状态**: 实时刷新 CPU、内存占用。
- **🤖 智能体管理**: 查看所有活跃 Agent 列表。
- **💬 通讯渠道**: 监控 Telegram/Discord 等通道连接状态。
- **🧩 技能商店**: 预览当前已挂载的所有本地技能插件。

---

## 🏥 维护与修复

如果遇到 Windows 兼容性报错或配置损坏，请在主菜单选择：
- **🔧 系统自愈**: 自动运行 `openclaw doctor --fix` 并修复环境变量问题。

---

## 💎 OmniGate Pro vs 原生 OpenClaw

| 功能特性 | 原生 OpenClaw | **OmniGate Pro (增强版)** |
| :--- | :--- | :--- |
| **安装部署** | 手动执行多条 pnpm 指令，易报错 | **`omni` 一键自动化部署，环境自愈** |
| **Token 消耗** | 基础上下文截断 | **语义级 Token 压缩 (节省 60%-90% 费用)** |
| **本地能力** | 基础 Shell 执行 | **深度系统性能分析、极速文件检索 (Python 增强)** |
| **多平台配置** | 需手动修改复杂的 JSON 文件 | **交互式 `config-center` 一键同步多端** |
| **监控界面** | 纯命令行 (CLI) | **可视化 Web Dashboard (图形化监控)** |

---
