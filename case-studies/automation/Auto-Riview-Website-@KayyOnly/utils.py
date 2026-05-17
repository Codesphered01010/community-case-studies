import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


def setup_logger() -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger("ai_website_review_bot")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def ensure_dirs() -> None:
    for folder in ["screenshots", "reports", "logs"]:
        Path(folder).mkdir(parents=True, exist_ok=True)


def slugify_url(url: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_").lower()[:80]


def save_json(path: str, data: dict[str, Any]) -> None:
    def make_serializable(obj, seen=None):
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return "[Circular Reference]"
        if isinstance(obj, dict):
            seen.add(obj_id)
            return {k: make_serializable(v, seen) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            seen.add(obj_id)
            return [make_serializable(i, seen) for i in obj]
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, "__dict__"):
            seen.add(obj_id)
            return make_serializable(obj.__dict__, seen)
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        return str(obj)

    clean_data = make_serializable(data)
    Path(path).write_text(
        json.dumps(clean_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    retries: int = 2,
    delay: float = 1.0,
    **kwargs: Any,
) -> T:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as exc:
            last_error = exc
            if attempt == retries:
                break
            await asyncio.sleep(delay)
    raise RuntimeError(f"Retry failed: {last_error}")
