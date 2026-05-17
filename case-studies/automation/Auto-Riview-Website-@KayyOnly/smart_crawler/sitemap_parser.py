from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from playwright.async_api import BrowserContext


class SitemapParser:
    async def discover(self, context: BrowserContext, base_url: str) -> dict:
        result = {"sitemap": [], "robots_txt": None}
        page = await context.new_page()
        try:
            robots_url = urljoin(base_url, "/robots.txt")
            robots_resp = await page.goto(robots_url, wait_until="domcontentloaded", timeout=12000)
            if robots_resp and robots_resp.ok:
                body = await page.text_content("body") or ""
                result["robots_txt"] = robots_url
                for line in body.splitlines():
                    if line.lower().startswith("sitemap:"):
                        result["sitemap"].append(line.split(":", 1)[1].strip())

            if not result["sitemap"]:
                result["sitemap"].append(urljoin(base_url, "/sitemap.xml"))

            xml_page = await context.new_page()
            for sm in list(result["sitemap"]):
                try:
                    resp = await xml_page.goto(sm, wait_until="domcontentloaded", timeout=12000)
                    if not resp or not resp.ok:
                        continue
                    content = await xml_page.content()
                    root = ET.fromstring(content)
                    for loc in root.findall(".//{*}loc"):
                        if loc.text:
                            result["sitemap"].append(loc.text.strip())
                except Exception:
                    continue
            await xml_page.close()
        finally:
            await page.close()
        return result
