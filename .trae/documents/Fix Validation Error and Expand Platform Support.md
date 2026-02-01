# OmniGate Pro 错误修复与配置增强计划

## **1. 错误诊断报告 (Diagnostic Report)**
- **错误现象**: 在运行 `omni run` 启动网关时，程序发生崩溃并抛出 `pydantic.ValidationError`。
- **根本原因**: 环境变量或 `.env` 文件中的 `DEBUG` 被设置为 `*`（通常由 shell 调试模式产生）。由于 `core/config.py` 中 `Settings.DEBUG` 类型定义为 `bool`，Pydantic 无法将 `*` 解析为布尔值，导致校验失败。
- **影响范围**: 整个应用程序无法正常启动，因为配置类 `Settings` 在核心模块中被广泛引用。

## **2. 修复步骤 (Implementation Steps)**

### **Step 1: 增强配置类校验 (Fix & Expand Config)**
- 修改 [config.py](file:///d:/artfish/core/config.py)：
    - 为 `DEBUG` 字段添加 Pydantic 校验器（Validator），将 `*`、`1`、`true` 等常见字符串智能转换为布尔值，防止崩溃。
    - 扩展 `Settings` 类，增加以下主流模型与平台的配置项：
        - **模型**: GPT-4 (OpenAI), Claude, Gemini, Llama (Groq/Ollama), 混元 (Hunyuan), 通义千问 (Qwen)。
        - **平台**: Discord Bot Token, 飞书 App Secret, Slack Bot Token, 钉钉 Webhook 等。

### **Step 2: 升级交互式配置向导 (Upgrade CLI)**
- 修改 [cli.py](file:///d:/artfish/cli.py)：
    - 重构 `setup_keys` 指令，支持多分类密钥设置（大模型类、国内大模型类、社交平台类）。
    - 更新 `onboard` 指令，将新增的密钥自动同步至 OpenClaw 的 `openclaw.json` 配置文件中。

### **Step 3: 文档与示例 (Documentation)**
- 创建 `docs/CONFIG_EXAMPLES.md`，提供包含所有主流平台配置的详细 `.env` 示例及 OpenClaw 配置参考。

## **3. 配置示例 (.env Example)**
```env
# 核心配置
DEBUG=false
FORCE_SYNC_EXECUTION=true

# 大模型 API
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-...
GEMINI_API_KEY=...
QWEN_API_KEY=...
HUNYUAN_API_KEY=...

# 社交平台
TELEGRAM_BOT_TOKEN=...
DISCORD_BOT_TOKEN=...
FEISHU_APP_ID=...
FEISHU_APP_SECRET=...
```

## **4. 验证方案 (Verification)**
- 运行测试脚本模拟 `DEBUG=*` 环境，确保 `Settings` 能够正常加载不再崩溃。
- 执行 `omni onboard` 检查生成的 `openclaw.json` 是否包含新增的模型提供商。
