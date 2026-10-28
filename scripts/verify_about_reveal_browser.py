"""Verify the paused gallery stays absent across navigation and fallbacks."""
import asyncio,json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT,Handler
from playwright.async_api import async_playwright
async def main():
 out=ROOT/'qa/about-reveal';out.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch()
   for width in [320,390,1200]:
    context=await browser.new_context(viewport={'width':width,'height':844})
    async def route(r):
     if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):await r.continue_()
     else:await r.abort()
    await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/about.html',wait_until='networkidle')
    assert await page.locator('.about-poster').count()==0
    assert await page.locator('.about-gallery').count()==0
    assert await page.locator('main h1').is_visible()
    assert await page.locator('.about-profile').is_visible()
    assert await page.locator('footer').count()==1
    assert await page.get_by_text('NOTRE GALERIE',exact=False).count()==0
    assert not await page.evaluate("performance.getEntriesByType('resource').some(r=>r.name.includes('/about-poster-'))")
    await page.screenshot(path=str(out/f'{width}-paused.png'),full_page=True)
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    await page.locator('header nav a').filter(has_text='Songs').click();await page.wait_for_url('**/tracks.html')
    await page.locator('header nav a').filter(has_text='About').click();await page.wait_for_url('**/about.html')
    assert await page.locator('.about-gallery').count()==0
    await context.close()
   for kwargs in [{'reduced_motion':'reduce'},{'java_script_enabled':False}]:
    context=await browser.new_context(**kwargs);page=await context.new_page();await page.goto(origin+'/premiumcuts/about.html')
    assert await page.locator('.about-poster').count()==0
    assert await page.locator('.about-gallery').count()==0
    assert await page.locator('main h1').is_visible()
    await context.close()
   await browser.close()
 finally:server.shutdown();server.server_close()
 (out/'report.json').write_text(json.dumps({'checks':['gallery absent from DOM','no poster requests','intro/profile/footer retained','SPA','320/390/1200','reduced motion','no JS']}))
 print('PASS gallery paused, surrounding About content retained, SPA, responsive, no-JS and reduced-motion')
if __name__=='__main__':asyncio.run(main())
