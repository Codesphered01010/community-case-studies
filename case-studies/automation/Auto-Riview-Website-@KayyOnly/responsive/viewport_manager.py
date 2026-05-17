from playwright.async_api import Playwright


class ViewportManager:
    def context_options(self, profile: dict, playwright: Playwright, video_dir: str) -> dict:
        options = {"ignore_https_errors": True, "record_video_dir": video_dir}
        if profile.get("playwright_device"):
            options.update(playwright.devices[profile["playwright_device"]])
        else:
            options["viewport"] = profile["viewport"]
        return options
