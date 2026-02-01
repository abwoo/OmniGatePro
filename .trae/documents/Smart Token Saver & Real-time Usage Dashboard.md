# OmniGate Pro Token 节省增强与实时看板方案

## **1. 算法升级：语义级 Token 压缩 (Smart Shrinking)**
- **现有问题**: 当前压缩仅通过正则提取关键词，容易丢失上下文语义。
- **改进方案**: 
    - 在 [omni_engine.py](file:///d:/artfish/core/omni_engine.py) 中引入 **“实体保持型递归摘要”** 算法。
    - **逻辑**: 识别并保留关键实体（如：文件名、用户名、日期、特定指令），对中间冗余对话进行语义分段并生成“极简事实链”。
    - **目标**: 将压缩率稳定在 80% 以上，同时保证 DeepSeek 的回复准确度。

## **2. 核心模块：Token 追踪器 (Token Tracker)**
- 创建新文件 [token_tracker.py](file:///d:/artfish/core/token_tracker.py)，实现以下功能：
    - **全量记录**: 追踪每一次 API 调用的原始 Token 数、优化后 Token 数、节省量及使用场景。
    - **成本预估**: 根据各平台（DeepSeek, OpenAI, Claude）的费率，实时计算节省的费用（美元/人民币）。
    - **数据持久化**: 保证即使重启程序，历史节省数据也不会丢失。

## **3. 终端看板 (TUI) 升级：数据可视化**
- 在 [cli.py](file:///d:/artfish/cli.py) 的仪表盘中新增 **“📊 Token 节省看板”** 分栏。
- **展示项**:
    - **累计节省率**: 使用进度条显示整体优化效果。
    - **API 消耗排行**: 实时列出各个 API（DeepSeek, GPT-4, etc.）的 Token 占用情况。
    - **场景明细**: 标注 Token 是在“Telegram 对话”、“智能体思考”还是“本地任务”中消耗的。
    - **节省金币**: 以趣味图标形式显示累计节省的理论成本。

## **4. 后端 API 支撑**
- 在 [fastapi_gateway.py](file:///d:/artfish/core/fastapi_gateway.py) 中增加 `/api/token/stats` 接口，为前端或 TUI 提供实时统计数据。

---
**您是否同意执行此方案？我将立即开始编写核心算法并升级您的终端面板。**
