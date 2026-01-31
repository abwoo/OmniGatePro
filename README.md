# OmniGate Pro

OmniGate Pro 是一个开源、自托管的 **全能 AI 智能体网关**。它连接了大模型、即时通讯平台与本地设备，让 AI 具备在您的电脑上直接完成真实任务的能力。

---

## 🌟 核心价值

- **本地优先**: 数据存储在本地，保障隐私。
- **消息驱动**: 通过 Telegram, Discord, Feishu 即可控制您的设备。
- **真实执行**: 不仅能聊天，还能跑脚本、管文件、控制浏览器。
- **Token 优化**: 专为 Clawdbot 设计的插件模式，大幅节省 Token 消耗。

---

## 📚 文档资源

- [OMNIGATE_GUIDE.md (学习手册)](docs/OMNIGATE_GUIDE.md)
- [PRO_ARCHITECTURE.md (架构规范)](docs/PRO_ARCHITECTURE.md)
- [API_EXTENSION_GUIDE.md (API 扩展指南)](docs/API_EXTENSION_GUIDE.md)

---

## 🚀 快速开始 (CLI-First)

### 1. 环境初始化
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 交互式配置密钥
python cli.py setup-keys

# 3. 系统环境自检
python cli.py doctor
```

### 2. 功能演示
验证 OmniGate 的本地执行与协作能力：
```bash
python demo_omni_pro.py
```

---

## 📅 更新日志

- **v3.0.0 (当前)**: 
    - 品牌升级为 **OmniGate Pro**，定位全能 AI 智能体网关。
    - 新增本地执行技能 (System, File Skills)。
    - 新增 **Clawdbot 插件适配器**，支持任务卸载与 Token 优化。
    - 实现基于 YAML 的 **标准化工作流系统**。
- **v2.2.0**: 引入多 Agent 辩论与协同架构。

---
**OmniGate Pro - 让大模型具备真实行动力**
