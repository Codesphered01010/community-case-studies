from __future__ import annotations

from copy import deepcopy
from typing import Any

MODE_CONFIG: dict[str, dict[str, Any]] = {
    "quick": {
        "label": "⚡ Quick Mode",
        "max_pages": 3,
        "devices": ["desktop"],
        "performance": True,
        "interaction": True,
        "interaction_max_pages": 1,
        "responsive": False,
        "responsive_max_pages": 1,
        "accessibility": True,
        "screenshots": True,
        "video": False,
        "auth": False,
        "ai_agent": False,
        "ai_analysis": True,
        "auth_override_allowed": False,
    },
    "standard": {
        "label": "🛠️ Standard Mode",
        "max_pages": 10,
        "devices": ["desktop", "mobile"],
        "performance": True,
        "interaction": True,
        "interaction_max_pages": 5,
        "responsive": True,
        "responsive_max_pages": 5,
        "accessibility": True,
        "screenshots": True,
        "video": False,
        "auth": False,
        "ai_agent": False,
        "ai_analysis": True,
        "auth_override_allowed": True,
    },
    "deep": {
        "label": "🚀 Deep Mode",
        "max_pages": 30,
        "devices": ["desktop", "tablet", "mobile"],
        "performance": True,
        "interaction": True,
        "interaction_max_pages": 20,
        "responsive": True,
        "responsive_max_pages": 10,
        "accessibility": True,
        "screenshots": True,
        "video": True,
        "auth": True,
        "ai_agent": True,
        "ai_analysis": True,
        "auth_override_allowed": True,
    },
}


def get_mode_config(mode_name: str) -> dict[str, Any]:
    key = (mode_name or "standard").lower()
    if key not in MODE_CONFIG:
        key = "standard"
    config = deepcopy(MODE_CONFIG[key])
    config["name"] = key
    return config
