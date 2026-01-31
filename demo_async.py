import logging
from datetime import datetime
from core.worker import execute_intent_task

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("artfish-async")

def trigger_async_job():
    """
    模拟商业 API 接收到请求并将其推入异步队列。
    """
    intent_data = {
        "goals": ["async_masterpiece", "futuristic_city"],
        "constraints": {"style": "hyper-realistic"},
        "user_id": "user_premium_999",
        "api_key": "sk-async-key-123",
        "priority": 2,
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
    }
    
    logger.info(f"[*] Dispatching intent to Celery worker: {intent_data['user_id']}")
    
    # 在没有 Redis 的环境下，这行会报错。
    # 在商业生产环境中，这会将任务发送到 Redis 队列。
    try:
        task = execute_intent_task.delay(intent_data)
        logger.info(f"[+] Task dispatched! Task ID: {task.id}")
        logger.info("You can now check the task status using the Task ID.")
    except Exception as e:
        logger.error(f"[-] Failed to dispatch task: {e}")
        logger.warning("Make sure Redis is running and REDIS_URL is correctly set.")

if __name__ == "__main__":
    trigger_async_job()
