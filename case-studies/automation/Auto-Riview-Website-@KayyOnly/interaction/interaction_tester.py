from pathlib import Path

from playwright.async_api import BrowserContext

from interaction.element_detector import ElementDetector
from interaction.form_tester import FormTester
from interaction.interaction_logger import InteractionEvent, InteractionReport
from interaction.navigation_tester import NavigationTester
from utils import slugify_url


class InteractionTester:
    def __init__(self) -> None:
        self.detector = ElementDetector()
        self.form_tester = FormTester()
        self.navigation_tester = NavigationTester()

    async def test_page(self, context: BrowserContext, url: str) -> dict:
        Path("screenshots/interactions").mkdir(parents=True, exist_ok=True)
        page = await context.new_page()
        report = InteractionReport(page_url=url)
        console_errors: list[str] = []
        failed_requests: list[str] = []

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: failed_requests.append(req.url))

        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(800)

        elements = await self.detector.detect(page)
        report.buttons_total = len(elements.get("buttons", []))

        await page.screenshot(path=f"screenshots/interactions/{slugify_url(url)}_before.png", full_page=True)

        buttons = page.locator("button, [role='button'], input[type='button'], input[type='submit']")
        for i in range(min(await buttons.count(), 8)):
            btn = buttons.nth(i)
            before = page.url
            before_dom = await page.content()
            before_err = len(console_errors)
            before_failed = len(failed_requests)
            try:
                await btn.click(timeout=2500)
                await page.wait_for_timeout(600)
                report.buttons_clicked += 1
                after = page.url
                after_dom = await page.content()
                report.add(InteractionEvent(
                    action="click_button",
                    selector=f"button[{i}]",
                    status="ok",
                    url_before=before,
                    url_after=after,
                    dom_changed=(before_dom != after_dom),
                    console_errors_new=max(0, len(console_errors) - before_err),
                    failed_requests_new=max(0, len(failed_requests) - before_failed),
                ))
            except Exception as exc:
                report.buttons_failed += 1
                err_path = f"screenshots/interactions/{slugify_url(url)}_button_{i}_error.png"
                await page.screenshot(path=err_path, full_page=True)
                report.add(InteractionEvent(action="click_button", selector=f"button[{i}]", status="failed", message=str(exc), error_screenshot=err_path))

        # input / textarea / search
        try:
            search = page.locator("input[type='search'], input[name*='search' i], input[placeholder*='search' i]")
            if await search.count() > 0:
                await search.first.fill("test query")
                await search.first.press("Enter")
                await page.wait_for_timeout(700)
                report.add(InteractionEvent(action="search", selector="search_input", status="ok"))
        except Exception as exc:
            report.interaction_timeouts += 1
            report.add(InteractionEvent(action="search", selector="search_input", status="failed", message=str(exc)))

        # modal open/close basic
        try:
            openers = page.locator("[data-bs-toggle='modal'], [aria-haspopup='dialog'], button")
            if await openers.count() > 0:
                await openers.first.click(timeout=2000)
                await page.wait_for_timeout(500)
                close_btn = page.locator("[data-bs-dismiss='modal'], [aria-label='Close'], .modal .close, .modal button")
                if await close_btn.count() > 0:
                    await close_btn.first.click(timeout=2000)
                report.add(InteractionEvent(action="modal_open_close", selector="modal", status="ok"))
        except Exception as exc:
            report.modal_issues += 1
            report.add(InteractionEvent(action="modal_open_close", selector="modal", status="failed", message=str(exc)))

        await self.form_tester.test_forms(page, report)
        await self.navigation_tester.test_navigation(page, url, report)

        # infinite scroll basic
        try:
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(500)
            await page.mouse.wheel(0, 3000)
            report.add(InteractionEvent(action="infinite_scroll", selector="window", status="ok"))
        except Exception as exc:
            report.interaction_timeouts += 1
            report.add(InteractionEvent(action="infinite_scroll", selector="window", status="failed", message=str(exc)))

        await page.screenshot(path=f"screenshots/interactions/{slugify_url(url)}_after.png", full_page=True)
        await page.close()
        return report.to_dict()
