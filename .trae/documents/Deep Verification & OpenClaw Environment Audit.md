# OmniGate Pro 深度入驻校验与环境自检方案

## **1. 全量 API 连通性校验 (Full API Audit)**
- **现有问题**: 校验仅覆盖了少数几个模型，且忽略了 Discord/飞书等社交渠道。
- **改进方案**: 
    - 遍历 `.env` 中所有以 `_API_KEY` 或 `_TOKEN` 结尾的变量。
    - 动态生成校验任务，覆盖 **DeepSeek, OpenAI, Claude, Gemini, Groq, Qwen, Hunyuan, Zhipu, Wenxin** 等所有已录入模型。
    - 增加 **Discord Webhook** 与 **飞书 Bot** 的连通性心跳测试。

## **2. OpenClaw 本地环境深度扫描 (OpenClaw Local Audit)**
- **新增校验项**:
    - **源码存在性**: 验证 `openclaw/openclaw` 目录是否完整。
    - **依赖完备性**: 检查 `node_modules` 文件夹，确保 `pnpm install` 已执行。
    - **构建状态**: 检查 `dist` 或关键构建产物，确保 `pnpm build` 已成功。
    - **配置一致性**: 验证 `~/.openclaw/openclaw.json` 是否能被正确解析且包含必要的 `mcpServers` 配置。

## **3. 交互式进度条升级 (TUI Update)**
- 进度条将分为三个阶段：
    1. **[基础设施]**: OpenClaw 源码、Node.js 运行时、Python 虚拟环境。
    2. **[社交中枢]**: Telegram, Discord, Feishu 的 Token 有效性。
    3. **[智能大脑]**: 逐一“握手”所有已配置的 LLM API。

## **4. 实现路径**
- 修改 [cli.py](file:///d:/artfish/cli.py) 中的 `onboard` 函数。
- 完善 [llm_gateway.py](file:///d:/artfish/core/llm_gateway.py) 中的 `verify_provider` 以支持更多厂商。
- 在 `onboard` 中增加 `check_openclaw_env()` 辅助函数。

---
**您是否同意此增强方案？我将确保“一键入驻”后的每一个勾选都是经过真实网络和本地文件系统验证的。**
