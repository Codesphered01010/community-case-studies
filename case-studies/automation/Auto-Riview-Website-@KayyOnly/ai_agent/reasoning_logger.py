from dataclasses import dataclass, field


@dataclass
class ReasoningLogger:
    decisions: list[dict] = field(default_factory=list)

    def log(self, reason: str, action: str, result: str) -> None:
        self.decisions.append({"reason": reason, "action": action, "result": result})