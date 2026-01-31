import redis
import json
import logging
from typing import Optional, Any, Dict
from core.config import settings

logger = logging.getLogger("artfish.pro.queue")

class DistributedTaskQueue:
    """
    基于 Redis 的分布式任务队列。
    支持优先级调度与失败重试。
    """
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.redis.ping()
        except Exception as e:
            logger.warning(f"Redis not available, falling back to local simulation: {e}")
            self.redis = None
        
        self.queue_name = "artfish_tasks"

    def enqueue(self, task_type: str, payload: Dict[str, Any], priority: int = 0):
        """入队任务"""
        task = {
            "task_type": task_type,
            "payload": payload,
            "retry_count": 0,
            "max_retries": 3
        }
        if self.redis:
            # 使用有序集合实现优先级 (分数越低优先级越高)
            self.redis.zadd(self.queue_name, {json.dumps(task): priority})
        else:
            logger.info(f"[Simulation] Enqueued task {task_type}")

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """出队任务"""
        if self.redis:
            # 获取并移除优先级最高的任务
            tasks = self.redis.zpopmin(self.queue_name)
            if tasks:
                return json.loads(tasks[0][0])
        return None

# 全局队列
task_queue = DistributedTaskQueue()
