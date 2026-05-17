from __future__ import annotations

import json
from collections import Counter
from typing import Any


class SummaryBuilder:
    MAX_CONSOLE_ERRORS = 5
    MAX_FAILED_REQUESTS = 5
    MAX_RESPONSIVE_ISSUES = 5
    MAX_ACCESSIBILITY_ISSUES = 10
    MAX_CRAWLED_PAGES = 15
    MAX_INTERACTION_LOGS = 10
    MAX_SCREENSHOTS = 8

    def __init__(self, max_payload_chars: int = 20000) -> None:
        self.max_payload_chars = max_payload_chars

    def build_summary(self, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        pages = payload.get("pages", [])[:self.MAX_CRAWLED_PAGES]
        summary = payload.get("summary", {})
        responsive = payload.get("responsive_testing", {}).get("devices", {})

        console_errors = [e.get("text", "") for p in pages for e in p.get("console_errors", [])]
        failed_requests = [self._request_key(r) for p in pages for r in p.get("failed_requests", [])]
        a11y = [self._a11y_key(i) for p in pages for i in p.get("accessibility_issues", [])]    

        grouped_console = self._group_issues(console_errors)[: self.MAX_CONSOLE_ERRORS]
        grouped_failed = self._group_issues(failed_requests)[: self.MAX_FAILED_REQUESTS]
        grouped_a11y = self._group_issues(a11y)[: self.MAX_ACCESSIBILITY_ISSUES]
        responsive_issues = self._summarize_responsive(responsive or [])[:self.MAX_RESPONSIVE_ISSUES]

        interactions = self._summarize_interactions(payload)[: self.MAX_INTERACTION_LOGS]
        important_pages = self._important_pages(payload)[: self.MAX_CRAWLED_PAGES]
        screenshots = self._collect_screenshots(payload)[: self.MAX_SCREENSHOTS]

        avg_fcp = round(sum((p.get("fcp_ms") or 0) for p in pages) / max(len(pages), 1), 2)
        top_perf_issue = self._top_perf_issue(summary, grouped_failed, grouped_console)

        compact = {
            "url": pages[0].get("url", "") if pages else "",
            "title": "AI Website Review Summary",
            "performance": {
               "avg_load_time_ms": summary.get("avg_load_time_ms", 0),
                "avg_fcp_ms": avg_fcp,
                "top_performance_issue": top_perf_issue,
                "api_latency_summary": grouped_failed[0]["issue"] if grouped_failed else "none",
                "render_issue_summary": grouped_console[0]["issue"] if grouped_console else "none",
            },
            "error_summary": {
                "total_console_errors": summary.get("total_console_errors", len(console_errors)),
                "total_failed_requests": summary.get("total_failed_requests", len(failed_requests)),
                "total_accessibility_issues": summary.get("total_accessibility_issues", len(a11y)),
            },
            "top_console_errors": grouped_console,
            "top_failed_requests": grouped_failed,
            "responsive_issues": responsive_issues,
            "accessibility_issues": grouped_a11y,
            "important_pages": important_pages,
            "interaction_logs": interactions,
            "screenshots": screenshots,
            "priority_signals": self._priority_signals(grouped_console, grouped_failed, responsive_issues, grouped_a11y),
        }

        trimmed, trim_info = self._enforce_payload_limit(compact)
        payload_chars = len(json.dumps(trimmed, ensure_ascii=False))
        print(f"Payload chars: {payload_chars}")
        debug = {
            "payload_size": payload_chars,
            "console_errors_summarized": f"{len(trimmed.get('top_console_errors', []))}/{len(console_errors)}",
            "failed_requests_summarized": f"{len(trimmed.get('top_failed_requests', []))}/{len(failed_requests)}",
            **trim_info,
        }
        return trimmed, debug

    def _group_issues(self, values: list[str]) -> list[dict[str, Any]]:
        cleaned = [self._normalize(v) for v in values if self._is_relevant(v)]
        counts = Counter(cleaned)
        return [{"issue": key, "count": count} for key, count in counts.most_common() if key]

    def _is_relevant(self, text: str) -> bool:
        t = (text or "").lower()
        if not t.strip():
            return False
        noise_patterns = [
            "extension://", "chrome-extension", "moz-extension", "safari-extension", "favicon",
            "google-analytics", "gtm.js", "doubleclick", "facebook pixel", "tracking", "hotjar", "clarity",
        ]
        return not any(p in t for p in noise_patterns)

    def _normalize(self, text: str) -> str:
        t = (text or "").strip()
        low = t.lower()
        if "hydration" in low:
            return "Hydration mismatch"
        if "401" in low or "unauthorized" in low:
            return "Auth issue (Unauthorized)"
        if "403" in low or "forbidden" in low:
            return "Auth issue (Forbidden)"
        if "timeout" in low:
            return "Network timeout"
        return t[:120]

    def _request_key(self, request: Any) -> str:
        if isinstance(request, dict):
            url = request.get("url", "")
            status = request.get("status", "")
            method = request.get("method", "")
            return f"{method} {status} {url}".strip()
        return str(request or "")

    def _a11y_key(self, issue: Any) -> str:
        if isinstance(issue, dict):
            return str(issue.get("type") or issue.get("message") or "unknown")
        return str(issue or "unknown")

    def _summarize_interactions(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        details = payload.get("interaction_testing", {}).get("details", [])
        seen: set[str] = set()
        result: list[dict[str, Any]] = []
        for item in details:
            if not isinstance(item, dict):
                continue
            key = json.dumps({k: item.get(k) for k in ("type", "target", "status", "message")}, sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            result.append({k: item.get(k) for k in ("type", "target", "status", "message") if item.get(k)})
        return result

    def _summarize_responsive(self, devices: dict[str, Any]) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        for group in ["desktop", "tablet", "mobile"]:
            for item in devices.get(group, []):
                issue_map = item.get("issue_map", {})
                first_issue = next((k for k, v in issue_map.items() if v), "")
                if first_issue:
                    issues.append({"device": item.get("device"), "issue": first_issue})

        unique = []
        seen = set()
        for issue in issues:
            key = (issue.get("device"), issue.get("issue"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(issue)
        return unique

    def _important_pages(self, payload: dict[str, Any]) -> list[str]:
        pages = payload.get("smart_crawler", {}).get("important_pages", {})
        if isinstance(pages, dict):
            return list(dict.fromkeys(pages.keys()))
        if isinstance(pages, list):
            return list(dict.fromkeys(pages))
        return []

    def _collect_screenshots(self, payload: dict[str, Any]) -> list[str]:
        shots = []
        for p in payload.get("pages", []):
            if p.get("console_errors") or p.get("failed_requests"):
                if p.get("screenshot_path"):
                    shots.append(p["screenshot_path"])

        auth = payload.get("authenticated_testing", {})
        for extra in [auth.get("dashboard_screenshot"), auth.get("protected_route_screenshot")]:
            if extra:
                shots.append(extra)
        
        return [s for s in dict.fromkeys(shots) if s]

    def _top_perf_issue(self, summary: dict[str, Any], failed: list[dict[str, Any]], console: list[dict[str, Any]]) -> str:
        if summary.get("avg_load_time_ms", 0) > 5000:
            return "performance bottleneck"
        if failed:
            return "failed request"
        if any("Hydration mismatch" == i.get("issue") for i in console):
            return "hydration mismatch"
        return "stable"

    def _priority_signals(self, console: list[dict[str, Any]], failed: list[dict[str, Any]], responsive: list[dict[str, Any]], a11y: list[dict[str, Any]]) -> list[str]:
        signals: list[str] = []
        if failed:
            signals.append("failed request")
        if any("auth issue" in (item.get("issue", "").lower()) for item in failed + console):
            signals.append("auth issue")
        if any(item.get("issue") == "Hydration mismatch" for item in console):
            signals.append("hydration mismatch")
        if responsive:
            signals.append("responsive break")
        if a11y:
            signals.append("accessibility critical")
        return signals[:6]

    def _enforce_payload_limit(self, summary: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        trimmed = dict(summary)
        dropped: list[str] = []
        order = ["interaction_logs", "screenshots", "accessibility_issues", "responsive_issues", "top_console_errors", "top_failed_requests", "important_pages"]
        minimums = {
            "interaction_logs": 2,
            "screenshots": 2,
            "accessibility_issues": 3,
            "responsive_issues": 2,
            "top_console_errors": 2,
            "top_failed_requests": 2,
            "important_pages": 5,
        }
        while len(json.dumps(trimmed, ensure_ascii=False)) > self.max_payload_chars:
            changed = False
            for field in order:
                if isinstance(trimmed.get(field), list) and len(trimmed[field]) > minimums[field]:
                    trimmed[field] = trimmed[field][:-1]
                    dropped.append(field)
                    changed = True
                    break
            if not changed:
                break
        return trimmed, {"trimmed": bool(dropped), "trimmed_fields": list(dict.fromkeys(dropped))}
