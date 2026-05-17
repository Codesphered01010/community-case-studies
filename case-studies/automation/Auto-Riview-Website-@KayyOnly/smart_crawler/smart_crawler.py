from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from playwright.async_api import BrowserContext

from smart_crawler.priority_engine import PriorityEngine, PrioritySignal
from smart_crawler.route_detector import RouteDetector
from smart_crawler.sitemap_parser import SitemapParser


@dataclass
class SmartCrawlerConfig:
    max_pages: int = 20
    max_depth: int = 3


@dataclass
class CrawlNode:
    url: str
    depth: int = 0
    source_text: str = ""


@dataclass
class SmartCrawlerResult:
    pages: list[str] = field(default_factory=list)
    issues: dict = field(default_factory=lambda: {"broken_routes": [], "duplicate_pages": [], "dead_links": [], "redirect_loops": []})
    structure: dict = field(default_factory=lambda: {"total_routes": 0, "total_internal_links": 0, "total_external_links": 0})
    important_pages: dict = field(default_factory=dict)


class SmartWebsiteCrawler:
    def __init__(self, start_url: str, config: SmartCrawlerConfig | None = None):
        self.start_url = start_url
        self.base_domain = urlparse(start_url).netloc
        self.config = config or SmartCrawlerConfig()
        self.route_detector = RouteDetector()
        self.priority_engine = PriorityEngine()
        self.sitemap_parser = SitemapParser()

    def _internal(self, url: str) -> bool:
        return urlparse(url).netloc == self.base_domain

    async def crawl(self, context: BrowserContext) -> SmartCrawlerResult:
        queue = deque([CrawlNode(self.route_detector.normalize(self.start_url), 0, "entry")])
        visited: set[str] = set()
        route_patterns: set[str] = set()
        result = SmartCrawlerResult()

        sitemap_info = await self.sitemap_parser.discover(context, self.start_url)
        for sm_url in sitemap_info.get("sitemap", [])[:20]:
            if sm_url.startswith("http") and self._internal(sm_url):
                queue.append(CrawlNode(self.route_detector.normalize(sm_url), 1, "sitemap"))

        while queue and len(result.pages) < self.config.max_pages:
            node = queue.popleft()
            if node.depth > self.config.max_depth or node.url in visited:
                continue

            page = await context.new_page()
            try:
                resp = await page.goto(node.url, wait_until="domcontentloaded", timeout=30000)
                if not resp or resp.status >= 400:
                    result.issues["broken_routes"].append(node.url)
                    continue

                title = await page.title()
                body_text = await page.text_content("body") or ""
                if "not found" in (title + body_text[:200]).lower() and resp.status == 200:
                    result.issues["dead_links"].append(node.url)

                visited.add(node.url)
                result.pages.append(node.url)

                pattern = self.route_detector.pattern(node.url)
                if pattern in route_patterns:
                    result.issues["duplicate_pages"].append(node.url)
                route_patterns.add(pattern)

                priority = self.priority_engine.score(PrioritySignal(url=node.url, text=node.source_text + " " + title))
                if priority > 0:
                    result.important_pages[node.url] = {
                        "score": priority,
                        "tags": self.priority_engine.classify(PrioritySignal(url=node.url, text=node.source_text + " " + title)),
                    }

                links = await page.eval_on_selector_all(
                    "a[href], [role='link'][href], nav a[href], footer a[href], aside a[href]",
                    "els => els.map(e => ({href: e.getAttribute('href'), text: (e.innerText || '').trim()})).filter(e => !!e.href)",
                )
                result.structure["total_internal_links"] += len([l for l in links if l.get("href", "").startswith("/") or self.base_domain in l.get("href", "")])
                result.structure["total_external_links"] += len([l for l in links if l.get("href", "").startswith("http") and self.base_domain not in l.get("href", "")])

                for link in links:
                    abs_url = self.route_detector.normalize(urljoin(node.url, link["href"]))
                    if not abs_url.startswith(("http://", "https://")):
                        continue
                    if not self._internal(abs_url):
                        continue
                    if abs_url in visited:
                        continue
                    queue.append(CrawlNode(abs_url, node.depth + 1, link.get("text", "")))

                # basic infinite scroll support
                await page.mouse.wheel(0, 2500)
                await page.wait_for_timeout(300)
            finally:
                await page.close()

        result.structure["total_routes"] = len(route_patterns)
        return result
