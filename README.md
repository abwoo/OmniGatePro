# Artfish: Model-Agnostic Artistic Agent Runtime

`artfish` 是一个教育性的运行时引擎，旨在将“艺术创作”视为一个严格定义的执行过程。与传统的艺术生成工具不同，`artfish` 的核心目标不是最终的像素输出，而是**执行追踪（ExecutionTrace）**——即创作过程中的决策日志。

## 1. 核心理念

*   **产品即追踪 (The Product is the Trace)**: 我们关注决策过程。系统记录每一个 `AtomicAction` 的状态、耗时、成本和结果。
*   **模型无关 (Model Agnosticism)**: 核心逻辑不依赖于任何具体的 AI 模型（如 OpenAI 或 Diffusers）。所有模型通过 `BackendAdapter` 抽象层接入。
*   **意图驱动 (Intent-First)**: 系统处理结构化的 `ArtIntent`，而非松散的文本提示词。

## 2. 核心架构

### A. 数据结构 (`artfish.core`)
*   **`ArtIntent`**: 声明式的用户意图。包含目标（goals）、约束（constraints）和元数据。
*   **`ExecutionPlan`**: 编译后的 DAG（有向无环图）。将意图分解为一系列有依赖关系的原子操作。
*   **`ExecutionTrace`**: 唯一的真理来源。记录从开始到结束的所有 `TraceEvent`。

### B. 执行引擎
*   **`Compiler`**: 将高级意图转换为可执行计划。支持自动依赖推断（如：Transform 操作自动依赖 Generate 操作）。
*   **`Runtime`**: 执行主循环。管理生命周期（PENDING -> RUNNING -> COMPLETED/FAILED），支持**并行执行**和**重试机制**。
*   **`Dispatcher`**: 智能路由。根据操作类型和后端提示，将任务分配给合适的 `BackendAdapter`。

### C. 抽象接口 (`artfish.interfaces`)
*   **`BackendAdapter`**: 抽象基类。定义了后端必须实现的 `execute` 接口，确保系统可扩展性。

## 3. 快速开始

### 在线体验 (Web Version)
您可以直接访问部署在 GitHub Pages 上的 Web 版本进行体验：
👉 **[Artfish AI Platform 在线演示](https://abwoo.github.io/artfish-ai-platform/)**

> **提示**：Web 版本需要连接后端服务。如果您在本地运行后端 (`python api/main.py`)，请在登录页面的 **API Config** 中确保地址设置为 `http://localhost:8000`。
> **预置管理员账号**：`admin@example.com` / `Admin123!@#456`

### 环境要求
*   Python 3.10+
*   PowerShell (可选，用于快捷调用)

### 安装
```powershell
git clone <repository-url>
cd artfish
pip install -r requirements.txt
```

### 单行运行 (PowerShell)
```powershell
.\artfish.ps1 --goals "generate_landscape" "add_sunset_style" --max-steps 10
```

### 命令行运行
```bash
python main.py --goals "create_character" "colorize" --parallel
```

## 4. 目录结构

```text
artfish/
├── core/
│   ├── intent.py       # 意图模型
│   ├── plan.py         # 执行计划与原子操作
│   ├── runtime.py      # 编译器、运行时与调度器
│   ├── trace.py        # 追踪系统
│   └── context.py      # 执行上下文与结果注入
├── interfaces/
│   └── backend.py      # 适配器接口
├── backends/
│   └── mock.py         # 模拟后端实现（用于测试）
├── main.py             # CLI 接口与演示脚本
└── artfish.ps1         # PowerShell 快捷入口
```

## 5. 高级功能

*   **依赖注入**: `Runtime` 会自动将前置操作的结果注入到后续操作的参数中。
*   **并行计算**: 互不依赖的操作（如同时生成两张互不相关的草图）会在不同的线程中并行执行。
*   **错误恢复**: 支持 `max_retries` 配置，后端执行失败时可自动尝试重新运行。
*   **统计分析**: 运行结束后自动生成执行报告，包括成功率、总成本、平均耗时等。

## 6. 开发约束

1.  **禁止直接导入供应商 SDK**: 严禁在 `core` 目录中导入 `openai` 等包。
2.  **强制类型提示**: 所有代码必须使用 Python `typing` 进行类型标注。
3.  **异常记录**: 任何后端执行错误都应转化为 `FAILED` 状态的事件记录，而不是导致程序崩溃。

---

**Artfish** - *Bringing Rigor to Computational Creativity.*
