# 🏗️ OpenClaw 底层配置与集成指南

OmniGate Pro 是建立在 **OpenClaw** (Clawdbot) 核心之上的增强中间件。在配置 OmniGate 之前，您需要先确保底层引擎 OpenClaw 已正确安装并构建。

---

## 1. OpenClaw 底层引擎安装

请按照以下步骤在本地手动构建 OpenClaw 核心：

### A. 源码获取
```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

### B. 依赖安装与 UI 构建
OpenClaw 采用前后端分离架构，需要先构建其管理界面：
```bash
pnpm install
pnpm ui:build # 首次运行会自动安装 UI 依赖并构建
```

### C. 核心编译
```bash
pnpm build
```

### D. 守护进程安装 (可选)
如果您希望 OpenClaw 网关在后台持续运行：
```bash
pnpm openclaw onboard --install-daemon
```

---

## 2. OmniGate Pro 的角色与作用

**OmniGate Pro** 并不是 OpenClaw 的替代品，而是它的“智能插件层”：

| 维度 | OpenClaw (底层) | OmniGate Pro (增强层) |
| :--- | :--- | :--- |
| **主要职责** | 协议对接 (Telegram/Discord/Slack) | 数据优化、本地技能分发 |
| **Token 处理** | 原始发送，容易超出限额 | **智能压缩 (节省 80% 费用)** |
| **插件系统** | 基于 Node.js 的基础工具 | **基于 Python 的全能 MCP 插件** |
| **用户界面** | 命令行或 Web | **精美 TUI 终端实时仪表盘** |

---

## 3. 开发者调试细则

如果您是开发者，想要对 OpenClaw 和 OmniGate 进行联调，请参考以下配置：

### 开启开发模式 (Dev Loop)
在 `openclaw` 目录下运行，以支持热重载：
```bash
pnpm gateway:watch
```

### 联调链路证明
1. **输入阶段**: 用户发送消息 -> **OpenClaw** 接收 -> 转发给 **OmniGate** 拦截器。
2. **处理阶段**: **OmniGate** 执行 Token 压缩 -> 调用 DeepSeek。
3. **执行阶段**: AI 需要操作本地硬件 -> 调用 **OmniGate Python MCP** -> 返回结果。

### 与 OpenClaw 开发的关系
OmniGate Pro 通过 OpenClaw 预留的 **MCP (Model Context Protocol)** 接口深度嵌入。这意味着您在 OmniGate 中编写的 Python 技能，可以无缝被 OpenClaw 的所有 Agent 实例调用。

---
**配置完成后，请返回主目录运行 `omni onboard` 完成最终的一键入驻。**
