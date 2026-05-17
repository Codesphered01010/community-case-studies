from dataclasses import dataclass


@dataclass
class AgentState:
    action_count: int = 0
    depth: int = 0


class StateManager:
    def __init__(self, max_actions: int = 25, max_depth: int = 3):
        self.max_actions = max_actions
        self.max_depth = max_depth
        self.state = AgentState()

    def allow_action(self) -> bool:
        return self.state.action_count < self.max_actions and self.state.depth <= self.max_depth

    def bump(self, depth: int = 0) -> None:
        self.state.action_count += 1
        self.state.depth = max(self.state.depth, depth)
