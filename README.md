# Artfish Gateway 🦞

Artfish 是一个基于 Python 开发的轻量级、高性能 AI 任务执行引擎。它对齐了 **Clawdbot (OpenClaw)** 的核心架构，采用“网关 + 技能”模式，既可以作为独立的后端服务运行，也可以通过 **Model Context Protocol (MCP)** 完美集成到 Claude Desktop 等 AI 助手。

---

## 📖 目录
- [🚀 快速开始](#-快速开始)
- [✨ 核心特性](#-核心特性)
- [🧩 技能系统 (Skills)](#-技能系统-skills)
- [🛠️ 命令行控制台 (CLI)](#-命令行控制台-cli)
- [🔌 Claude 插件集成 (MCP)](#-claude-插件集成-mcp)
- [🛡️ 安全与权限](#-安全与权限)
- [📅 更新日志](#-更新日志)

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
*脚本会自动检测环境、安装依赖并启动交互式主向导。*

---

## ✨ 核心特性

- **Clawdbot 架构对齐**: 采用网关 (Gateway) 模式管理会话与工具分发。
- **模块化技能 (Skills)**: 支持动态加载 Python 编写的技能插件，灵活扩展 AI 能力。
- **AI 原生设计**: 完美适配 Anthropic MCP 协议，支持 Claude 毫秒级调用。
- **Figma 级终端交互**: 基于 `Rich` 打造，支持彩色日志、动态进度条和多级子命令。
- **高性能架构**: 全量实施延迟加载 (Lazy Loading) 与 stdio 极速传输。

---

## 🧩 技能系统 (Skills)

Artfish 的核心能力由 **Skills** 提供。每个技能可以包含多个可被 AI 调用的工具。

### 自定义技能示例
在 `skills/` 目录下创建一个 `.py` 文件：
```python
from core.skill import BaseSkill, skill_tool

class MySkill(BaseSkill):
    name = "my_skill"
    description = "我的自定义技能"

    @skill_tool(description="执行一个自定义操作")
    def do_something(self, param: str):
        return f"操作成功: {param}"
```

### 已内置技能
- **System**: 提供文件读写、终端命令执行等系统级操作。

---

## 🛠️ 命令行控制台 (CLI)

直接输入 `./artfish` 即可进入交互菜单。

| 命令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `run` | 运行意图任务 | `./artfish run "设计 Logo" --apply` |
| `status` | 实时监控指标 | `./artfish status --verbose` |
| `doctor` | 系统环境诊断 | `./artfish doctor` |
| `benchmark` | 性能压力测试 | `./artfish benchmark` |
| `config` | 交互式配置管理 | `./artfish config` |

---

## 🔌 Claude 插件集成 (MCP)

Artfish 作为 **MCP Server** 运行，赋予 Claude 操作本地系统和执行复杂任务的能力。

### 配置步骤
1. 确保已安装 MCP：`pip install mcp`
2. 打开 Claude 配置文件 (`%APPDATA%\Claude\claude_desktop_config.json`)。
3. 添加以下配置：
```json
{
  "mcpServers": {
    "artfish": {
      "command": "python",
      "args": ["d:/artfish/mcp_server.py"],
      "env": { "PYTHONPATH": "d:/artfish" }
    }
  }
}
```
4. 重启 Claude Desktop 即可看到 Artfish 提供的所有 Skills 工具。

---

## 🛡️ 安全与权限

1. **Dry-run 保护**: 默认开启预览模式，敏感操作需显式追加 `--apply`。
2. **非 Root 运行**: 建议以普通用户运行，必要时使用 `sudo` 提升。
3. **沙箱建议**: 在执行不可信命令时，建议配合 Docker 等容器化环境。

---

## 📅 更新日志

- **v0.4.0 (当前)**: 重构为 Gateway 架构，引入 Skills 系统，全面对齐 Clawdbot 设计理念。
- **v0.3.0**: 引入 MCP 协议支持，优化冷启动速度。
- **v0.2.0**: 重构终端交互，引入 Typer + Rich。

---
**Artfish Gateway - 专业的 AI 技能执行中枢**
