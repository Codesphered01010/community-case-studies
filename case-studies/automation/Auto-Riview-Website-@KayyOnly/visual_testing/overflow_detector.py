class OverflowDetector:
    async def detect(self, page) -> list[dict]:
        return await page.evaluate(
            """() => {
                const issues = [];
                const doc = document.documentElement;
                if (doc.scrollWidth > window.innerWidth + 2) {
                    issues.push({type: 'horizontal_overflow', scrollWidth: doc.scrollWidth, viewport: window.innerWidth});
                }
                for (const el of document.querySelectorAll('*')) {
                    const r = el.getBoundingClientRect();
                    if (r.width > window.innerWidth + 4) {
                        issues.push({type:'element_overflow', tag: el.tagName, className: el.className || '', width: r.width});
                        if (issues.length > 20) break;
                    }
                }
                return issues;
            }"""
        )
