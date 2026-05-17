from pathlib import Path


class VideoRecorder:
    FLOW_FILES = [
        "videos/desktop-main-flow.webm",
        "videos/mobile-main-flow.webm",
        "videos/tablet-main-flow.webm",
        "videos/auth-flow.webm",
        "videos/error-flow.webm",
    ]

    @staticmethod
    def cleanup_flow_videos() -> None:
        for file_path in VideoRecorder.FLOW_FILES:
            path = Path(file_path)
            if path.exists():
                path.unlink()

    @staticmethod
    async def finalize_page_video(page) -> str:
        await page.close()
        video = page.video
        if not video:
            return ""
        src = await video.path()
        return str(Path(src))
    
    @staticmethod
    async def finalize_named_video(page, output_path: str) -> str:
        video_path = await VideoRecorder.finalize_page_video(page)
        if not video_path:
            return ""
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        Path(video_path).replace(target)
        return str(target)
