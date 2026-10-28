"""Premium notice is informational, session-scoped and outside player controls."""
import asyncio,json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT,Handler,overlap
from verify_essentials_experience_browser import MOCK
from playwright.async_api import async_playwright
async def main():
 out=ROOT/'qa/premium-hint';out.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
 checks=[]
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch()
   for width in [320,390,430,1200]:
    for blocked in [False,True]:
     context=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');await context.add_init_script(MOCK)
     if blocked:await context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new Error('storage denied')}})")
     async def route(r):
      if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):await r.continue_()
      else:await r.abort()
     await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/my-spin.html',wait_until='networkidle')
     hint=page.locator('.premium-playback-hint');assert await hint.count()==0
     await page.locator('#pc-toggle').click();await hint.wait_for(state='visible')
     assert '加入アカウントへのログイン・ブラウザ設定によります。' in await hint.inner_text()
     assert await hint.locator('a').get_attribute('href')=='https://support.google.com/youtube/answer/7437519?hl=ja'
     hb=await hint.bounding_box()
     for selector in ['.pc-stage','.pc-transport']:
      assert not overlap(hb,await page.locator(selector).bounding_box())
     assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
     await page.screenshot(path=str(out/f'{width}-{blocked}.png'))
     await hint.locator('button').click();assert await hint.count()==0
     await page.locator('#pc-toggle').click();assert await hint.count()==0
     await page.locator('header nav a').filter(has_text='Songs').click();await page.wait_for_url('**/tracks.html');await page.locator('#pc-toggle').click();assert await hint.count()==0
     if not blocked:
      await page.reload(wait_until='networkidle');await page.locator('#pc-toggle').click();assert await hint.count()==0
     checks.append({'width':width,'storageBlocked':blocked,'geometryAndOnce':True});await context.close()
   context=await browser.new_context(viewport={'width':390,'height':900});await context.add_init_script(MOCK)
   await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/my-spin.html',wait_until='networkidle')
   await page.locator('#pc-full').click();await page.locator('#pc-toggle').click();assert await page.locator('.premium-playback-hint').count()==0
   await page.locator('#pc-close-full').click();hint=page.locator('.premium-playback-hint');await hint.wait_for(state='visible')
   await hint.locator('a').focus();await page.wait_for_timeout(8200);assert await hint.count()==1
   await page.locator('#pc-toggle').focus();await page.wait_for_timeout(8200);assert await hint.count()==0
   checks.append({'fullScreenDeferred':True,'focusPreserved':True,'autoDismiss':True});await context.close();await browser.close()
 finally:server.shutdown();server.server_close()
 (out/'report.json').write_text(json.dumps(checks,indent=2));print('PASS Premium hint: responsive, once/session, blocked storage, SPA/reload, fullscreen, focus and timeout')
if __name__=='__main__':asyncio.run(main())
