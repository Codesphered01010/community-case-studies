import time
from dataclasses import asdict, dataclass, field
from typing import Any

from playwright.async_api import BrowserContext, Page


@dataclass
class PageCheckResult:
    url: str
    status: str = "ok"
    load_time_ms: float = 0.0
    dom_ready_ms: float = 0.0
    fcp_ms: float | None = None
    console_errors: list[dict[str, Any]] = field(default_factory=list)
    failed_requests: list[dict[str, Any]] = field(default_factory=list)
    broken_images: list[dict[str, Any]] = field(default_factory=list)
    forms: list[dict[str, Any]] = field(default_factory=list)
    links: list[dict[str, Any]] = field(default_factory=list)
    accessibility_issues: list[dict[str, Any]] = field(default_factory=list)
    screenshot_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class WebsiteChecker:
    async def check_page(self, context: BrowserContext, url: str, screenshot_path: str) -> PageCheckResult:
        result = PageCheckResult(url=url)
        page = await context.new_page()

        page.on("console", lambda m: self._capture_console(m.type, m.text, result))
        page.on("requestfailed", lambda r: result.failed_requests.append({"url": r.url, "error": str(r.failure)}))

        try:
            start = time.perf_counter()
            try:
                response = await page.goto(url, wait_until="domcontentloaded    ", timeout=30000)
            except Exception as exc:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            result.load_time_ms = round((time.perf_counter() - start) * 1000, 2)

            if response and response.status >= 400:
                result.failed_requests.append({"url": url, "status": response.status})

            perf = await page.evaluate(
                """() => {
                    const nav = performance.getEntriesByType('navigation')[0];
                    const fcp = performance.getEntriesByName('first-contentful-paint')[0];
                    return {
                        domReady: nav ? nav.domContentLoadedEventEnd - nav.startTime : 0,
                        fcp: fcp ? fcp.startTime : null
                    }
                }"""
            )
            result.dom_ready_ms = round(perf.get("domReady") or 0, 2)
            result.fcp_ms = round(perf["fcp"], 2) if perf.get("fcp") is not None else None

            result.broken_images = await self._check_broken_images(page)
            result.forms = await self._check_forms(page)
            result.links = await self._check_links(page)
            result.accessibility_issues = await self._check_accessibility(page)

            await page.screenshot(path=screenshot_path, full_page=True)
            result.screenshot_path = screenshot_path

        except Exception as exc:
            result.status = "failed"
            result.failed_requests.append({"url": url, "error": str(exc)})
        finally:
            await page.close()

        return result

    def _capture_console(self, msg_type: str, text: str, result: PageCheckResult) -> None:
        if msg_type == "error":
            result.console_errors.append({"type": msg_type, "text": text})

    async def _check_broken_images(self, page: Page) -> list[dict[str, Any]]:
        return await page.evaluate(
            """() => Array.from(document.querySelectorAll('img')).filter(i => i.complete && i.naturalWidth === 0)
                .map(i => ({src: i.src, alt: i.alt || ''}))"""
        )

    async def _check_forms(self, page: Page) -> list[dict[str, Any]]:
        return await page.evaluate(
            """() => Array.from(document.querySelectorAll('form')).map((f, idx) => ({
                index: idx,
                action: f.action || '',
                method: (f.method || 'get').toUpperCase(),
                input_count: f.querySelectorAll('input,textarea,select').length,
                has_submit: !!f.querySelector('button[type=submit],input[type=submit]')
            }))"""
        )

    async def _check_links(self, page: Page) -> list[dict[str, Any]]:
        return await page.evaluate(
            """() => Array.from(document.querySelectorAll('a[href]')).slice(0, 200).map(a => ({
                href: a.href,
                text: (a.textContent || '').trim().slice(0, 100)
            }))"""
        )

    async def _check_accessibility(self, page: Page) -> list[dict[str, Any]]:
        return await page.evaluate(
            """() => {
                const issues = [];
                document.querySelectorAll('img').forEach(img => {
                    if (!img.hasAttribute('alt')) issues.push({type: 'missing_alt', element: img.src || 'img'});
                });
                document.querySelectorAll('input,select,textarea').forEach(el => {
                    const id = el.getAttribute('id');
                    const hasLabel = id ? document.querySelector(`label[for="${id}"]`) : el.closest('label');
                    if (!hasLabel) issues.push({type: 'missing_label', element: el.name || el.id || el.tagName});
                });
                if (!document.querySelector('h1')) issues.push({type: 'missing_h1', element: 'document'});
                return issues;
            }"""
        )