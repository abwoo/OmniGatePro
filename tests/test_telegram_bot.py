import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from interfaces.telegram_bot import EduSenseBot
from core.trace import ExecutionTrace, TraceEvent, ActionStatus
from datetime import datetime

@pytest.fixture
def bot():
    with patch('interfaces.telegram_bot.ApplicationBuilder'):
        return EduSenseBot("fake_token")

@pytest.mark.asyncio
async def test_start_command(bot):
    update = MagicMock()
    update.effective_user.first_name = "TestUser"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    
    await bot.start_command(update, context)
    
    update.message.reply_text.assert_called_once()
    assert "你好 TestUser" in update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_format_response_tutor(bot):
    # Mock a trace with tutor result
    trace = ExecutionTrace()
    event = TraceEvent(
        timestamp=datetime.now(),
        action_id="tutor_heuristic_tutor",
        status=ActionStatus.COMPLETED,
        result_payload="这是一条启发式建议"
    )
    trace.add_event(event)
    
    response = bot._format_response(trace, "tutor")
    assert "启发式引导" in response
    assert "这是一条启发式建议" in response

@pytest.mark.asyncio
async def test_format_response_exam(bot):
    trace = ExecutionTrace()
    event = TraceEvent(
        timestamp=datetime.now(),
        action_id="exam_generate_quiz",
        status=ActionStatus.COMPLETED,
        result_payload={
            "question": {"q": "测试题目", "level": 2, "tags": ["标签1"]}
        }
    )
    trace.add_event(event)
    
    response = bot._format_response(trace, "exam")
    assert "针对性练习题" in response
    assert "测试题目" in response

@pytest.mark.asyncio
async def test_error_handling(bot):
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_chat_action = AsyncMock()
    
    # Force an error in Gateway
    bot.gateway.execute_intent = MagicMock(side_effect=Exception("Gateway Error"))
    
    await bot._process_edu_task(update, "tutor", "test query")
    
    update.message.reply_text.assert_called_with("抱歉，处理您的请求时出现错误：Gateway Error")
