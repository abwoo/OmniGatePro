import httpx
import logging
import asyncio
from typing import Optional, Dict, Any, Union
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup

logger = logging.getLogger("artfish.core.network")

class NetworkClient:
    """
    统一联网模块：支持 HTTP/HTTPS 请求，包含重试、超时及基础抓取功能。
    对齐 Clawdbot 的高性能网络访问标准。
    """
    def __init__(self, timeout: float = 10.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "ArtfishStudio/2.0 (Bot; +https://github.com/abwoo/artfish-ai-platform)",
            "Accept": "application/json, text/html, */*"
        }

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
        headers: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """
        发送带重试机制的 HTTP 请求。
        支持自定义超时和头部信息。
        """
        req_headers = self.headers.copy()
        if headers:
            req_headers.update(headers)
            
        async with httpx.AsyncClient(
            timeout=timeout or self.timeout, 
            follow_redirects=True,
            verify=True
        ) as client:
            logger.debug(f"Sending {method} request to {url}")
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=req_headers
            )
            response.raise_for_status()
            return response

    async def get_json(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """获取 JSON 数据并解析"""
        try:
            response = await self.request("GET", url, params=params)
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch JSON from {url}: {e}")
            raise

    async def scrape_web_content(self, url: str) -> Dict[str, Any]:
        """
        抓取网页内容并提取核心信息。
        返回包含标题、纯文本和元数据的字典。
        """
        try:
            response = await self.request("GET", url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 提取标题
            title = soup.title.string if soup.title else ""
            
            # 移除干扰标签
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
                
            # 提取正文文本
            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)
            
            return {
                "url": url,
                "title": title.strip() if title else "No Title",
                "content": clean_text[:5000], # 截断以防过长
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return {"url": url, "error": str(e), "status": "failed"}
