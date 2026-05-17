from urllib.parse import urlparse

from playwright.async_api import Page

from interaction.interaction_logger import InteractionEvent, InteractionReport


class NavigationTester:
    async def test_navigation(self, page: Page, base_url: str, report: InteractionReport) -> None:
        base_domain = urlparse(base_url).netloc
        links = page.locator("nav a[href], .navbar a[href], .menu a[href], .pagination a[href], a[href]")
        count = min(await links.count(), 8)

        for i in range(count):
            link = links.nth(i)
            try:
                href = await link.get_attribute("href") or ""
                if href.startswith("#") or href.startswith("javascript"):
                    continue
                full = await link.get_attribute("href") or ""
                if full.startswith("http") and urlparse(full).netloc != base_domain:
                    continue

                before = page.url
                await link.click(timeout=2500)
                await page.wait_for_timeout(700)
                after = page.url
                if before == after and href not in ("/", ""):
                    report.dead_routes += 1

                report.add(InteractionEvent(action="navigate", selector=f"a[{i}]", status="ok", url_before=before, url_after=after))
            except Exception as exc:
                report.broken_links += 1
                report.add(InteractionEvent(action="navigate", selector=f"a[{i}]", status="failed", message=str(exc)))
