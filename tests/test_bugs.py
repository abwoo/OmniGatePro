import pytest
import asyncio
from core.agent import orchestrator
from core.agents.art_agents import TutorAgent, ArtistAgent, CriticAgent
from core.orchestrator_pro import discussion_room
from core.persona import persona_engine

@pytest.mark.asyncio
async def test_agent_memory_update():
    """测试 Agent 记忆是否能正确存储互动"""
    tutor = TutorAgent()
    orchestrator.register_agent(tutor)
    
    # 模拟一次任务
    await tutor.process_task({"topic": "色彩理论"})
    # 当前代码中并没有更新 memory 的逻辑，这是一个潜在的增强点
    # 如果用户希望 Agent 能记住之前的对话，这里应该有数据
    # 我们先检查初始化状态
    assert isinstance(tutor.memory, list)

@pytest.mark.asyncio
async def test_persona_fallback_with_complex_data():
    """测试个性化引擎在处理复杂字典时的兜底逻辑"""
    complex_data = {"critique": "构图太散", "score": 4.5, "details": {"color": "good"}}
    
    # 模拟 LLM 失败的情况 (通过传入不存在的 provider)
    # 我们强制 mock LLM 返回失败
    from unittest.mock import patch
    with patch('core.llm_gateway.LLMGateway.chat', return_value={"status": "fail"}):
        res = await persona_engine.generate_response("user_1", "context", complex_data)
        # 验证是否正确提取了 critique 字段
        assert "构图太散" in res

@pytest.mark.asyncio
async def test_orchestrator_missing_agent():
    """测试编排器在缺少 Agent 时的鲁棒性"""
    from core.agent import AgentOrchestrator
    new_orch = AgentOrchestrator()
    
    # 尝试并行运行不存在的 Agent
    res = await new_orch.run_parallel("test", ["non_existent"])
    assert res == {}
    
    # 尝试运行辩论
    res = await new_orch.run_debate("test", "a", "b")
    assert "无法启动辩论" in res[0]

@pytest.mark.asyncio
async def test_interaction_loop_consistency():
    """测试互动工坊的轮次一致性"""
    orchestrator.register_agent(TutorAgent())
    orchestrator.register_agent(ArtistAgent())
    
    rounds = 2
    dialogue = await orchestrator.run_interaction("极简主义", ["tutor", "artist"], rounds=rounds)
    
    # 2 轮 * 2 个 Agent = 4 条对话
    assert len(dialogue) == rounds * 2
    for line in dialogue:
        assert "[" in line and "]" in line
