# 📖 OmniGate Pro 全量配置手册 (Config Examples)

本手册提供了 OmniGate Pro v3 支持的所有主流 AI 模型与社交平台的配置示例。

---

## 🛠️ 环境变量 (.env) 完整示例

将以下内容保存为项目根目录下的 `.env` 文件：

```env
# --- 系统核心配置 ---
DEBUG=false                # 支持 true, false, *, 1, 0
ENV=prod                   # 运行环境: prod 或 dev
FORCE_SYNC_EXECUTION=true  # 开启本地极速同步模式 (无需 Redis)

# --- 🌍 国际主流模型 (Global LLMs) ---
DEEPSEEK_API_KEY=sk-...    # DeepSeek V3/R1 (推荐)
OPENAI_API_KEY=sk-...      # GPT-4o / GPT-4 Turbo
CLAUDE_API_KEY=sk-...      # Claude 3.5 Sonnet
GEMINI_API_KEY=...         # Google Gemini 1.5 Pro
GROQ_API_KEY=gsk_...       # 极速 Llama 3 / Mixtral

# --- 🇨🇳 国内主流模型 (Chinese LLMs) ---
QWEN_API_KEY=sk-...        # 阿里通义千问 (DashScope)
HUNYUAN_API_KEY=...        # 腾讯混元 (Hunyuan)
ZHIPU_API_KEY=...          # 智谱清言 (ChatGLM/GLM-4)
WENXIN_API_KEY=...         # 百度文心一言 (ERNIE)

# --- 💬 社交平台通道 (Channels) ---
TELEGRAM_BOT_TOKEN=...     # Telegram 机器人 Token
TELEGRAM_OWNER_ID=123456   # 您的 Telegram ID (用于安全锁定)
DISCORD_BOT_TOKEN=...      # Discord 机器人 Token
DISCORD_WEBHOOK_URL=...    # Discord 频道通知 Hook
FEISHU_APP_ID=cli_...      # 飞书自建应用 ID
FEISHU_APP_SECRET=...      # 飞书应用密钥
```

---

## 🦞 OpenClaw (Clawdbot) 联动说明

当您运行 `omni onboard` 时，系统会自动将上述 `.env` 中的密钥映射到 OpenClaw 的 `openclaw.json` 中。

### 自动生成的提供商结构示例：
```json
"models": {
  "providers": {
    "deepseek": {
      "enabled": true,
      "baseUrl": "https://api.deepseek.com",
      "apiKey": "sk-...",
      "api": "openai-completions",
      "models": [{"id": "deepseek-chat", "name": "DeepSeek Chat"}]
    },
    "qwen": {
      "enabled": true,
      "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "apiKey": "sk-...",
      "api": "openai-completions",
      "models": [{"id": "qwen-plus", "name": "通义千问 Plus"}]
    }
  }
}
```

---

## 🏥 常见错误处理

### 1. DEBUG 类型错误 (Input should be a valid boolean)
**现象**: 报错 `ValidationError: DEBUG Input should be a valid boolean`.
**修复**: OmniGate Pro v3 已内置智能校验。即使您的系统设置了 `DEBUG=*`，程序也会自动将其解析为 `True` 而不再崩溃。

### 2. 密钥不生效
**现象**: AI 无法回复或提示 401。
**修复**: 
1. 检查 `.env` 文件末尾是否有空格。
2. 运行 `omni setup-keys` 重新录入。
3. 运行 `omni onboard` 确保配置已同步至 OpenClaw。

---
**OmniGate Pro - 全能 AI 智能体网关**
