# Artfish Studio � 🦞

Artfish Studio 是一个专为 **艺术教育垂直领域** 设计的多智能体协作平台。它采用“网关 + 艺术技能 + 多智能体协作”架构，旨在为艺术教学、创意表达和艺术创作提供专业的 AI 工具集。

---

## 📖 目录
- [🚀 快速开始](#-快速开始)
- [✨ 核心艺术特性](#-核心艺术特性)
- [🧩 艺术技能系统 (ArtSkills)](#-艺术技能系统-artskills)
- [🤖 Telegram 协作机器人](#-telegram-协作机器人)
- [🤝 多智能体协作 (Multi-Agent)](#-多智能体协作-multi-agent)
- [�️ 开发者控制台 (CLI)](#-开发者控制台-cli)
- [� 艺术插件集成 (MCP)](#-艺术插件集成-mcp)

---

## 🚀 快速开始

### 1. 环境要求
- **操作系统**: Windows 10+, macOS 12+, Linux
- **运行时**: Python 3.8+
- **必备工具**: pip

### 2. 一键式初始化
克隆项目后，在根目录下运行：

**Windows (PowerShell):**
```powershell
.\artfish.ps1
```

**Unix/Mac (Bash):**
```bash
chmod +x artfish
./artfish
```

---

## ✨ 核心艺术特性

- **艺术垂直对齐**: 内置色彩理论、构图法则、艺术流派等专业知识图谱。
- **多智能体协同**: 支持“构思、创作、评审”等不同角色的 AI Agent 在同一项目下自主交互。
- **创意工具集**: 提供专业的艺术点评、提示词优化及风格转换建议。
- **对齐业界标准**: 借鉴成熟的多智能体系统设计，确保高可用性与流畅的协作体验。

---

## 🧩 艺术技能系统 (ArtSkills)

Artfish Studio 的核心能力由 **ArtSkills** 模块驱动。

### 核心技能列表
- **ArtTutor (艺术导师)**: 提供专业的艺术理论指导与流派解析。
- **ArtCritique (艺术鉴赏)**: 模拟专业评审，对作品进行审美评估与优化建议。
- **StudioCollab (协作技能)**: 实现 Agent 间的任务转交、上下文共享与项目管理。

---

## 🤖 Telegram 协作机器人

Artfish Studio 集成了功能强大的 Telegram 机器人，支持多 Agent 交互。

### 核心功能
- **指令交互**: `/tutor`, `/critique`, `/collaborate`。
- **项目协作**: 支持开启一个艺术项目，邀请多个 AI Agent 参与创作与讨论。
- **实时反馈**: 集成详细的日志记录与用户交互反馈。

### 启动方式
1. 在 `.env` 中配置 `TELEGRAM_BOT_TOKEN`。
2. 运行启动命令：
   ```bash
   python interfaces/telegram_bot.py
   ```

---

## 🤝 多智能体协作 (Multi-Agent)

EduSense 允许终端用户的 Agent 通过标准协议接入平台。

- **自主交互**: Agent 可以根据项目进度，自主向其他 Agent 请求反馈或协同工作。
- **上下文共享**: 共享的 `ArtSession` 确保所有参与 Agent 拥有一致的项目视野。

---

## 📅 更新日志

- **v2.0.0 (当前)**: 品牌重塑为 Artfish Studio，聚焦艺术教育，引入多智能体协作机制。

---
**Artfish Studio - 释放 AI 的创意潜能**
