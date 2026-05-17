from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentMemory:
    visited_urls: set[str] = field(default_factory=set)
    action_fingerprints: set[str] = field(default_factory=set)
    timeline: list[dict[str, Any]] = field(default_factory=list)  # ← tambah ini

    def remember_action(self, fingerprint: str) -> bool:
        if fingerprint in self.action_fingerprints:
            return False
        self.action_fingerprints.add(fingerprint)
        return True

    def remember(self, data: dict) -> None:  # ← tambah ini
        if "url" in data:
            self.visited_urls.add(data["url"])
        self.timeline.append(data)