# OmniGate Pro 系统稳定性与同步机制全量修复方案

## **1. 核心修复：配置同步与环境加载 (Synchronization Fix)**
- **问题**: `settings` 单例加载后无法感知 `.env` 的变化，且 `questionary` 取消操作会导致脚本崩溃。
- **修复方案**:
    - **健壮性增强**: 在 `setup_keys` 中增加对 `None` 值的检查，防止 `.strip()` 报错。
    - **实时热重载**: 重构 `core/config.py`，允许手动调用 `settings.reload()` 来强制从磁盘重新加载环境变量。
    - **显式注入**: 在 `onboard` 和 `doctor` 开始前，显式调用 `load_dotenv` 并触发 `settings.reload()`。

## **2. 健壮性修复：异步任务与网络代理 (Robustness Fix)**
- **问题**: `httpx` 在处理空字符串代理或网络波动时可能挂起进度条。
- **修复方案**:
    - **代理清洗**: 在使用 `httpx` 前，严格过滤掉空字符串代理，确保传递给 `proxies` 的是有效的 URL 或 `None`。
    - **超时保护**: 为所有网络请求设置严格的 10s 超时，并增加全局异常捕获，确保进度条即使在断网情况下也能正常走完并报告错误，而不是“死掉”。

## **3. 逻辑链路优化 (Logic Flow)**
- **OpenClaw 路径纠偏**: 增强 `check_openclaw_env`，支持自动发现常见的克隆路径（如 `openclaw-main` 等），提高环境识别率。
- **配置持久化安全**: 在写入 `openclaw.json` 前增加备份机制，防止意外损坏用户的原始配置。

## **4. 新增：一键自愈 (omni fix) 增强**
- 将 `omni fix` 升级为真正的“自愈中心”，自动检查并安装缺失的 Python 依赖（通过 `pip install -r requirements.txt`），并尝试修复损坏的虚拟环境。

---
**您是否同意此全量修复方案？我将一次性解决所有已知的同步和运行 Bug，让系统达到生产级的稳定性。**
