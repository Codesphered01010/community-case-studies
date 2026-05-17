from __future__ import annotations

from pathlib import Path

from playwright.async_api import BrowserContext

from ai_agent.action_executor import ActionExecutor
from ai_agent.decision_engine import DecisionEngine
from ai_agent.memory import AgentMemory
from ai_agent.reasoning_logger import ReasoningLogger
from ai_agent.state_manager import StateManager
from utils import slugify_url


class AutonomousTestingAgent:
    def __init__(self, max_actions: int = 20):
        self.decision_engine = DecisionEngine()
        self.action_executor = ActionExecutor()
        self.memory = AgentMemory()
        self.logger = ReasoningLogger()
        self.state = StateManager(max_actions=max_actions)

    async def run(self, context: BrowserContext, url: str) -> dict:
        Path("screenshots/agent").mkdir(parents=True, exist_ok=True)
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=40000)

        step = 0
        while self.state.allow_action():
            step += 1
            decision = await self.decision_engine.decide(page)
            fingerprint = f"{page.url}:{decision['action']}"
            if fingerprint in self.memory.action_fingerprints:
                self.logger.log("Aksi berulang terdeteksi", decision["action"], "skipped")
                break
            self.memory.action_fingerprints.add(fingerprint)

            try:
                outcome = await self.action_executor.execute(page, decision)
                self.logger.log(decision["reason"], decision["action"], outcome["status"])
            except Exception as exc:
                self.logger.log(decision["reason"], decision["action"], f"failed: {exc}")

            shot = f"screenshots/agent/{slugify_url(page.url)}_step_{step}.png"
            await page.screenshot(path=shot, full_page=True)
            self.memory.remember({"step": step, "url": page.url, "decision": decision, "screenshot": shot})
            self.state.bump(depth=1)

        await page.close()
        return {
            "actions_performed": self.memory.timeline,
            "ai_decisions": self.logger.decisions,
            "autonomous_findings": [d for d in self.logger.decisions if "failed" in d["result"]],
        }
