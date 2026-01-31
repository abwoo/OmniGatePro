# Artfish Studio Pro 🎨 🦞

Artfish Studio Pro 是一个高度可扩展的 **艺术教育多智能体 (Multi-Agent) 协作平台**。它不仅支持多种第三方接口（Telegram, Feishu, Discord），更核心的是其强大的 **指针式 API 引擎** 与 **专家 Agent 协作体系**。

---

##  快速开始 (CLI-First)

我们建议先在本地终端完成初始化与验证，确保核心引擎稳健运行。

### 1. 环境初始化
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 交互式配置 API 密钥 (OpenAI, DeepSeek, Telegram 等)
python cli.py setup-keys

# 3. 系统环境自检
python cli.py doctor
```

### 2. 本地引擎验证 (Pointer Engine)
验证基于字符串指针的动态调用机制：
```bash
python demo_api_engine.py
```

### 3. 多 Agent 协作演示
在不依赖任何第三方平台的情况下，直接在控制台体验专家 Agent 的辩论与协同：
```bash
python demo_art_pro.py
```

---

## ✨ 核心架构特性

- **指针式 API 引擎 (Pointer-based Engine)**: 借鉴成熟架构，支持通过 `telegram.sendMessage` 或 `feishu.send_text` 这种统一的字符串指针调用异构服务。
- **专家 Agent 协作体系**: 
    - **Tutor (导师)**: 负责艺术理论与知识引导。
    - **Artist (艺术家)**: 负责创意实现与视觉提示词。
    - **Critic (评审)**: 负责审美把关与学术辩论。
- **个性化表达引擎 (Persona Engine)**: Agent 不再是死板的回复模板，而是具有动态性格（如“耐心”、“毒舌”、“诗意”）的创意伙伴。
- **分布式任务队列**: 基于 Redis 支持高并发、可重试的任务处理流。

---

## 🧩 扩展指南

如果您想接入新的平台（如微信、钉钉）：
1. 在 `core/adapters/` 继承 `BaseAdapter` 实现新适配器。
2. 在 `APIEngine` 中注册。
3. 即可通过指针 `myplatform.method` 全局调用。

详情请参阅 **[API_EXTENSION_GUIDE.md](file:///d:/artfish/docs/API_EXTENSION_GUIDE.md)**。

---

## 📅 更新日志

- **v2.2.0 (当前)**: 
    - 引入 **Artfish Studio Pro** 架构，支持多 Agent 辩论与协同。
    - 实现 **Universal API Engine**，支持指针式跨平台调用。
    - 新增飞书 (Feishu) 与 Discord 适配器。
    - 强化 CLI 工具，支持环境诊断 (doctor) 与密钥向导。
- **v2.1.0**: 引入统一 LLM 网关与 5 大艺术专业技能。

---
**Artfish Studio Pro - 重新定义 AI 艺术协作**
