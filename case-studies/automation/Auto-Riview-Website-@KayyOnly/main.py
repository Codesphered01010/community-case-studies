import argparse
import asyncio
from datetime import datetime

from playwright.async_api import async_playwright
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.tree import Tree

from ai_agent.agent import AutonomousTestingAgent
from analyzer import AIAnalyzer
from auth.auth_crawler import AuthCrawler
from auth.auth_manager import AuthManager
from auth.auth_tester import AuthTester
from auth.session_manager import SessionManager
from checker import WebsiteChecker
from config.modes import get_mode_config
from interaction.interaction_tester import InteractionTester
from report import build_report, write_reports
from responsive.responsive_tester import ResponsiveTester
from smart_crawler.smart_crawler import SmartCrawlerConfig, SmartWebsiteCrawler
from utils import ensure_dirs, retry_async, setup_logger, slugify_url

EXIT_COMMANDS = {"exit", "quit", "q"}
MODE_MAP = {"1": "quick", "2": "standard", "3": "deep"}


async def run(url: str, mode_config: dict, auth_config: dict | None = None) -> tuple[str, str, dict]:
    ensure_dirs()
    logger = setup_logger()
    checker = WebsiteChecker()
    interaction_tester = InteractionTester()
    analyzer = AIAnalyzer()
    agent = AutonomousTestingAgent(max_actions=18)
    responsive_tester = ResponsiveTester()
    auth_manager = AuthManager(auth_config or {"enabled": False})
    session_manager = SessionManager()
    auth_crawler = AuthCrawler()
    auth_tester = AuthTester()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        session_options = session_manager.load() or {}
        context = await browser.new_context(ignore_https_errors=True, **session_options)

        auth_result: dict = {"status": "skipped", "reason": "disabled_by_mode"}
        if mode_config.get("auth"):
            auth_result = await auth_manager.login(context, url)
            if auth_result.get("status") == "success":
                await session_manager.save(context)

        crawler = SmartWebsiteCrawler(url, SmartCrawlerConfig(max_pages=mode_config["max_pages"], max_depth=3))
        crawl_result = await retry_async(crawler.crawl, context, retries=1, delay=1)
        pages_to_check = auth_crawler.prioritize(crawl_result.pages)[: mode_config["max_pages"]]
        logger.info("Crawled %s pages (mode=%s)", len(pages_to_check), mode_config["name"])

        page_results = []
        interaction_results = []
        for idx, page_url in enumerate(pages_to_check):
            shot_path = None
            if mode_config.get("screenshots"):
                shot_name = slugify_url(page_url) + ".png"
                shot_path = f"screenshots/{shot_name}"
            result = await retry_async(checker.check_page, context, page_url, shot_path, retries=1, delay=1)
            page_results.append(result.to_dict())

            if mode_config.get("interaction") and idx < mode_config.get("interaction_max_pages", 0):
                interaction_result = await retry_async(interaction_tester.test_page, context, page_url, retries=1, delay=1)
                interaction_results.append(interaction_result)
            logger.info("Checked page: %s", page_url)

        agent_result = {"status": "skipped", "reason": "disabled_by_mode"}
        if mode_config.get("ai_agent"):
            agent_result = await agent.run(context, url)

        responsive_result = {"devices": {"desktop": [], "tablet": [], "mobile": []}, "session_recording": {}, "video_paths": []}
        if mode_config.get("responsive"):
            responsive_result = await responsive_tester.test_pages(
                p, browser, pages_to_check,
                include_groups=mode_config.get("devices", ["desktop", "mobile"]),
                max_pages=mode_config.get("responsive_max_pages", 5),
                record_video=mode_config.get("video", False),
            )

        if mode_config.get("auth"):
            auth_test_result = await auth_tester.test_dashboard(context, pages_to_check) if auth_result.get("status") == "success" else {}
            auth_result["session"] = session_manager.inspect_state()
            auth_result["protected_routes"] = auth_crawler.summarize(pages_to_check)
            auth_result.update(auth_test_result)

        await browser.close()

    report_payload = build_report(
        page_results, interaction_results,
        crawl_result=crawl_result.__dict__,
        agent_session=agent_result,
        responsive_result=responsive_result,
    )
    report_payload["authenticated_testing"] = auth_result
    ai_result = analyzer.analyze(report_payload)
    ai_result["raw_report"] = report_payload
    base_name = "website_review_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    txt_path, json_path = write_reports(base_name, report_payload, ai_result)
    return txt_path, json_path, ai_result


