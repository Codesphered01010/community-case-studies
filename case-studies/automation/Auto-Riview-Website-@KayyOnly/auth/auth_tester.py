from __future__ import annotations

from pathlib import Path

from recording.video_recorder import VideoRecorder


class AuthTester:
    async def test_dashboard(self, context, urls: list[str], video_output: str = "") -> dict:
        Path("screenshots/auth").mkdir(parents=True, exist_ok=True)
        api_calls: list[dict] = []
        route_results: list[dict] = []

        page = await context.new_page()
        page.on("response", lambda r: api_calls.append({"url": r.url, "status": r.status}) if "/api/" in r.url else None)

        protected_target = None
        for url in urls[:8]:
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(700)
                ok = bool(resp and resp.status < 400)
                route_results.append({"url": url, "status": resp.status if resp else None, "ok": ok})
                if protected_target is None and any(k in url.lower() for k in ["dashboard", "profile", "settings", "admin", "billing", "orders", "checkout"]):
                    protected_target = url
            except Exception as exc:
                route_results.append({"url": url, "ok": False, "error": str(exc)})

        if protected_target:
            await page.goto(protected_target, wait_until="domcontentloaded", timeout=30000)
            await page.screenshot(path="screenshots/auth/protected-route.png", full_page=True)

        await page.screenshot(path="screenshots/auth/dashboard.png", full_page=True)
        auth_video = ""
        if video_output:
            auth_video = await VideoRecorder.finalize_named_video(page, video_output)
        else:
            await page.close()
        return {
            "protected_route_results": route_results,
            "authenticated_api": api_calls[:60],
            "dashboard_screenshot": "screenshots/auth/dashboard.png",
            "protected_route_screenshot": "screenshots/auth/protected-route.png" if protected_target else "",
            "auth_video": auth_video,
        }
