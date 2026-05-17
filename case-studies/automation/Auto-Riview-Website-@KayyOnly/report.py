from datetime import datetime
from pathlib import Path
from typing import Any

from utils import save_json


def build_report(
    pages: list[dict[str, Any]],
    interactions: list[dict[str, Any]] | None = None,
    crawl_result: dict[str, Any] | None = None,
    agent_session: dict[str, Any] | None = None,
    responsive_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    interactions = interactions or []
    crawl_result = crawl_result or {}
    agent_session = agent_session or {}
    responsive_result = responsive_result or {}
    total_console_errors = sum(len(p["console_errors"]) for p in pages)
    total_failed_requests = sum(len(p["failed_requests"]) for p in pages)
    total_broken_images = sum(len(p["broken_images"]) for p in pages)
    total_accessibility_issues = sum(len(p["accessibility_issues"]) for p in pages)
    avg_load_time_ms = round(sum(p["load_time_ms"] for p in pages) / max(len(pages), 1), 2)

    interaction_summary = {
        "pages_tested": len(interactions),
        "buttons_total": sum(i.get("buttons_total", 0) for i in interactions),
        "buttons_clicked": sum(i.get("buttons_clicked", 0) for i in interactions),
        "buttons_failed": sum(i.get("buttons_failed", 0) for i in interactions),
        "forms_tested": sum(i.get("forms_tested", 0) for i in interactions),
        "validation_issues": sum(i.get("validation_issues", 0) for i in interactions),
        "broken_forms": sum(i.get("broken_forms", 0) for i in interactions),
        "broken_links": sum(i.get("broken_links", 0) for i in interactions),
        "dead_routes": sum(i.get("dead_routes", 0) for i in interactions),
        "redirect_issues": sum(i.get("redirect_issues", 0) for i in interactions),
        "modal_issues": sum(i.get("modal_issues", 0) for i in interactions),
        "dropdown_issues": sum(i.get("dropdown_issues", 0) for i in interactions),
        "interaction_timeouts": sum(i.get("interaction_timeouts", 0) for i in interactions),
    }

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": {
            "pages_crawled": len(pages),
            "avg_load_time_ms": avg_load_time_ms,
            "total_console_errors": total_console_errors,
            "total_failed_requests": total_failed_requests,
            "total_broken_images": total_broken_images,
            "total_accessibility_issues": total_accessibility_issues,
        },
        "smart_crawler": crawl_result,
        "interaction_testing": {"summary": interaction_summary, "details": interactions},
        "ai_agent_session": agent_session,
        "responsive_testing": responsive_result,
        "pages": pages,
    }

def write_reports(base_name: str, payload: dict[str, Any], ai_result: dict[str, Any]) -> tuple[str, str]:
    Path("reports").mkdir(exist_ok=True)
    json_path = f"reports/{base_name}.json"
    txt_path = f"reports/{base_name}.txt"

    payload["ai_analysis"] = ai_result
    save_json(json_path, payload)

    summary = payload["summary"]
    interaction = payload.get("interaction_testing", {}).get("summary", {})
    crawler = payload.get("smart_crawler", {})
    structure = crawler.get("structure", {})
    issues = crawler.get("issues", {})
    agent = payload.get("ai_agent_session", {})
    responsive = payload.get("responsive_testing", {})
    ai_debug = payload.get("ai_analysis", {}).get("summary_debug", {})
    devices = responsive.get("devices", {})
    auth = payload.get("authenticated_testing", {})
    video_recording = payload.get("video_recording", {})
    lines = [
        "AI WEBSITE REVIEW BOT REPORT",
        "=" * 40,
        f"Generated: {payload['generated_at']}",
        f"Pages Crawled: {summary['pages_crawled']}",
        f"Avg Load Time: {summary['avg_load_time_ms']} ms",
        f"Console Errors: {summary['total_console_errors']}",
        "",
        "🧠 AI SUMMARY",
        "-" * 40,
        f"Payload size: {ai_debug.get('payload_size', 0)} chars",
        f"Console errors summarized: {ai_debug.get('console_errors_summarized', '0/0')}",
        f"Failed requests summarized: {ai_debug.get('failed_requests_summarized', '0/0')}",
        "",
        "🕷️ SMART CRAWLER",
        "-" * 40,
        f"Total halaman: {len(crawler.get('pages', []))}",
        f"Total route: {structure.get('total_routes', 0)}",
        f"Total internal link: {structure.get('total_internal_links', 0)}",
        f"Total external link: {structure.get('total_external_links', 0)}",
        f"Important pages detected: {len(crawler.get('important_pages', {}))}",
        f"Broken route: {len(issues.get('broken_routes', []))} | Dead link: {len(issues.get('dead_links', []))} | Duplicate: {len(issues.get('duplicate_pages', []))}",
        "",
        "🤖 AI AGENT SESSION",
        "-" * 40,
        f"Actions performed: {len(agent.get('actions_performed', []))}",
        f"Decisions logged: {len(agent.get('ai_decisions', []))}",
        f"Autonomous findings: {len(agent.get('autonomous_findings', []))}",
        "",
        "📱 RESPONSIVE TESTING",
        "-" * 40,
        f"Desktop checks: {len(devices.get('desktop', []))}",
        f"Tablet checks: {len(devices.get('tablet', []))}",
        f"Mobile checks: {len(devices.get('mobile', []))}",
        f"Session videos: {len([v for v in responsive.get('video_paths', []) if v])}",
        "",
        "Device findings:",
        "",
        "🔐 AUTHENTICATED TESTING",
        "-" * 40,
        f"Login status: {auth.get('status', 'skipped')}",
        f"Cookie/session: {auth.get('session', {}).get('cookies', 0)} cookies",
        f"Auth token detected: {auth.get('auth_token_exists', False)}",
        f"Protected routes found: {auth.get('protected_routes', {}).get('protected_route_count', 0)}",
        "",
        "🎥 VIDEO RECORDING",
        "-" * 40,
        f"Total videos: {video_recording.get('total_videos', 0)}",
        "",
        "🧪 INTERACTION TESTING",
        "-" * 40,
        f"Buttons total/clicked/failed: {interaction.get('buttons_total',0)}/{interaction.get('buttons_clicked',0)}/{interaction.get('buttons_failed',0)}",
    ]


    for group in ["desktop", "tablet", "mobile"]:
        for item in devices.get(group, []):
            status_icon = "✅" if item.get("status") == "ok" else "⚠️"
            issue_map = item.get("issue_map", {})
            top_issue = next((k for k, v in issue_map.items() if v), "layout_normal")
            lines.append(f"{status_icon} {item.get('device')} | {item.get('url')} | {top_issue}")
    

    for api in auth.get("authenticated_api", [])[:15]:
        lines.append(f"API {api.get('url')} -> {api.get('status')}")

    for shot in auth.get("screenshots", []):
        lines.append(f"- {shot}")
    if auth.get("dashboard_screenshot"):
        lines.append(f"- {auth.get('dashboard_screenshot')}")
    if auth.get("protected_route_screenshot"):
        lines.append(f"- {auth.get('protected_route_screenshot')}")

    for video in video_recording.get("files", []):
        lines.append(f"- {video}")

    lines.append("Auth logs:")
    for entry in auth.get("auth_logs", [])[:20]:
        lines.append(f"- {entry.get('time')} | {entry.get('event')} | {entry.get('detail')}")

    Path(txt_path).write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path
