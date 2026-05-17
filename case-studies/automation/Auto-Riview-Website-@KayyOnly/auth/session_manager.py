from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SessionManager:
    def __init__(self, storage_path: str = "sessions/auth_state.json") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    async def save(self, context) -> str:
        await context.storage_state(path=str(self.storage_path))
        return str(self.storage_path)

    def load(self) -> dict[str, Any] | None:
        if not self.storage_path.exists():
            return None
        return {"storage_state": str(self.storage_path)}

    def inspect_state(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {"cookies": 0, "origins": 0}
        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return {"cookies": len(raw.get("cookies", [])), "origins": len(raw.get("origins", []))}
