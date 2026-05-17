from playwright.async_api import Page

from interaction.interaction_logger import InteractionEvent, InteractionReport


class FormTester:
    async def test_forms(self, page: Page, report: InteractionReport) -> None:
        forms = page.locator("form")
        count = min(await forms.count(), 5)
        report.forms_tested = count

        for i in range(count):
            form = forms.nth(i)
            try:
                email = form.locator("input[type='email']")
                if await email.count() > 0:
                    await email.first.fill("invalid-email")

                number = form.locator("input[type='number']")
                if await number.count() > 0:
                    await number.first.fill("abc")

                text_input = form.locator("input[type='text'], input:not([type])")
                if await text_input.count() > 0:
                    await text_input.first.fill("")

                submit = form.locator("button[type='submit'], input[type='submit'], button")
                if await submit.count() > 0:
                    await submit.first.click(timeout=3000)

                validation_text = await page.locator(":is(.error,[role='alert'],.invalid-feedback,:invalid)").count()
                if validation_text > 0:
                    report.validation_issues += 1

                report.add(InteractionEvent(action="form_submit", selector=f"form[{i}]", status="ok", message="Form tested"))
            except Exception as exc:
                report.broken_forms += 1
                report.add(InteractionEvent(action="form_submit", selector=f"form[{i}]", status="failed", message=str(exc)))
