from __future__ import annotations


class ActionExecutor:
    async def execute(self, page, decision: dict) -> dict:
        action = decision["action"]
        if action == "test_form":
            form_input = page.locator("form input:not([type='hidden'])")
            if await form_input.count() > 0:
                await form_input.first.fill("ai-test")
            await page.keyboard.press("Tab")
            return {"status": "ok", "detail": "form inspected"}
        if action == "search":
            search = page.locator("input[type='search'], input[name*='search' i]").first
            await search.fill("test")
            await search.press("Enter")
            await page.wait_for_timeout(700)
            return {"status": "ok", "detail": "search submitted"}
        if action == "click_button":
            await page.locator("button, [role='button']").first.click(timeout=2000)
            await page.wait_for_timeout(600)
            return {"status": "ok", "detail": "button clicked"}
        if action == "navigate_link":
            await page.locator("a[href]").first.click(timeout=2000)
            await page.wait_for_load_state("domcontentloaded")
            return {"status": "ok", "detail": "navigated"}

        await page.mouse.wheel(0, 2000)
        return {"status": "ok", "detail": "scrolled"}
