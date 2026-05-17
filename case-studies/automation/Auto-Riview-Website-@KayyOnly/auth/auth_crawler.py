from __future__ import annotations

from typing import Any


class AuthCrawler:
    PRIORITY_KEYWORDS = ["dashboard", "profile", "settings", "admin", "billing", "checkout", "orders"]

    def prioritize(self, pages: list[str]) -> list[str]:
        prioritized = sorted(
            pages,
            key=lambda p: (0 if any(k in p.lower() for k in self.PRIORITY_KEYWORDS) else 1, p),
        )
        return prioritized

    def summarize(self, pages: list[str]) -> dict[str, Any]:
        protected = [p for p in pages if any(k in p.lower() for k in self.PRIORITY_KEYWORDS)]
        return {"protected_routes": protected[:20], "protected_route_count": len(protected)}
