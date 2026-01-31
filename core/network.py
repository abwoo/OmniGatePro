import httpx
import logging
from typing import Optional, Dict, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup

logger = logging.getLogger("artfish.core.network")

class NetworkClient:
    """
    统一联网模块：支持 HTTP/HTTPS 请求，包含重试、超时及基础抓取功能。
    """
    def __init__(self, timeout: float = 10.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True
    )
    async def request(
        self, 
        method: str, 
        url: str, 
        params: Optional[Dict] = None, 
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> httpx.Response:
        """发送带重试机制的 HTTP 请求"""
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers
            )
            response.raise_for_status()
            return response

    async def get_json(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取 JSON 数据并解析"""
        try:
            response = await self.request("GET", url, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JSON from {url}: {e}")
            raise

    async def fetch_page_text(self, url: str) -> str:
        """抓取网页内容并提取文本"""
        try:
            response = await self.request("GET", url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
                
            text = soup.get_text()
            # 清理空白
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return "\n".join(chunk for chunk in chunks if chunk)
        except Exception as e:
            logger.error(f"Failed to scrape page {url}: {e}")
            raise
