"""Actual gallery reveal, scoped deterrence and fallback checks."""
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
    assert await page.locator('.about-poster').count()==20
    assert await page.locator('.about-reveal-pending').count()>0
    first=page.locator('.about-poster').first;await first.scroll_into_view_if_needed();await page.wait_for_timeout(1100)
    assert await first.evaluate('e=>getComputedStyle(e).opacity')=='1'
    img=first.locator('img');assert await img.evaluate('e=>e.draggable')==False
    for event in ['contextmenu','dragstart']:
     assert await img.evaluate('(e,n)=>e.dispatchEvent(new Event(n,{bubbles:true,cancelable:true}))',event)==False
     assert await page.locator('main h1').evaluate('(e,n)=>e.dispatchEvent(new Event(n,{bubbles:true,cancelable:true}))',event)==True
    await page.screenshot(path=str(out/f'{width}.png'))
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    await page.locator('header nav a').filter(has_text='Songs').click();await page.wait_for_url('**/tracks.html')
    assert await page.locator('.about-reveal-pending').count()==0
    await page.locator('header nav a').filter(has_text='About').click();await page.wait_for_url('**/about.html');assert await page.locator('.about-gallery').get_attribute('data-reveal-ready')=='true'
    await context.close()
   for kwargs in [{'reduced_motion':'reduce'},{'java_script_enabled':False}]:
    context=await browser.new_context(**kwargs);page=await context.new_page();await page.goto(origin+'/premiumcuts/about.html')
    assert await page.locator('.about-poster').count()==20
    assert await page.locator('.about-poster').last.evaluate('e=>getComputedStyle(e).opacity')=='1'
    await context.close()
   await browser.close()
 finally:server.shutdown();server.server_close()
 (out/'report.json').write_text(json.dumps({'checks':['20 retained','reveal','scoped save deterrence','SPA','320/390/1200','reduced motion','no JS']}))
 print('PASS About reveal, all 20 retained, scoped deterrence, SPA, no-JS and reduced-motion fallbacks')
if __name__=='__main__':asyncio.run(main())
