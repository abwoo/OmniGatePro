# Artfish Studio: 艺术教育垂直领域多智能体平台重构计划

## 1. 核心定位与品牌重塑 (Pivot to Art Education)
- **项目更名**：从 "EduSense" 回归并升级为 **"Artfish Studio"**。
- **垂直领域聚焦**：专注艺术教育（绘画、设计、审美、艺术史），移除通用学科逻辑。
- **对齐 Clawdbot**：引入“网关 + 智能体协作”模式，支持多 Agent 在同一艺术项目下协同工作。

## 2. 艺术教育核心技能 (Art-Specific Skills)
- **ArtTutorSkill (艺术导师)**：提供色彩理论、构图法则、艺术流派知识图谱。
- **ArtCritiqueSkill (艺术鉴赏)**：模拟专业评审，对艺术作品（或描述）进行审美评估与建议。
- **StudioSkill (工作室协作)**：
    - **Agent Handoff**：允许用户 Agent 将任务从“构思”转交给“创作”或“评审”。
    - **Collaborative Project**：支持多智能体共享艺术项目上下文。

## 3. Telegram 任务机器人实现 (Telegram Bot Integration)
- **核心开发**：使用提供的 API 令牌 (`8434211814:AAFUTWoELMEIio7O8zkKo9siFp233MUQt2A`) 构建 `ArtfishTelegramBot`。
- **功能特性**：
    - `/tutor`：艺术理论咨询。
    - `/critique`：上传作品描述或思路获取专业点评。
    - `/collaborate`：开启多 Agent 协同创作模式。
- **并发与安全**：支持多用户独立会话，集成错误处理与详细日志记录。

## 4. 技术架构方案 (Technical Architecture)
- **Gateway 升级**：引入 `StudioGateway` 概念，管理艺术项目会话 (ArtSessions) 与 Agent 路由。
- **多 Agent 协议**：设计轻量级的 Agent 间通信协议，使终端用户的 Agent 能够在此平台上进行“自主交互”。
- **存储增强**：在 `db/models.py` 中增加 `ArtProject`、`AgentRole` 与 `CollabLog` 模型。

## 5. 测试与验证标准 (Testing & Verification)
- **单元测试**：覆盖所有艺术技能工具的逻辑。
- **集成测试**：模拟 Telegram -> Gateway -> 多 Skill 调用的全链路。
- **端到端测试**：验证“构思 -> 创作 -> 评审”的多 Agent 协同闭环。
- **交付文档**：提供详细的部署指南与多 Agent 协作协议说明。
