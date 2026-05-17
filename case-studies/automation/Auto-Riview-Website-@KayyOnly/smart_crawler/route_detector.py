from __future__ import annotations

import re
from urllib.parse import urlparse


DYNAMIC_HINTS = [
    re.compile(r"/\d+(?:/|$)"),
    re.compile(r"/[0-9a-f]{8,}(?:/|$)", re.I),
    re.compile(r"\[(?:\.\.\.)?[^\]]+\]"),
    re.compile(r"/:\w+"),
]


class RouteDetector:
    def normalize(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/") or "/"
        return f"{parsed.scheme}://{parsed.netloc}{path}"

    def pattern(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path or "/"
        path = re.sub(r"/\d+(?=/|$)", "/{id}", path)
        path = re.sub(r"/[0-9a-f]{8,}(?=/|$)", "/{hash}", path, flags=re.I)
        return f"{parsed.scheme}://{parsed.netloc}{path.rstrip('/') or '/'}"

    def is_dynamic(self, url: str) -> bool:
        parsed = urlparse(url)
        return any(p.search(parsed.path or "") for p in DYNAMIC_HINTS)
