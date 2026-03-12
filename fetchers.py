import random
import asyncio
import httpx
import logging
from enum import Enum
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class Action(Enum):
    SUCCESS = "SUCCESS"
    DISCARD = "DISCARD"
    RETRY = "RETRY"
    BLOCK = "BLOCK"

class FetcherError(Exception):
    """Exception personnalisée pour déclencher les retries de tenacity."""
    pass

class HttpFetcher:
    def __init__(self, user_agents):
        self.client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
        self.user_agents = user_agents

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, FetcherError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def fetch(self, url: str):
        headers = {"User-Agent": random.choice(self.user_agents)}
        response = await self.client.get(url, headers=headers)
        
        # Logique de classification
        if 200 <= response.status_code < 300:
            return {"action": Action.SUCCESS, "html": response.text}
        
        if response.status_code in [408, 429, 500, 502, 503, 504]:
            raise FetcherError(f"HTTP {response.status_code} - Retrying")
            
        return {"action": Action.DISCARD}

    async def close(self):
        await self.client.aclose()

class BrowserFetcher:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self

    async def fetch(self, url: str):
        if not self.browser:
            raise RuntimeError("Browser not started. Use 'async with BrowserFetcher()'")
        
        # On utilise un context éphémère pour chaque requête (très performant)
        context = await self.browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            content = await page.content()
            return {"action": Action.SUCCESS, "html": content}
        finally:
            await context.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()