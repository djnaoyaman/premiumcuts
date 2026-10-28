"""Read-only browser QA for the Songs control, with actual responsive player geometry."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from threading import Thread
from urllib.parse import urlsplit, unquote
import asyncio
import json
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/back-to-top'
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = unquote(urlsplit(path).path).removeprefix('/premiumcuts')
        return super().translate_path(path)
    def log_message(self, *args): pass

def overlap(a, b):
    return a['x'] < b['x'] + b['width'] and a['x'] + a['width'] > b['x'] and a['y'] < b['y'] + b['height'] and a['y'] + a['height'] > b['y']

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT / 'dist')))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    report=[]
    try:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch()
            for width,height in [(1200,900),(390,844),(320,568)]:
                context=await browser.new_context(viewport={'width':width,'height':height},locale='ja-JP')
                # No external playback or third-party state is needed for UI QA.
                async def route(r):
                    if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):await r.continue_()
                    else:await r.abort()
                await context.route('**/*',route)
                page=await context.new_page()
                await page.goto(origin+'/premiumcuts/tracks.html',wait_until='networkidle')
                await page.evaluate('document.fonts.ready')
                button=page.locator('#songs-back-to-top')
                assert await button.is_disabled()
                await page.evaluate("window.scrollTo({top:2000,behavior:'instant'})")
                await button.wait_for(state='visible')
                for expanded in [True,False]:
                    if await page.locator('#pc-player').get_attribute('data-expanded') != str(expanded).lower():
                        await page.locator('#pc-fold').click()
                    assert await page.locator('#pc-player').get_attribute('data-expanded')==str(expanded).lower()
                    a=await page.locator('#songs-scroll-nav').bounding_box();b=await page.locator('#pc-player').bounding_box()
                    assert a and b and not overlap(a,b),(width,expanded,a,b)
                    assert a['width']>=44 and a['height']>=44
                    assert a['x']>=0 and a['x']+a['width']<=width and a['y']>=0 and a['y']+a['height']<=height
                    name=f'{width}-'+('expanded' if expanded else 'collapsed')+'.png'
                    await page.screenshot(path=str(OUT/name))
                    report.append({'viewport':[width,height],'playerExpanded':expanded,'button':a,'player':b,'overlap':False,'screenshot':name})
                # Bottom and native range controls follow the complete scrollable extent.
                await page.locator('[data-scroll-edge="bottom"]').click()
                await page.wait_for_function('Math.abs(scrollY-(document.documentElement.scrollHeight-innerHeight)) < 3')
                assert await page.locator('#songs-scroll-nav output').inner_text() == '100%'
                slider = page.locator('#songs-scroll-nav input')
                await slider.fill('50')
                await page.wait_for_function('Math.abs(scrollY/(document.documentElement.scrollHeight-innerHeight)-.5) < .01')
                await slider.focus(); await page.keyboard.press('ArrowDown')
                assert int(await slider.input_value()) in (49,51)
                await button.focus()
                await page.keyboard.press('Enter')
                await page.wait_for_function('window.scrollY < 2')
                assert await page.locator('main h1').evaluate('e=>e===document.activeElement')
                assert await button.is_disabled()
                # Existing internal navigation removes the control on every other page.
                await page.locator('header nav a').filter(has_text='About').click()
                await page.wait_for_url('**/about.html')
                assert await page.locator('#songs-back-to-top').count()==0
                await page.locator('header nav a').filter(has_text='Songs').click()
                await page.wait_for_url('**/tracks.html')
                await page.evaluate("window.scrollTo({top:1500,behavior:'instant'})")
                await page.locator('#songs-back-to-top').wait_for(state='visible')
                await context.close()
            context=await browser.new_context(viewport={'width':390,'height':844},reduced_motion='reduce')
            await context.route('**/*',route)
            page=await context.new_page()
            await page.goto(origin+'/premiumcuts/tracks.html?feature=essentials',wait_until='networkidle')
            await page.evaluate("window.scrollTo({top:1500,behavior:'instant'})")
            await page.locator('#songs-back-to-top').wait_for(state='visible')
            await page.locator('#songs-back-to-top').click()
            assert await page.evaluate('window.scrollY')<2
            assert await page.locator('main h1').evaluate('e=>e===document.activeElement')
            await page.locator('#search').fill('zzzznoresultzzzz')
            await page.wait_for_timeout(200)
            assert await page.locator('#result-count').inner_text() == '0 曲目'
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            await context.close();await browser.close()
    finally:
        server.shutdown();server.server_close()
    (OUT/'report.json').write_text(json.dumps({'checks':'keyboard, reduced-motion, filtered view, SPA isolation, geometry','screenshots':report},indent=2)+'\n')
    print('PASS actual Chromium: desktop/mobile, expanded/collapsed, no overlaps, keyboard, reduced motion and SPA isolation')

if __name__=='__main__':asyncio.run(main())
