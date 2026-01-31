import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from interfaces.telegram_bot import ArtfishStudioBot
from core.trace import ExecutionTrace, TraceEvent, ActionStatus
from datetime import datetime

@pytest.fixture
def bot():
    with patch('interfaces.telegram_bot.ApplicationBuilder'):
        return ArtfishStudioBot("fake_token")

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
    # Mock result from tutor skill
    result = "这是一条艺术建议"
    response = bot._format_studio_response("art_tutor", "get_theory", result)
    assert "艺术导师建议" in response
    assert "这是一条艺术建议" in response

@pytest.mark.asyncio
async def test_format_response_critique(bot):
    result = {
        "overall_score": 85.5,
        "expert_feedback": "创意不错",
        "improvement_tip": "注意细节"
    }
    response = bot._format_studio_response("art_critique", "critique_concept", result)
    assert "专业评审报告" in response
    assert "85.5" in response
    assert "创意不错" in response

@pytest.mark.asyncio
async def test_error_handling(bot):
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_chat_action = AsyncMock()
    
    # Force an error during skill execution
    with patch('asyncio.to_thread', side_effect=Exception("Execution Error")):
        await bot._execute_art_task(update, "art_tutor", "get_theory", concept="test")
    
    update.message.reply_text.assert_called_with("❌ 协作过程中出现小插曲：Execution Error")
