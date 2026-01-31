import sys
import os
import logging
from datetime import datetime

# 配置商业级日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("artfish")

# 确保当前目录在路径中，以便正确导入 artfish 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intent import ArtIntent
from core.plan import Compiler
from core.runtime import Runtime
from backends.mock import MockBackend
from db.session import init_db, SessionLocal
from core.exporter import Exporter
from core.config import settings

def main():
    """
    artfish 框架的执行入口。
    演示了从意图定义、编译到运行时追踪的完整生命周期。
    """
    # 0. 初始化数据库
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info("Initializing persistence layer...")
    init_db()
    db_session = SessionLocal()

    try:
        # 1. 实例化模拟后端 (Model Agnostic)
        backend = MockBackend()
        
        # 2. 定义结构化艺术意图 (Intent-First)
        intent = ArtIntent(
            goals=["high_contrast_abstract", "cyberpunk_neon_blue"],
            constraints={
                "max_steps": 5,
                "style": "cinematic",
                "aspect_ratio": "16:9"
            },
            user_id="user_premium_001",
            api_key="sk-artfish-test-key",
            priority=1
        )
        
        # 3. 编译意图为执行计划 (Compilation)
        logger.info(f"Compiling intent for user: {intent.user_id}")
        plan = Compiler.compile(intent)
        
        # 4. 启动运行时并执行 (Execution Loop)
        logger.info(f"Starting runtime with {len(plan.actions)} actions...")
        runtime = Runtime(backend)
        trace = runtime.run(plan, intent=intent, db_session=db_session)
        
        # 5. 输出最终的执行轨迹 (The Product is the Trace)
        # 对于核心产出（Trace），我们保留清晰的打印格式，但去掉容易引起歧义的符号
        print("\n" + "="*20 + " FINAL EXECUTION TRACE " + "="*20)
        print(trace.to_json())
        print("="*63)
        
        logger.info(f"Execution finished. Total Cost: {trace.total_cost:.4f} USD")
        logger.info("Trace has been persisted to the database.")

        # 6. 导出结果 (Commercial Evidence)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = f"exports/trace_{timestamp}.json"
        pdf_path = f"exports/report_{timestamp}.pdf"
        
        Exporter.export_json(trace, json_path)
        Exporter.export_pdf(trace, pdf_path, user_id=intent.user_id)
        
        logger.info(f"Results exported to: {json_path} and {pdf_path}")

    finally:
        db_session.close()

if __name__ == "__main__":
    main()
