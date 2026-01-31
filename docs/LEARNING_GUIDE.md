# Artfish Studio Pro 学习与操作手册

欢迎来到 **Artfish Studio Pro**！这是一个基于高度可扩展多智能体 (Multi-Agent) 架构的艺术教育与协作平台。本手册将带你从零开始，一步步掌握系统的核心功能。

---

## 🛠️ 第一步：环境初始化

在开始任何操作前，我们需要确保系统环境已正确配置。

1.  **安装依赖**：
    ```powershell
    pip install -r requirements.txt
    ```
2.  **配置 API 密钥**：
    运行交互式向导，配置你的 AI 模型（推荐优先配置 OpenAI 或 DeepSeek）及其他平台密钥。
    ```powershell
    python cli.py setup-keys
    ```
3.  **系统自检**：
    使用 `doctor` 命令检查核心库、Redis 队列及配置文件的状态。
    ```powershell
    python cli.py doctor
    ```

---

## 🏗️ 第二步：核心引擎验证 (Pointer Engine)

Artfish Pro 采用了类似于 **Clawdbot** 的指针式调用机制。你可以通过统一的字符串标识符调用不同的 API 适配器。

- **运行演示**：
    ```powershell
    python demo_api_engine.py
    ```
- **核心逻辑**：
    - 指针格式：`adapter_name.method_name` (如 `telegram.sendMessage`)。
    - 优点：解耦业务逻辑与具体平台实现，方便未来接入微信、钉钉等。

---

## 🎨 第三步：多 Agent 艺术协作 (Local Collab)

这是系统的灵魂所在。你可以在不启动任何第三方接口的情况下，直接在本地体验专家 Agent 之间的互动。

- **启动本地演示**：
    ```powershell
    python demo_art_pro.py
    ```

### 体验四种协作场景：
1.  **场景 1：艺术讨论室** - 多个 Agent 围绕你的灵感进行初步交流。
2.  **场景 2：专家辩论** - 针对具有争议性的艺术话题（如“AI 艺术的原创性”），启动正反方辩论。
3.  **场景 3：协同创作工作流** - 从理论定调到视觉构思，再到审美优化，Agent 们分工明确。
4.  **场景 4：艺术互动工坊** - **(新功能)** Agent 之间进行多轮相互启发式对话，产生更深层的艺术见解。

---

## 🤖 第四步：接入 Telegram 协作机器人

当你对本地引擎感到满意后，可以开启 Telegram 入口。

1.  **启动机器人**：
    ```powershell
    python interfaces/telegram_bot.py
    ```
2.  **核心指令**：
    - `/start`: 欢迎信息与功能概览。
    - `/debate <主题>`: 启动 Agent 间的学术辩论。
    - `/collab <灵感>`: 进入多 Agent 协作讨论。
    - `/monitor`: 实时监控系统延迟与熔断器状态。

---

## 🧩 开发者指南：如何添加新的 Agent？

1.  在 `core/agents/art_agents.py` 中继承 `ArtAgent` 类。
2.  实现 `process_task` 方法，定义 Agent 的专业逻辑。
3.  在 `orchestrator` 中注册你的新 Agent。

---

## 📅 更新日志与修复记录

- **Bug 修复**:
    - 解决了 LLM 不可用时直接打印 Python 字典的问题，新增了 `_fallback_format` 逻辑。
    - 修复了 `rich` 库在某些终端下颜色解析失败的错误。
    - 增强了测试用例的鲁棒性，确保 CI/CD 流程绿色通过。
- **新增功能**:
    - **艺术互动工坊**: 支持 Agent 间多轮循环互动。
    - **个性化增强**: 改进了 `PersonaEngine`，使回复内容更具情感色彩。

---
**Artfish Studio Pro - 释放 AI 的创意潜能**
