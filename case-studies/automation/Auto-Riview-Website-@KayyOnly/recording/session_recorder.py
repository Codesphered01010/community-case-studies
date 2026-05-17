class SessionRecorder:
    def __init__(self) -> None:
        self.timeline: list[dict] = []

    def record(self, step: str, detail: dict) -> None:
        self.timeline.append({"step": step, "detail": detail})
