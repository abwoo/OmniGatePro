import json
import os
import time
from typing import Dict, List, Any
from threading import Lock

class TokenTracker:
    """
    Token 消耗与节省追踪器：负责记录各 API 的使用数据并计算节省率。
    """
    def __init__(self, storage_path: str = "token_stats.json"):
        self.storage_path = storage_path
        self.lock = Lock()
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_original": 0,
            "total_optimized": 0,
            "total_saved": 0,
            "providers": {}, # e.g., {"deepseek": {"original": 0, "optimized": 0}}
            "scenes": {},    # e.g., {"telegram": 0, "agent": 0}
            "history": []    # 最近 50 条记录
        }

    def _save_stats(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    def record(self, provider: str, scene: str, original: int, optimized: int):
        """记录一次 Token 消耗"""
        with self.lock:
            saved = original - optimized
            
            # 更新总体数据
            self.stats["total_original"] += original
            self.stats["total_optimized"] += optimized
            self.stats["total_saved"] += saved
            
            # 更新厂商数据
            if provider not in self.stats["providers"]:
                self.stats["providers"][provider] = {"original": 0, "optimized": 0, "saved": 0}
            self.stats["providers"][provider]["original"] += original
            self.stats["providers"][provider]["optimized"] += optimized
            self.stats["providers"][provider]["saved"] += saved
            
            # 更新场景数据
            self.stats["scenes"][scene] = self.stats["scenes"].get(scene, 0) + optimized
            
            # 记录历史
            entry = {
                "timestamp": time.time(),
                "provider": provider,
                "scene": scene,
                "original": original,
                "optimized": optimized,
                "saved": saved
            }
            self.stats["history"].append(entry)
            if len(self.stats["history"]) > 50:
                self.stats["history"].pop(0)
            
            self._save_stats()

    def get_summary(self) -> Dict[str, Any]:
        """获取摘要数据用于看板展示"""
        with self.lock:
            total = self.stats["total_original"]
            saved = self.stats["total_saved"]
            rate = (saved / total * 100) if total > 0 else 0
            
            return {
                "total_original": total,
                "total_optimized": self.stats["total_optimized"],
                "total_saved": saved,
                "savings_rate": round(rate, 1),
                "providers": self.stats["providers"],
                "recent_history": self.stats["history"][-5:]
            }

# 全局单例
token_tracker = TokenTracker()
