class LayoutAnalyzer:
    async def analyze(self, page) -> dict:
        return await page.evaluate(
            """() => {
                const navbar = document.querySelector('nav, header');
                const navbarOk = !!navbar;
                const modal = document.querySelector('[role="dialog"], .modal');
                let modalOut = false;
                if (modal) {
                    const r = modal.getBoundingClientRect();
                    modalOut = r.left < 0 || r.top < 0 || r.right > window.innerWidth || r.bottom > window.innerHeight;
                }
                const imageDistortion = Array.from(document.querySelectorAll('img')).slice(0,40).filter(i => i.naturalWidth && i.naturalHeight && Math.abs((i.clientWidth/(i.clientHeight||1)) - (i.naturalWidth/i.naturalHeight)) > 0.6).length;
                return {navbar_ok: navbarOk, modal_out_of_view: modalOut, image_distortion_count: imageDistortion};
            }"""
        )
