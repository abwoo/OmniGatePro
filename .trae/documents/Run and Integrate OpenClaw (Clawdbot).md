# 集成与运行 OpenClaw (Clawdbot) 方案

## **1. 环境准备与构建**
1. 进入 `openclaw/openclaw` 目录。
2. 执行 `pnpm install` 安装所有依赖。
3. 执行 `pnpm build` 编译源码，确保 `dist/` 目录是最新的。

## **2. 标准化入驻与配置**
1. 运行官方 `openclaw onboard` 指令，生成基础 `openclaw.json`。
2. 注入密钥：将 `.env` 中的 DeepSeek API Key 和 Telegram Token 同步至配置文件。
3. 插件挂载：在 `openclaw.json` 的 `plugins` 部分手动注册 OmniGate Pro 的 MCP 服务路径。

## **3. 运行与验证**
1. 启动网关：执行 `pnpm gateway:dev` 进入开发监听模式。
2. 功能测试：使用 `openclaw agent` 命令进行对话测试，观察 OmniGate Pro 的 Token 压缩效果和本地任务执行能力。
3. 权限验证：通过您的 Telegram Bot 发送指令，确认 DeepSeek 推理结果能正常回传。

## **4. 完善文档**
1. 将此次实操的成功链路整理进 `COMMANDS.md`。
2. 更新 `cli.py` 中的提示语，使其更贴合真实的 OpenClaw 运行逻辑。
