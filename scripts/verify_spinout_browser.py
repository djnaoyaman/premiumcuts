"""Actual responsive header and legacy Spinout navigation checks (no playback)."""
import asyncio
import json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT, Handler, overlap
from playwright.async_api import async_playwright

async def main():
    out = ROOT / 'qa/spinout'
    out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT / 'dist')))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    report = []
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            for width in [320, 390, 1200]:
                context = await browser.new_context(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
                async def route(r):
                    if r.request.url.startswith((origin, 'https://fonts.googleapis.com/', 'https://fonts.gstatic.com/')):
                        await r.continue_()
                    else:
                        await r.abort()
                await context.route('**/*', route)
                page = await context.new_page()
                await page.goto(origin + '/premiumcuts/my-spin.html', wait_until='networkidle')
                await page.evaluate('document.fonts.ready')
                nav = page.locator('header nav a')
                assert await nav.all_text_contents() == ['Works', 'Songs', 'Essentials', 'Remix', 'Spinout', 'About']
                boxes = [await nav.nth(i).bounding_box() for i in range(6)]
                assert all(b and b['x'] >= 0 and b['x'] + b['width'] <= width for b in boxes)
                assert all(not overlap(a, b) for i, a in enumerate(boxes) for b in boxes[i+1:])
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert await page.locator('h1').inner_text() == 'Spinout.'
                assert await page.evaluate("PremiumPlayer.getState().scope === 'myspin' && PremiumPlayer.getState().queue.length === 11")
                assert await nav.nth(4).get_attribute('class') == 'selected'
                await page.screenshot(path=str(out / f'{width}-spinout.png'))
                await nav.nth(5).click()
                await page.wait_for_url('**/about.html')
                spinout = page.locator('header nav a').nth(4)
                await spinout.focus()
                await page.keyboard.press('Enter')
                await page.wait_for_url('**/my-spin.html')
                assert await page.locator('h1').inner_text() == 'Spinout.'
                assert await page.evaluate("PremiumPlayer.getState().scope === 'myspin' && PremiumPlayer.getState().queue.length === 11")
                report.append({'width': width, 'headerLinks': boxes, 'keyboardLegacyRoute': True, 'noOverflowOrOverlap': True})
                await context.close()
            await browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    print('PASS Spinout header order, responsive geometry, legacy URL and keyboard SPA navigation at 320/390/1200px')

if __name__ == '__main__':
    asyncio.run(main())
