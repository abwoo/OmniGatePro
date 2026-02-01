# OmniGate Pro 实时入驻校验与自检系统方案

## **1. 核心逻辑升级：从“静态报告”到“实时校验”**
- **现有问题**: `onboard` 仅同步配置文件，不检查密钥是否有效，用户无法确定配置是否真实成功。
- **改进方案**: 在 `onboard` 流程中引入 **“实时连通性校验”** 阶段。

## **2. 技术实现步骤 (Technical Implementation)**

### **Step 1: 增强 LLM 网关校验能力**
- 在 [llm_gateway.py](file:///d:/artfish/core/llm_gateway.py) 中新增 `verify_connectivity(provider)` 异步方法。
- **逻辑**: 通过向 DeepSeek/OpenAI 等平台的 `/models` 或基础心跳接口发送轻量级请求，验证 API Key 的有效性。

### **Step 2: 升级 `onboard` 指令 (cli.py)**
- 使用 `rich.progress` 替代静态 Panel，展示实时进度。
- **流程**:
    1.  **配置写入**: 完成 `openclaw.json` 的同步。
    2.  **网络心跳**: 实时测试 Telegram Bot Token（访问 `api.telegram.org/bot<token>/getMe`）。
    3.  **模型握手**: 依次验证已配置的 LLM 提供商。
    4.  **环境扫描**: 验证本地 MCP 服务路径及 Python 环境是否就绪。

### **Step 3: 新增 `omni doctor` 指令**
- 创建一个专门的“系统自检”面板，支持随时运行。
- **展示内容**: 
    - 各个社交通道的实时连接状态（🟢/🔴）。
    - 各个 AI 模型的余额/有效性状态。
    - 本地磁盘空间与 CPU/内存 负载预警。

## **3. 视觉展示 (TUI Preview)**
```text
第二步：正在执行实时入驻校验...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
- [OK] 配置文件同步
- [OK] Telegram 接口响应 (Bot: @MyAssistant)
- [OK] DeepSeek API 握手成功 (Latency: 120ms)
- [ERROR] OpenAI Key 校验失败 (请检查 .env)
- [OK] MCP 插件挂载正常
```

## **4. 验证方案**
- 修改 `.env` 中的一个密钥为错误值，运行 `omni onboard` 确保系统能实时识别并报告 [ERROR]。
- 恢复正确密钥，确保进度条最终达到 100% 并显示 [OK]。
