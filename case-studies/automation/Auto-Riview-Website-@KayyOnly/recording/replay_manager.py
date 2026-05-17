class ReplayManager:
    def build_replay_info(self, timeline: list[dict], video_paths: list[str]) -> dict:
        return {
            "steps": len(timeline),
            "video_count": len([v for v in video_paths if v]),
            "timeline": timeline,
            "videos": video_paths,
        }
