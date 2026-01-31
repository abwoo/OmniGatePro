# Artfish Studio Pro 学习与操作手册

欢迎来到 **Artfish Studio Pro**！这是一个基于高度可扩展多智能体 (Multi-Agent) 架构的艺术教育与协作平台。

为了让你能够顺利掌握系统，我们建议按照以下 **“从本地到云端”** 的顺序逐步操作。

---

## 🏗️ 第一阶段：本地环境与核心引擎 (Basics)

在这一阶段，我们不需要任何复杂的外部配置，重点是验证系统的“大脑”是否正常工作。

### 1. 环境初始化
```powershell
# 安装核心依赖 (已优化，无需 C++ 编译环境)
pip install -r requirements.txt

# 运行系统自检
python cli.py doctor
```
*如果你看到 `Redis | OFFLINE`，请不要担心，系统会自动切换到本地模拟模式。*

### 2. 验证 API 指针引擎
Artfish 使用“指针”来调用 API。即使你没有配置真实的 Key，你也可以观察到系统是如何调度这些请求的。
```powershell
$env:PYTHONPATH = "."; python demo_api_engine.py
```

### 3. 体验多 Agent 艺术协作 (核心功能)
直接在控制台观看专家 Agent 们的灵感碰撞。
```powershell
$env:PYTHONPATH = "."; python demo_art_pro.py
```
**在这个演示中，你会看到：**
- **学术辩论**：针对“AI 艺术原创性”的正反方交锋。
- **互动工坊**：导师与艺术家之间的多轮启发式对话。
- **协同创作**：从理论到构想的完整工作流。

---

## 🔑 第二阶段：配置与 AI 模型接入 (AI Integration)

当你熟悉了本地流程后，可以开始接入真实的 AI 模型，让 Agent 的回复更加智能。

1.  **获取密钥**：准备好 OpenAI, DeepSeek 或其他厂商的 API Key。
2.  **配置向导**：
    ```powershell
    python cli.py setup-keys
    ```
    *按照提示输入密钥，系统会自动生成 `.env` 配置文件。*

---

## 🤖 第三阶段：多平台接口接入 (Interface)

最后，你可以将这一套强大的 Agent 系统对接到社交平台。

1.  **Telegram 机器人**：
    ```powershell
    python interfaces/telegram_bot.py
    ```
    - 使用 `/debate` 发起辩论。
    - 使用 `/collab` 发起协作。
2.  **飞书推送验证**：
    ```powershell
    python demo_feishu.py
    ```

---

## 🧩 进阶：自定义你的 Agent

你可以通过修改 `core/agents/art_agents.py` 来定义自己的 Agent 角色和性格。系统会自动为你的 Agent 匹配合适的语调和评价维度。

---

## �️ 常见问题排查 (Troubleshooting)

- **Conflict 错误**：如果你在启动 Telegram 时看到 Conflict，说明后台有残留进程。请运行 `Stop-Process -Name "python" -Force`。
- **缺失 C++ 编译环境**：我们已经将 gRPC 设为可选，如果安装报错，请检查 `requirements.txt` 中相关行是否已注释。

---
**Artfish Studio Pro - 释放 AI 的创意潜能**
