class OverlapDetector:
    async def detect(self, page) -> list[dict]:
        return await page.evaluate(
            """() => {
                const issues = [];
                const candidates = Array.from(document.querySelectorAll('button, a, input, nav, header, [role="dialog"]')).slice(0, 60);
                for (let i = 0; i < candidates.length; i++) {
                    const a = candidates[i].getBoundingClientRect();
                    if (a.width < 6 || a.height < 6) continue;
                    for (let j = i + 1; j < candidates.length; j++) {
                        const b = candidates[j].getBoundingClientRect();
                        const overlap = !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom);
                        if (overlap) {
                            issues.push({type: 'overlap', a: candidates[i].tagName, b: candidates[j].tagName});
                            if (issues.length > 20) return issues;
                        }
                    }
                }
                return issues;
            }"""
        )
