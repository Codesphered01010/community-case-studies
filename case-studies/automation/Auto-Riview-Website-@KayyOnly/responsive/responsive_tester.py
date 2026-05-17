from __future__ import annotations

from pathlib import Path

from playwright.async_api import Playwright

from recording.replay_manager import ReplayManager
from recording.session_recorder import SessionRecorder
from recording.video_recorder import VideoRecorder
from responsive.device_profiles import DEVICE_PROFILES
from responsive.responsive_analyzer import ResponsiveAnalyzer
from responsive.viewport_manager import ViewportManager
from utils import slugify_url


class ResponsiveTester:
    def __init__(self) -> None:
        self.viewport_manager = ViewportManager()
        self.analyzer = ResponsiveAnalyzer()
        self.session = SessionRecorder()
        self.replay = ReplayManager()

    async def test_pages(
        self,
        playwright: Playwright,
        browser,
        pages: list[str],
        include_groups: list[str] | None = None,
        max_pages: int = 10,
        record_video: bool = True,
    ) -> dict:
        Path("screenshots/responsive").mkdir(parents=True, exist_ok=True)
        Path("screenshots/desktop").mkdir(parents=True, exist_ok=True)
        Path("screenshots/tablet").mkdir(parents=True, exist_ok=True)
        Path("screenshots/mobile").mkdir(parents=True, exist_ok=True)
        results: dict = {"desktop": [], "tablet": [], "mobile": []}
        video_paths: list[str] = []

        groups = set(include_groups or ["desktop", "tablet", "mobile"])

        for profile in DEVICE_PROFILES:
            if profile["group"] not in groups:
                continue
            group = profile["group"]
            video_dir = f"videos/{group}"
            Path(video_dir).mkdir(parents=True, exist_ok=True)
            context = await browser.new_context(**self.viewport_manager.context_options(profile, playwright, video_dir))

            for url in pages[:max_pages]:
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(800)
                analysis = await self.analyzer.analyze(page)
                shot = f"screenshots/{group}/{slugify_url(url)}_{slugify_url(profile['name'])}.png"
                await page.screenshot(path=shot, full_page=True)
                self.session.record("responsive_page_test", {"device": profile["name"], "url": url, "status": analysis["status"]})
                if analysis["total_issues"] > 0:
                    bug_shot = f"screenshots/responsive/bug_{slugify_url(url)}_{slugify_url(profile['name'])}.png"
                    await page.screenshot(path=bug_shot, full_page=True)
                    analysis["bug_screenshot"] = bug_shot

                results[group].append({"device": profile["name"], "url": url, "screenshot": shot, **analysis})
                if record_video:
                    video_paths.append(await VideoRecorder.finalize_page_video(page))

            await context.close()

        return {
            "devices": results,
            "session_recording": self.replay.build_replay_info(self.session.timeline, video_paths),
            "video_paths": video_paths,
        }