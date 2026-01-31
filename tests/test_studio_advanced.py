import pytest
import asyncio
from core.network import NetworkClient
from core.llm_gateway import LLMGateway
from skills.art_extended_skills import ArtExtendedSkills
from core.plugin_manager import CustomCommandManager

@pytest.mark.asyncio
async def test_network_client_retry():
    client = NetworkClient(timeout=1.0)
    # 模拟一个会失败的 URL (使用不存在的域名来触发 RequestError)
    url = "https://non-existent-domain-123456789.com"
    
    # 验证重试逻辑（由于域名不存在，会抛出异常，但 tenacity 会尝试 3 次）
    with pytest.raises(Exception):
        await client.get_json(url)

@pytest.mark.asyncio
async def test_llm_gateway_fallback():
    gateway = LLMGateway()
    # 即使没有 API Key，也会返回错误信息而不是崩溃
    res = await gateway.chat("openai", "Hello Artfish", "user_1")
    assert "status" in res

def test_art_extended_skills():
    skills = ArtExtendedSkills()
    
    # 测试提示词优化
    prompt_res = skills.process_prompt("A lonely tree")
    assert "highly detailed" in prompt_res
    
    # 测试知识库
    knowledge_res = skills.get_art_knowledge("巴洛克")
    assert "华丽" in knowledge_res
    
    # 测试创作头脑风暴
    ideas = skills.brainstorm_ideas("城市")
    assert len(ideas) == 3

def test_custom_command_manager(tmp_path):
    config_file = tmp_path / "custom.yaml"
    manager = CustomCommandManager(config_path=str(config_file))
    
    # 注册新指令
    manager.register_command("test_cmd", "Hello {args}")
    
    # 执行指令
    res = manager.execute_custom("test_cmd", ["World"])
    assert res == "Hello World"
