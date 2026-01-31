# Artfish API 扩展指南 (API Extension Guide)

Artfish 采用类似于 **Clawdbot** 的“指针式”调用架构。通过 `APIEngine`，你可以使用统一的字符串标识符调用不同的第三方服务。

## 1. 核心概念

### 指针 (Pointer)
指针是一个字符串，格式为 `adapter_name.method_name`。
- `telegram.send_message`: 调用 Telegram 适配器的发送消息方法。
- `slack.chat.postMessage`: 调用 Slack 适配器的频道推送方法。

## 2. 如何添加新的 API 支持

要添加对新平台（如 Feishu, WeChat）的支持，请遵循以下步骤：

### 第一步：创建适配器类
在 `core/adapters/` 目录下创建一个新的 Python 文件（如 `feishu_adapter.py`），并继承 `BaseAdapter`。

```python
from core.adapters.base import BaseAdapter, APIResponse

class FeishuAdapter(BaseAdapter):
    @property
    def name(self) -> str:
        return "feishu"

    async def call(self, method: str, **kwargs) -> APIResponse:
        # 在这里实现具体的 API 调用逻辑
        if method == "send":
            # 业务逻辑...
            return APIResponse(status="success", data={"msg_id": "123"})
        return APIResponse(status="error", error="Unsupported method")
```

### 第二步：注册适配器
在 `core/api_engine.py` 的 `_init_standard_adapters` 方法中添加注册逻辑，或者在应用启动时手动注册：

```python
from core.api_engine import api_engine
from core.adapters.feishu_adapter import FeishuAdapter

api_engine.register_adapter(FeishuAdapter())
```

## 3. 调用示例

```python
from core.api_engine import api_engine

async def main():
    # 调用 Telegram
    res = await api_engine.execute("telegram.sendMessage", chat_id="123", text="Hello!")
    
    # 调用 Discord
    res = await api_engine.execute("discord.execute_webhook", 
                                   webhook_url="...", 
                                   content="Alert!")
```

## 4. 统一错误处理
所有适配器都应使用 `self.format_error(e)` 来捕获并标准化异常，确保上层引擎获得一致的 `APIResponse` 对象。
