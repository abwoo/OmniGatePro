# OmniGate Pro: Clawdbot 核心增强插件与网关

OmniGate Pro 是一款专为 **Clawdbot** 设计的轻量化增强插件。它能让您的 Clawdbot 具备本地执行能力，同时大幅降低 Token 消耗。

---

## 🌟 三大核心价值

1.  **极致轻量化**: 专为低配置环境优化，移除冗余模块，核心运行内存占用极低。
2.  **Clawdbot 深度集成**: 
    - **任务卸载**: Clawdbot 可将复杂的本地脚本、文件操作卸载给 OmniGate 执行。
    - **Token 节省**: 内置本地摘要算法，自动压缩长对话上下文，节省 50%+ Token。
3.  **智能手机级 UX**: 像操作手机 App 一样简单，无需记忆复杂指令，支持标准化工作流。

---

## 🛠️ 快速安装 (3 分钟)

```powershell
pip install -r requirements.txt
python cli.py setup-keys
python cli.py doctor
```

---

## 📱 极简操作手册

### 1. 本地执行
在 Telegram 或终端中直接发送：
- `RUN: ls -R` (执行系统命令)
- `读取 config.py` (操作本地文件)

### 2. 作为 Clawdbot 插件
在 Clawdbot 的 `config.json` 中添加指针：
```json
{
  "plugins": {
    "omni": "omni.offload",
    "token_optimizer": "omni.shrink"
  }
}
```

---

## 🔗 资源链接
- [OMNIGATE_GUIDE.md (详细教程)](docs/OMNIGATE_GUIDE.md)
- [PRO_ARCHITECTURE.md (架构说明)](docs/PRO_ARCHITECTURE.md)

---
**OmniGate Pro - 让您的 AI 助手更轻、更快、更省。**
