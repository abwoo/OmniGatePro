# Artfish Studio Pro: 从零开始的本地化操作指南 (非 Telegram 优先)

为了确保系统稳健且不依赖单一接口，我们将按照以下“由内而外”的顺序重新开始操作：

## 第一阶段：环境与密钥初始化 (CLI First)
我们将不再手动修改 `.env`，而是通过增强的命令行工具进行配置。
- **任务 1**: 运行密钥设置向导。
    - `python cli.py setup-keys`
    - 依次配置 OpenAI, DeepSeek, Discord, Slack 等密钥。
- **任务 2**: 系统环境自检。
    - `python cli.py doctor` (检查依赖、Redis 状态及 API 连通性)

## 第二阶段：通用 API 引擎测试 (Engine First)
验证 Clawdbot 式的指针调用机制是否在本地完美运行。
- **任务 1**: 运行 API 引擎演示。
    - `python demo_api_engine.py`
    - 验证 `telegram`, `discord`, `slack` 适配器的调度逻辑。
- **任务 2**: 动态适配器扩展。
    - 在本地注册一个新的自定义适配器并测试调用。

## 第三阶段：多 Agent 协作流验证 (Local Collab)
在不启动 Telegram 的情况下，直接在控制台模拟多 Agent 辩论与协同。
- **任务 1**: 运行艺术场景模拟脚本。
    - `python demo_edu_scenarios.py` (我们将重构此脚本以支持 Pro 架构)
    - 观察 Tutor, Artist, Critic 在控制台的对话流。
- **任务 2**: 个性化引擎 (Persona) 压力测试。
    - 批量生成不同性格的回复并检查一致性。

## 第四阶段：多平台接入 (Multi-Platform)
当核心引擎稳定后，我们再选择性接入：
- **飞书 (Feishu)**: 通过 `/api` 或本地指令推送。
- **Web 控制台**: 启动 FastAPI 后端通过 Swagger 调试。
- **Telegram**: 作为最后的展示入口。

---
**如果您确认此方案，我们将从“第一阶段：运行密钥设置向导”开始执行。**
