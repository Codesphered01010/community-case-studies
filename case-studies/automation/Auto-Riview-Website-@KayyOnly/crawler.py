from collections import deque
from dataclasses import dataclass, field
from typing import Set
from urllib.parse import urljoin, urlparse, urldefrag

from playwright.async_api import BrowserContext


# Ekstensi file yang bukan halaman HTML — skip semua ini
SKIP_EXTENSIONS = {
    ".xml", ".json", ".txt", ".rss", ".atom",          # data/feed
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt",  # dokumen
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",  # gambar
    ".mp4", ".webm", ".mp3", ".wav", ".ogg",           # media
    ".zip", ".rar", ".gz", ".tar",                     # arsip
    ".css", ".js", ".woff", ".woff2", ".ttf",          # asset
}

# Keyword di URL yang biasanya bukan halaman biasa
SKIP_KEYWORDS = {
    "sitemap", "feed", "rss", "atom", "robots.txt",
    "wp-json", "wp-admin", "wp-login", "xmlrpc",
    "cdn-cgi", ".well-known",
}


@dataclass
class CrawlConfig:
    max_pages: int = 8
    timeout_ms: int = 30_000


class WebsiteCrawler:
    def __init__(self, start_url: str, config: CrawlConfig | None = None):
        self.start_url = start_url
        self.config = config or CrawlConfig()
        self.base_domain = urlparse(start_url).netloc
        self.visited: Set[str] = set()

    def _normalize(self, url: str) -> str:
        clean, _ = urldefrag(url)
        return clean.rstrip("/")

    def _is_internal(self, url: str) -> bool:
        return urlparse(url).netloc == self.base_domain

    def _should_skip(self, url: str) -> bool:
        """Return True jika URL ini bukan halaman HTML yang perlu dicrawl."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Skip berdasarkan ekstensi file
        for ext in SKIP_EXTENSIONS:
            if path.endswith(ext):
                return True

        # Skip berdasarkan keyword di URL
        full = url.lower()
        for keyword in SKIP_KEYWORDS:
            if keyword in full:
                return True

        return False

    async def crawl(self, context: BrowserContext) -> list[str]:
        queue = deque([self._normalize(self.start_url)])
        collected: list[str] = []

        while queue and len(collected) < self.config.max_pages:
            current_url = queue.popleft()

            if current_url in self.visited:
                continue
            if self._should_skip(current_url):
                continue

            self.visited.add(current_url)
            page = await context.new_page()
            try:
                response = await page.goto(
                    current_url,
                    wait_until="domcontentloaded",
                    timeout=self.config.timeout_ms,
                )

                # Skip halaman yang bukan HTML (cek content-type)
                content_type = ""
                if response:
                    content_type = response.headers.get("content-type", "")
                if content_type and "html" not in content_type:
                    continue

                collected.append(current_url)

                links = await page.eval_on_selector_all(
                    "a[href]",
                    "anchors => anchors.map(a => a.getAttribute('href')).filter(Boolean)",
                )

                for href in links:
                    absolute = self._normalize(urljoin(current_url, href))
                    if not absolute.startswith(("http://", "https://")):
                        continue
                    if not self._is_internal(absolute):
                        continue
                    if absolute in self.visited:
                        continue
                    if self._should_skip(absolute):   # filter sebelum masuk queue
                        continue
                    if absolute not in queue:
                        queue.append(absolute)

            except Exception as e:
                # Kalau satu halaman gagal, lanjut ke berikutnya
                print(f"  [skip] {current_url} — {type(e).__name__}: {str(e)[:80]}")
            finally:
                await page.close()

        return collected