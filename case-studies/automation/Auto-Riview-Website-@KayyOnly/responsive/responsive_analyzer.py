from visual_testing.layout_analyzer import LayoutAnalyzer
from visual_testing.visual_detector import VisualDetector


class ResponsiveAnalyzer:
    def __init__(self) -> None:
        self.visual = VisualDetector()
        self.layout = LayoutAnalyzer()

    async def analyze(self, page) -> dict:
        visual = await self.visual.detect(page)
        layout = await self.layout.analyze(page)
        text_issues = await page.evaluate(
            """() => Array.from(document.querySelectorAll('p,span,a,button,h1,h2,h3,li,label')).slice(0,200)
                .filter(el => {
                    const style = getComputedStyle(el);
                    if (style.whiteSpace !== 'nowrap') return false;
                    return el.scrollWidth > el.clientWidth + 1;
                }).slice(0,20).map(el => ({type: 'text_overflow', tag: el.tagName, text: (el.textContent || '').trim().slice(0,60)}))"""
        )
        navbar_issues = [] if layout.get("navbar_ok") else [{"type": "broken_navbar", "detail": "missing_nav_or_header"}]
        modal_issues = [{"type": "modal_overflow"}] if layout.get("modal_out_of_view") else []

        issue_map = {
            "horizontal_overflow": [i for i in visual["overflow"] if i.get("type") == "horizontal_overflow"],
            "element_outside_viewport": visual["offscreen"],
            "overlap": visual["overlap"],
            "hidden_button": [i for i in visual["hidden"] if i.get("tag") == "BUTTON"],
            "text_overflow": text_issues,
            "modal_overflow": modal_issues,
            "broken_navbar": navbar_issues,
            "responsive_layout_broken": [i for i in visual["overflow"] if i.get("type") == "element_overflow"],
        }
        total_issues = sum(len(v) for v in issue_map.values())
        status = "ok" if total_issues == 0 else "issue_found"
        return {
            "status": status,
            "visual_issues": visual,
            "layout": layout,
            "issue_map": issue_map,
            "total_issues": total_issues,
        }
