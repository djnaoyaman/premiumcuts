"""Actual special-edition disclosure, player continuity and accessibility checks."""
import asyncio,json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT,Handler
from playwright.async_api import async_playwright
MOCK='''(() => { window.__audioCalls=[];window.YT={Player:function(id,o){let video='';window.__provider=o.events;this.loadVideoById=id=>{video=id;__audioCalls.push(['load',id])};this.cueVideoById=id=>{video=id;__audioCalls.push(['cue',id])};this.getVideoData=()=>({video_id:video});this.getDuration=()=>180;this.getCurrentTime=()=>0;this.pauseVideo=()=>{};this.stopVideo=()=>{};this.playVideo=()=>{};this.seekTo=()=>{};setTimeout(()=>o.events.onReady(),0)}};})();'''
async def main():
 out=ROOT/'qa/essentials-experience';out.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch()
   for width in [320,390,1200]:
    context=await browser.new_context(viewport={'width':width,'height':900});await context.add_init_script(MOCK)
    async def route(r):
     if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):await r.continue_()
     else:await r.abort()
    await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/features/essentials.html',wait_until='networkidle')
    assert await page.locator('.essential-recording').count()==40
    assert await page.locator('.essential-recording[open]').count()==0
    assert await page.locator('.essential-recording [data-play-id="005-a-11"]').count()==1
    assert await page.locator('.essential-recording [data-play-id="cd-00-d1-10"]').count()==1
    assert not await page.evaluate('__audioCalls.some(x=>x[0]==="load")')
    first=page.locator('.essential-recording').first;summary=first.locator(':scope > summary');await summary.focus();await page.keyboard.press('Enter')
    assert await first.get_attribute('open') is not None
    await first.locator('[data-play-id]').click();await page.evaluate('__provider.onStateChange({data:1})')
    assert await first.locator('.essential-listening-state').is_visible()
    count=await page.evaluate('__audioCalls.length');await first.locator('.essential-liner > summary').click();assert await page.evaluate('__audioCalls.length')==count
    assert await first.locator('.essential-liner p').is_visible()
    # Native details queues its toggle event; wait for the observable fold result.
    await page.wait_for_function("document.getElementById('pc-player').dataset.expanded === 'false'")
    paragraph=first.locator('.essential-liner p');await paragraph.evaluate("e=>e.scrollIntoView({block:'start',behavior:'instant'})");await page.wait_for_timeout(500)
    a=await paragraph.bounding_box();b=await page.locator('#pc-player').bounding_box()
    assert a and b and (a['y']+a['height']<=b['y'] or a['x']+a['width']<=b['x']), (width,a,b)
    assert await page.evaluate('__audioCalls.length')==count
    await page.screenshot(path=str(out/f'{width}-reading.png'))
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    second=page.locator('.essential-recording').nth(1);await second.locator(':scope > summary').click();assert await first.get_attribute('open') is None;assert await second.get_attribute('open') is not None
    assert await page.evaluate('__audioCalls.length')==count
    await page.locator('header nav a').filter(has_text='Songs').click();await page.wait_for_url('**/tracks.html');assert await page.locator('.essential-recording').count()==0;assert await page.evaluate('__audioCalls.length')==count
    await context.close()
   for kwargs in [{'reduced_motion':'reduce'},{'java_script_enabled':False}]:
    context=await browser.new_context(**kwargs);page=await context.new_page();await page.goto(origin+'/premiumcuts/features/essentials.html');first=page.locator('.essential-recording').first;await first.locator(':scope > summary').click();assert await first.get_attribute('open') is not None
    if 'reduced_motion' in kwargs:assert await first.locator('.essential-inside').evaluate('e=>getComputedStyle(e).animationName')=='none'
    await context.close()
   await browser.close()
 finally:server.shutdown();server.server_close()
 (out/'report.json').write_text(json.dumps({'checks':['38 retained plus Tijuana Taxi and Kerrie Biddell','native keyboard accordion','no autoplay','playback emphasis','liner continuity','SPA','320/390/1200','reduced motion','no JS']}))
 print('PASS Essentials native disclosures, player continuity, scope, 40 selections and accessibility fallbacks')
if __name__=='__main__':asyncio.run(main())
