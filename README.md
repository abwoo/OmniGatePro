# 🦞 OmniGate Pro: Clawdbot 核心增强插件与极简网关

[![Smoke Test](https://github.com/abwoo/OmniGatePro/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/abwoo/OmniGatePro/actions/workflows/smoke-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

OmniGate Pro 是一款专为 **Clawdbot** (OpenClaw) 打造的“全屋智能”补丁。它不仅让您的 AI 助手更聪明，更让它变得前所未有的**轻量**与**省钱**。

---

## 🚀 一键安装 (One-line Install)

适用于 **Linux / macOS / Windows (WSL)**。请在终端执行：

```bash
curl -sSL https://raw.githubusercontent.com/abwoo/OmniGatePro/main/install.sh | bash
```

> **注意**: 该脚本会自动完成依赖检测、虚拟环境创建、PATH 配置及 OpenClaw 构建。

---

## 🗺️ 快速导航 (Documentation Portal)

为了让您快速掌握系统，我们将所有操作分门别类，您可以点击下方链接跳转至详细文档：

### 🏗️ [OpenClaw 底层配置与集成逻辑](docs/OPENCLAW_SETUP.md)
- **必读**: 详细说明如何从源码构建 OpenClaw 引擎，以及它与 OmniGate Pro 的共生关系。

### 🚀 [快速开始 (1-2-3 流程)](docs/FEATURES_GUIDE.md#🚀-智能手机级-setup-1-2-3-流程)
- 密钥配置、一键入驻、启动运行。

### 🧩 [技能与操作指南 (Skills Guide)](docs/FEATURES_GUIDE.md)
- 如何让 AI 使用备忘录、画图、搜索本地文件。
- **必读**: 自然语言触发技能的技巧。

### 🤖 [智能体与多端管理 (Agents & Channels)](docs/FEATURES_GUIDE.md#🤖-智能体管理：多重身份切换)
- 如何管理多个 AI 身份。
- 配置 Telegram, Discord, 飞书等多端同步。

### 🖥️ [终端面板操作 (TUI Manual)](docs/FEATURES_GUIDE.md#💻-tui-终端仪表盘：实时监控)
- 如何读取系统负载、监控渠道状态。

### ⚙️ [全量配置与指令集 (Command Reference)](docs/COMMANDS.md)
- 环境变量 `.env` 详细示例。
- `omni` 指令全集。

---

## 💎 核心优势

| 功能特性 | 原生 OpenClaw | **OmniGate Pro (增强版)** |
| :--- | :--- | :--- |
| **Token 消耗** | 基础上下文截断 | **语义级智能压缩 (节省 60%-90% 费用)** |
| **本地能力** | 基础 Shell 执行 | **深度系统分析、极速文件检索 (Python 增强)** |
| **安装部署** | 易报错 | **`omni` 一键自动化环境自愈与入驻** |
| **操作门槛** | 纯命令行 | **TUI 终端仪表盘 + 1-2-3 标准化流程** |

---

## 🔗 逻辑链条 (Tutorial Chain)

```text
[ 用户 ] ↔ [ Telegram/Discord ] 
               ↕ (协议对接)
         [ OpenClaw Engine ]
               ↕ (MCP 协议嵌入)
         [ OmniGate Pro ] ↔ [ DeepSeek / OpenAI ]
               ↕ (本地执行)
         [ 🧩 本地技能插件 ]
```

1.  **🧠 大脑 (DeepSeek)**: 推理大脑。
2.  **📱 界面 (Telegram/Discord)**: 交互入口。
3.  **🦞 中枢 (OmniGate Pro)**: 负责 **Token 压缩** 与 **本地技能分发**。

---
**OmniGate Pro - 让您的 AI 助手更轻、更快、更省。**
