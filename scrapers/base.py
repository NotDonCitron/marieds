import re
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Optional
from abc import ABC, abstractmethod
from urllib.parse import urljoin
import httpx
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@dataclass
class ListingResult:
    title: str
    url: str
    platform: str
    price: Optional[float] = None
    price_text: Optional[str] = None
    location: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def id(self) -> str:
        return hashlib.sha256(f"{self.url}{self.title}".encode()).hexdigest()[:16]

class BaseScraper(ABC):
    platform_name: ClassVar[str] = "unknown"
    base_url: ClassVar[str] = ""

    def __init__(self):
        self.ua = UserAgent()
        self._client = None
        self._playwright = None
        self._browser = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(headers={"User-Agent": self.ua.random}, timeout=30.0, follow_redirects=True)
        return self._client

    async def _get_browser(self):
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser

    async def _stealth_get(self, url: str, wait_ms: int = 2000) -> str:
        browser = await self._get_browser()
        page = await browser.new_page(user_agent=self.ua.random)
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(wait_ms)
            return await page.content()
        finally:
            await page.close()

    @staticmethod
    def extract_price(text: str | None) -> tuple[float | None, str | None]:
        if not text: return None, None
        match = re.search(r"([\d\s.,]+)", text)
        if match:
            raw = match.group(1).replace(" ", "").replace(".", "").replace(",", ".")
            try:
                return float(raw), text.strip()
            except: pass
        return None, text.strip()

    @abstractmethod
    async def scrape(self, query: str) -> list[ListingResult]:
        pass

    async def close(self):
        if self._client: await self._client.aclose()
        if self._browser: await self._browser.close()
        if self._playwright: await self._playwright.stop()
