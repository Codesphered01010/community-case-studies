from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LoginCandidate:
    score: int
    source: str
    details: str

class LoginDetector:
    SUCCESS_HINTS = ["logout", "sign out", "dashboard", "my account", "profile"]
    FAILURE_HINTS = ["invalid", "incorrect", "wrong password", "try again", "failed"]
    URL_PATTERNS = ["/login", "/signin", "/auth", "/account", "/masuk"]
    AUTH_KEYWORDS = ["login", "sign in", "masuk", "account", "authenticate", "password", "email"]
    BUTTON_TEXTS = ["login", "sign in", "masuk", "continue", "account", "my account", "authenticate"]

    async def wait_for_spa_hydration(self, page) -> None:
        await page.wait_for_load_state("domcontentloaded", timeout=20000)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=20000)
        except Exception:
            pass
        await page.wait_for_timeout(900)

    async def _modal_open_attempt(self, page) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        openers = page.locator(
            "button:has-text('Login'), a:has-text('Login'), button:has-text('Sign in'), a:has-text('Sign in'), "
            "button:has-text('Account'), a:has-text('Account'), button:has-text('Masuk'), a:has-text('Masuk'), "
            "button:has-text('My Account'), a:has-text('My Account')"
        )
        count = min(await openers.count(), 6)
        for idx in range(count):
            node = openers.nth(idx)
            try:
                if not await node.is_visible():
                    continue
                text = (await node.inner_text()).strip()
                await node.click(timeout=2500)
                await page.wait_for_timeout(800)
                actions.append({"action": "auth_opener_clicked", "text": text})
                break
            except Exception as exc:
                actions.append({"action": "auth_opener_click_failed", "error": str(exc)})

        menu_toggles = page.locator("button[aria-label*='menu' i], button:has-text('Menu'), [data-testid*='menu' i]")
        if await menu_toggles.count() > 0:
            try:
                await menu_toggles.first.click(timeout=2000)
                await page.wait_for_timeout(700)
                actions.append({"action": "mobile_menu_opened"})
            except Exception as exc:
                actions.append({"action": "mobile_menu_failed", "error": str(exc)})
        return actions

    async def _candidate_scan(self, page) -> dict[str, Any]:
        url = page.url.lower()
        body_text = (await page.inner_text("body")).lower()[:12000]

        candidates: list[LoginCandidate] = []
        if any(p in url for p in self.URL_PATTERNS):
            candidates.append(LoginCandidate(score=3, source="url", details=url))

        keyword_hits = [k for k in self.AUTH_KEYWORDS if k in body_text]
        if keyword_hits:
            candidates.append(LoginCandidate(score=min(len(keyword_hits), 4), source="keywords", details=", ".join(keyword_hits[:6])))

        button_count = await page.locator(
            "button:has-text('Login'), a:has-text('Login'), button:has-text('Sign in'), a:has-text('Sign in'), "
            "button:has-text('Masuk'), a:has-text('Masuk'), button:has-text('Continue'), a:has-text('Continue'), "
            "button:has-text('Account'), a:has-text('Account'), button:has-text('My Account'), a:has-text('My Account'), "
            "button:has-text('Authenticate'), a:has-text('Authenticate')"
        ).count()
        if button_count:
            candidates.append(LoginCandidate(score=min(button_count, 4), source="buttons", details=f"{button_count} auth-like buttons"))

        password_count = await page.locator("input[type='password']").count()
        user_count = await page.locator("input[type='email'], input[name*=user i], input[name*=email i], input[name*=login i]").count()
        submit_count = await page.locator("button[type='submit'], input[type='submit']").count()

        auth_form_candidate = password_count > 0 and user_count > 0 and submit_count > 0
        if auth_form_candidate:
            candidates.append(LoginCandidate(score=6, source="form", details=f"password={password_count},user={user_count},submit={submit_count}"))

        modal_count = await page.locator("[role='dialog'], .modal, [aria-modal='true'], [data-testid*='modal' i]").count()
        modal_auth = False
        if modal_count:
            modal_text = (await page.locator("[role='dialog'], .modal, [aria-modal='true'], [data-testid*='modal' i]").first.inner_text()).lower()
            modal_auth = any(t in modal_text for t in ["login", "sign in", "masuk", "password", "account"])
            if modal_auth:
                candidates.append(LoginCandidate(score=5, source="modal", details="auth keyword in modal"))

        score = sum(c.score for c in candidates)
        return {
            "score": score,
            "is_auth_candidate": score >= 6,
            "has_auth_form": auth_form_candidate,
            "has_auth_modal": modal_auth,
            "password_field_detected": password_count > 0,
            "button_candidate_count": button_count,
            "form_candidate": {
                "password_fields": password_count,
                "username_or_email_fields": user_count,
                "submit_buttons": submit_count,
            },
            "button_candidates": self.BUTTON_TEXTS,
            "candidate_sources": [c.__dict__ for c in candidates],
        }

    async def detect(self, page) -> dict:
        await self.wait_for_spa_hydration(page)
        first_scan = await self._candidate_scan(page)
        interactions = await self._modal_open_attempt(page)
        await self.wait_for_spa_hydration(page)
        second_scan = await self._candidate_scan(page)
        url = page.url.lower()
        body_text = (await page.inner_text("body")).lower()[:6000]
        cookies = await page.context.cookies()

        has_failure_text = any(h in body_text for h in self.FAILURE_HINTS)
        has_success_text = any(h in body_text for h in self.SUCCESS_HINTS)
        logout_button = await page.locator("button:has-text('Logout'), a:has-text('Logout'), button:has-text('Sign out'), a:has-text('Sign out')").count()
        redirect_after_login = "login" not in url and "signin" not in url
        token_detected = await page.evaluate(
            """() => {
                const keys = [...Object.keys(localStorage), ...Object.keys(sessionStorage)];
                return keys.some(k => /(token|auth|jwt|session)/i.test(k));
            }"""
        )

        login_success = (redirect_after_login or has_success_text) and not has_failure_text
        best_scan = second_scan if second_scan["score"] >= first_scan["score"] else first_scan
        return {
            "login_success": login_success,
            "login_failed": has_failure_text and not login_success,
            "invalid_credential_message": has_failure_text,
            "redirect_after_login": redirect_after_login,
            "dashboard_loaded": has_success_text,
            "logout_button_visible": logout_button > 0,
            "auth_token_exists": bool(token_detected),
            "cookie_session_created": len(cookies) > 0,
            "login_detection": {
                "initial_scan": first_scan,
                "after_interaction_scan": second_scan,
                "modal_interaction": interactions,
                "final_auth_candidate": best_scan["is_auth_candidate"],
            },
        }
