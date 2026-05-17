from __future__ import annotations


class DecisionEngine:
    async def decide(self, page) -> dict:
        if await page.locator("form").count() > 0:
            return {"action": "test_form", "reason": "Form ditemukan"}
        if await page.locator("input[type='search'], input[name*='search' i]").count() > 0:
            return {"action": "search", "reason": "Search bar ditemukan"}
        if await page.locator("button, [role='button']").count() > 0:
            return {"action": "click_button", "reason": "Tombol interaktif ditemukan"}
        if await page.locator("a[href]").count() > 0:
            return {"action": "navigate_link", "reason": "Link navigasi ditemukan"}
        return {"action": "scroll", "reason": "Tidak ada aksi utama, lakukan eksplorasi scroll"}
