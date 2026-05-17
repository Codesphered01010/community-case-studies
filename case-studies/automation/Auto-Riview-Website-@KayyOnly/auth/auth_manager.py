from __future__ import annotations

from pathlib import Path
from typing import Any

from auth.auth_logger import AuthLogger
from auth.login_detector import LoginDetector


class AuthManager:
    def __init__(self, config: dict[str, Any], logger: AuthLogger | None = None) -> None:
        self.config = config
        self.detector = LoginDetector()
        self.logger = logger or AuthLogger()

    async def login(self, context, base_url: str) -> dict[str, Any]:
        if not self.config.get("enabled"):
            return {"enabled": False, "status": "skipped", "auth_logs": self.logger.events}

        page = await context.new_page()
        Path("screenshots/auth").mkdir(parents=True, exist_ok=True)
        login_url = self.config.get("login_url") or base_url
        self.logger.log("open_login_page", {"url": login_url})
        await page.goto(login_url, wait_until="domcontentloaded", timeout=45000)
        await self.detector.wait_for_spa_hydration(page)
        await page.screenshot(path="screenshots/auth/login-page.png", full_page=True)
        await page.screenshot(path="screenshots/auth/before-login.png", full_page=True)

        username_selector = self.config.get("username_selector", "input[type='email'], input[name*=user i], input[name*=email i]")
        password_selector = self.config.get("password_selector", "input[type='password']")
        submit_selector = self.config.get("submit_selector", "button[type='submit'], button:has-text('Login'), button:has-text('Sign in')")

        await page.locator(username_selector).first.fill(self.config.get("username", ""))
        await page.locator(password_selector).first.fill(self.config.get("password", ""))
        await page.screenshot(path="screenshots/auth/auth-form-filled.png", full_page=True)
        self.logger.log("credential_filled", {"username_selector": username_selector, "password_selector": password_selector})

        await page.locator(submit_selector).first.click(timeout=10000)
        self.logger.log("submit_clicked", {"submit_selector": submit_selector})
        await self.detector.wait_for_spa_hydration(page)

        detection = await self.detector.detect(page)
        self.logger.log("login_detection", detection)
        if detection["login_detection"]["after_interaction_scan"].get("has_auth_modal"):
            await page.screenshot(path="screenshots/auth/auth-modal.png", full_page=True)
        if detection["login_success"]:
            await page.screenshot(path="screenshots/auth/login-success.png", full_page=True)
        else:
            await page.screenshot(path="screenshots/auth/auth-error.png", full_page=True)

        await page.close()
        return {
            "enabled": True,
            "status": "success" if detection["login_success"] else "failed",
            "auth_logs": self.logger.events,
            "screenshots": [
                "screenshots/auth/login-page.png",
                "screenshots/auth/before-login.png",
                "screenshots/auth/auth-form-filled.png",
                "screenshots/auth/auth-modal.png" if detection["login_detection"]["after_interaction_scan"].get("has_auth_modal") else "",
                "screenshots/auth/login-success.png" if detection["login_success"] else "screenshots/auth/auth-error.png",
            ],
            **detection,
        }
