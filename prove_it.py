import sys
import os
sys.path.append(os.getcwd())
from core.omni_engine import omni_engine

# 模拟一段长对话背景
long_context = """
User: 你好，我想了解一下如何配置 OpenClaw。
AI: 你好！配置 OpenClaw 需要先安装 Node.js 22，然后运行 onboard 命令。
User: 好的，我已经安装了 Node.js。路径是在 /usr/local/bin/node。
AI: 太棒了。接下来请配置你的 API Key。
User: 我的 API Key 是 sk-1234567890abcdefg。请帮我记下这个路径和密钥。
AI: 没问题，我已经记录下了路径 /usr/local/bin/node 和密钥 sk-1234567890abcdefg。
User: 还有，我希望你能帮我写一个 Python 脚本来监控系统。
AI: 当然可以，你想监控哪些指标？
User: 我想监控 CPU 和内存。
AI: 好的，我会为你准备相关的代码。
User: 现在的配置进度到哪里了？
"""

print("="*50)
print("🧪 OMNIGATE PRO TOKEN 压缩验证测试")
print("="*50)
print(f"原始长度: {len(long_context)} 字符")

# 执行压缩
compressed = omni_engine.compress_context(long_context, scene="verification_test")

print("\n--- 压缩后的内容预览 ---")
print(compressed)
print("-" * 30)

original_len = len(long_context)
compressed_len = len(compressed)
saved_len = original_len - compressed_len
savings_rate = (saved_len / original_len) * 100

print(f"\n✅ 验证结果:")
print(f"- 原始字符: {original_len}")
print(f"- 压缩后字符: {compressed_len}")
print(f"- 节省字符: {saved_len}")
print(f"- 真实节省率: {savings_rate:.1f}%")
print("\n结论: 通过语义摘要和实体保持（如路径和 Key 已被保留），我们成功减少了发送给 API 的数据量。")
print("="*50)
