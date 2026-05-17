from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class InteractionEvent:
    action: str
    selector: str
    status: str
    message: str = ""
    before_screenshot: str = ""
    after_screenshot: str = ""
    error_screenshot: str = ""
    url_before: str = ""
    url_after: str = ""
    dom_changed: bool = False
    console_errors_new: int = 0
    failed_requests_new: int = 0


@dataclass
class InteractionReport:
    page_url: str
    buttons_total: int = 0
    buttons_clicked: int = 0
    buttons_failed: int = 0
    forms_tested: int = 0
    validation_issues: int = 0
    broken_forms: int = 0
    broken_links: int = 0
    dead_routes: int = 0
    redirect_issues: int = 0
    modal_issues: int = 0
    dropdown_issues: int = 0
    interaction_timeouts: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)

    def add(self, event: InteractionEvent) -> None:
        self.events.append(asdict(event))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
