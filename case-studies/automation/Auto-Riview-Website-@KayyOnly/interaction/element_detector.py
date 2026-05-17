from typing import Any

from playwright.async_api import Page


class ElementDetector:
    async def detect(self, page: Page) -> dict[str, list[dict[str, Any]]]:
        return await page.evaluate(
            """() => {
                const pick = (nodes, mapper) => Array.from(nodes).slice(0, 20).map(mapper);
                const internal = (href) => href && href.startsWith(location.origin);
                return {
                    buttons: pick(document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]'), el => ({selector: el.tagName.toLowerCase() + (el.id ? '#'+el.id : ''), text: (el.textContent || el.value || '').trim().slice(0, 80)})),
                    inputs: pick(document.querySelectorAll('input[type="text"], input[type="email"], input[type="number"], input:not([type])'), el => ({name: el.name || el.id || '', type: el.type || 'text'})),
                    textareas: pick(document.querySelectorAll('textarea'), el => ({name: el.name || el.id || ''})),
                    selects: pick(document.querySelectorAll('select'), el => ({name: el.name || el.id || ''})),
                    checkboxes: pick(document.querySelectorAll('input[type="checkbox"]'), el => ({name: el.name || el.id || ''})),
                    radios: pick(document.querySelectorAll('input[type="radio"]'), el => ({name: el.name || el.id || ''})),
                    forms: pick(document.querySelectorAll('form'), (el, i) => ({index: i, action: el.action || ''})),
                    modals: pick(document.querySelectorAll('[role="dialog"], .modal, [aria-modal="true"]'), el => ({tag: el.tagName.toLowerCase()})),
                    nav_menus: pick(document.querySelectorAll('nav a[href], header a[href], .navbar a[href], .menu a[href]'), a => ({href: a.href, text: (a.textContent||'').trim().slice(0,60)})),
                    paginations: pick(document.querySelectorAll('.pagination a[href], [aria-label*="pagination" i] a[href]'), a => ({href: a.href, text: (a.textContent||'').trim()})),
                    search_bars: pick(document.querySelectorAll('input[type="search"], input[name*="search" i], input[placeholder*="search" i]'), el => ({name: el.name || el.id || ''})),
                    internal_links: pick(document.querySelectorAll('a[href]'), a => ({href: a.href, text: (a.textContent || '').trim().slice(0, 80)})).filter(a => internal(a.href))
                };
            }"""
        )
