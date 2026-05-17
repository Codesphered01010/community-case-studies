from __future__ import annotations

from datetime import datetime


class AuthLogger:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def log(self, event: str, detail: dict | None = None) -> None:
        self.events.append({"time": datetime.utcnow().isoformat() + "Z", "event": event, "detail": detail or {}})