async def _run_single_session(console: Console, target_url: str, mode_config: dict, auth_config: dict | None = None) -> None:
    console.print(f"[cyan]Mode   : {mode_config['name'].upper()}[/cyan]")
    console.print(f"[cyan]URL    : {target_url}[/cyan]")
    console.print(f"[cyan]Pages  : {mode_config['max_pages']}[/cyan]")
    console.print(f"[cyan]Devices: {', '.join(mode_config['devices'])}[/cyan]\n")
    console.print("[cyan]Membuka website...[/cyan]")
    console.print("[cyan]Mengukur performa...[/cyan]")
    console.print("[cyan]Mendeteksi error...[/cyan]")
    console.print("[cyan]Testing interaction...[/cyan]")
    console.print("[cyan]Crawling website...[/cyan]")

    txt_path, json_path, ai_result = await run(target_url, mode_config, auth_config)
    raw_payload = ai_result.get("raw_report", {})
    _render_tools_summary(console, raw_payload)
    _render_technical_explanation(console, raw_payload)
    ai_markdown = ai_result.get("markdown_report") or ai_result.get("analysis") or "Analisis tidak tersedia."
    console.print(Panel(Markdown(ai_markdown), title="HASIL ANALISIS WEB", border_style="green", expand=True))
    console.print("[green]Analisis selesai[/green]")
    console.print(f"[green]TXT report: {txt_path}[/green]")
    console.print(f"[green]JSON report: {json_path}[/green]")


