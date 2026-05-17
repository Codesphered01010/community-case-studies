from __future__ import annotations

from dataclasses import dataclass


KEYWORDS = {
    "login": 10,
    "signin": 10,
    "register": 9,
    "signup": 9,
    "dashboard": 9,
    "admin": 10,
    "checkout": 10,
    "cart": 9,
    "profile": 7,
    "settings": 7,
    "search": 8,
    "contact": 6,
    "product": 8,
    "blog": 6,
}


@dataclass
class PrioritySignal:
    url: str
    text: str = ""


class PriorityEngine:
    def score(self, signal: PrioritySignal) -> int:
        haystack = f"{signal.url} {signal.text}".lower()
        return sum(v for k, v in KEYWORDS.items() if k in haystack)

    def classify(self, signal: PrioritySignal) -> list[str]:
        haystack = f"{signal.url} {signal.text}".lower()
        return [k for k in KEYWORDS if k in haystack]
