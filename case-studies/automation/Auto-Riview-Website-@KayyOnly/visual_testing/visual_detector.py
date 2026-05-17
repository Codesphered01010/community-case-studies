from visual_testing.overflow_detector import OverflowDetector
from visual_testing.overlap_detector import OverlapDetector


class VisualDetector:
    def __init__(self) -> None:
        self.overflow_detector = OverflowDetector()
        self.overlap_detector = OverlapDetector()

    async def detect(self, page) -> dict:
        overflow = await self.overflow_detector.detect(page)
        overlap = await self.overlap_detector.detect(page)
        hidden = await page.evaluate(
            """() => Array.from(document.querySelectorAll('button,a,input,[role="button"]'))
                .filter(el => {
                    const r = el.getBoundingClientRect();
                    const style = getComputedStyle(el);
                    return style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0' || r.width === 0 || r.height === 0;
                }).slice(0,20).map(el => ({type:'hidden_element', tag: el.tagName, text: (el.innerText || '').slice(0,50)}))"""
        )
        offscreen = await page.evaluate(
            """() => Array.from(document.querySelectorAll('button,a,input,[role="dialog"],nav')).slice(0,80)
                .filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.right < 0 || r.bottom < 0 || r.left > window.innerWidth || r.top > window.innerHeight;
                }).slice(0,20).map(el => ({type:'offscreen_element', tag: el.tagName}))"""
        )
        return {"overflow": overflow, "overlap": overlap, "hidden": hidden, "offscreen": offscreen}