def _render_tools_summary(console: Console, payload: dict) -> None:
    summary = payload.get("summary", {})
    crawler = payload.get("smart_crawler", {})
    interaction = payload.get("interaction_testing", {}).get("summary", {})
    pages = payload.get("pages", [])
    total_forms = sum(len(p.get("forms", [])) for p in pages)
    screenshot_count = len([p for p in pages if p.get("screenshot_path")])
    total_issues = (
        summary.get("total_console_errors", 0)
        + summary.get("total_failed_requests", 0)
        + summary.get("total_broken_images", 0)
        + summary.get("total_accessibility_issues", 0)
        + interaction.get("validation_issues", 0)
    )
    table = Table(title="HASIL TESTING", show_lines=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Pages crawled", str(summary.get("pages_crawled", 0)))
    table.add_row("Interaction tested", str(interaction.get("pages_tested", 0)))
    table.add_row("Console errors", str(summary.get("total_console_errors", 0)))
    table.add_row("Failed requests", str(summary.get("total_failed_requests", 0)))
    table.add_row("Forms", str(total_forms))
    table.add_row("Buttons", str(interaction.get("buttons_total", 0)))
    table.add_row("Total issues", str(total_issues))
    table.add_row("Screenshots", str(screenshot_count))
    table.add_row("Smart crawler routes", str(crawler.get("structure", {}).get("total_routes", 0)))
    console.print(Rule("HASIL TESTING", style="cyan"))
    console.print(table)


def _render_technical_explanation(console: Console, payload: dict) -> None:
    pages = payload.get("pages", [])
    summary = payload.get("summary", {})
    interaction = payload.get("interaction_testing", {}).get("summary", {})
    crawler = payload.get("smart_crawler", {})
    structure = crawler.get("structure", {})
    issues = crawler.get("issues", {})
    avg_dom_ready = round(sum(p.get("dom_ready_ms", 0) for p in pages) / max(len(pages), 1), 2)
    avg_fcp = round(sum((p.get("fcp_ms") or 0) for p in pages) / max(len(pages), 1), 2)
    total_links = sum(len(p.get("links", [])) for p in pages)

    tree = Tree("PENJELASAN TEKNIS", guide_style="bold bright_blue")
    perf = tree.add("Performa")
    perf.add(f"Load Time avg: {summary.get('avg_load_time_ms', 0)} ms")
    perf.add(f"DOM Ready avg: {avg_dom_ready} ms")
    perf.add(f"FCP avg: {avg_fcp} ms")
    inter = tree.add("Interaction")
    inter.add(f"Buttons: {interaction.get('buttons_total',0)} total | {interaction.get('buttons_clicked',0)} clicked | {interaction.get('buttons_failed',0)} failed")
    inter.add(f"Forms: {interaction.get('forms_tested',0)} | validation issues: {interaction.get('validation_issues',0)}")
    crawl_node = tree.add("Crawl")
    crawl_node.add(f"Pages: {len(crawler.get('pages', []))}")
    crawl_node.add(f"Routes: {structure.get('total_routes',0)} | internal: {structure.get('total_internal_links',0)} | external: {structure.get('total_external_links',0)}")
    crawl_node.add(f"Broken: {len(issues.get('broken_routes',[]))} | dead links: {len(issues.get('dead_links',[]))}")
    network = tree.add("Network")
    network.add(f"Failed requests: {summary.get('total_failed_requests', 0)}")
    network.add(f"Total links: {total_links}")
    a11y = tree.add("Accessibility")
    a11y.add(f"Issues: {summary.get('total_accessibility_issues', 0)}")
    a11y.add(f"Broken images: {summary.get('total_broken_images', 0)}")
    responsive_payload = payload.get("responsive_testing", {})
    devices = responsive_payload.get("devices", {})
    resp = tree.add("Responsive")
    resp.add(f"Desktop/Tablet/Mobile: {len(devices.get('desktop',[]))}/{len(devices.get('tablet',[]))}/{len(devices.get('mobile',[]))}")
    resp.add(f"Videos: {len([v for v in responsive_payload.get('video_paths',[]) if v])}")
    auth_payload = payload.get("authenticated_testing", {})
    auth_node = tree.add("Auth")
    auth_node.add(f"Status: {auth_payload.get('status', 'skipped')}")
    auth_node.add(f"Dashboard: {auth_payload.get('dashboard_loaded', False)}")
    console.print(Rule("PENJELASAN TEKNIS", style="bright_blue"))
    console.print(tree)


def _build_auth_config(args, mode_config: dict) -> dict:
    mode_auth = mode_config.get("auth", False)
    force_auth = bool(args and args.auth_enabled and mode_config.get("auth_override_allowed", False))
    return {
        "enabled": mode_auth or force_auth,
        "login_url": getattr(args, "login_url", ""),
        "username": getattr(args, "auth_username", ""),
        "password": getattr(args, "auth_password", ""),
        "username_selector": getattr(args, "username_selector", "input[type=email],input[name*=email i],input[name*=user i]"),
        "password_selector": getattr(args, "password_selector", "input[type=password]"),
        "submit_selector": getattr(args, "submit_selector", "button[type=submit]"),
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description="AI Website Review Bot")
    parser.add_argument("--url", required=False)
    parser.add_argument("--mode", choices=["quick", "standard", "deep"], default="standard")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--auth-enabled", action="store_true")
    parser.add_argument("--login-url", default="")
    parser.add_argument("--auth-username", default="")
    parser.add_argument("--auth-password", default="")
    parser.add_argument("--username-selector", default="input[type=email],input[name*=email i],input[name*=user i]")
    parser.add_argument("--password-selector", default="input[type=password]")
    parser.add_argument("--submit-selector", default="button[type=submit]")
    args = parser.parse_args()

    console = Console()

    try:
        # CLI mode: python main.py --url ... --mode ...
        if args.url:
            mode_config = get_mode_config(args.mode)
            if args.max_pages:
                mode_config["max_pages"] = args.max_pages
            await _run_single_session(console, args.url, mode_config, _build_auth_config(args, mode_config))
            return

        # Stdin mode: dipanggil GUI atau terminal (kirim mode + URL via stdin)
        mode_input  = input("Pilih mode (1/2/3): ").strip()
        mode_name   = MODE_MAP.get(mode_input, "standard")
        mode_config = get_mode_config(mode_name)

        while True:
            try:
                url_input = input("URL: ").strip()
            except EOFError:
                break

            if not url_input or url_input.lower() in EXIT_COMMANDS:
                break

            if not url_input.startswith(("http://", "https://")):
                url_input = "https://" + url_input

            await _run_single_session(console, url_input, mode_config, _build_auth_config(args, mode_config))
            console.print("\n" + "-" * 58 + "\n")

    except KeyboardInterrupt:
        console.print("\n[cyan]Terima kasih.[/cyan]")


if __name__ == "__main__":
    asyncio.run(main())