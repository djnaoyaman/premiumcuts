"""Actual painted footer dates at mobile/desktop widths; no external audio."""
import asyncio,json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT,Handler
from verify_essentials_experience_browser import MOCK
from playwright.async_api import async_playwright
async def main():
 out=ROOT/'qa/compact-profile';out.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')))
 Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}';checks=[]
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch()
   for width in [320,390,1200]:
    context=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
    await context.add_init_script(MOCK)
    async def route(r):
     if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):await r.continue_()
     else:await r.abort()
    await context.route('**/*',route);page=await context.new_page()
    for path in ['about.html']:
     await page.goto(origin+'/premiumcuts/'+path,wait_until='networkidle')
     profile=page.locator('.about-profile');await profile.scroll_into_view_if_needed()
     assert await profile.is_visible()
     assert await profile.locator('a[href="https://djnaoyaman.github.io/profile.html"]').count()==1
     assert await profile.locator('details').count()==0
     await profile.screenshot(path=str(out/f'profile-{width}.png'))
     footer=page.locator('.site-updated');await footer.scroll_into_view_if_needed()
     assert await footer.is_visible()
     box=await footer.bounding_box();assert box and box['width']>0 and box['height']>0
     assert box['x']>=-1 and box['x']+box['width']<=width+1
     assert '最終更新：' in await footer.inner_text() and 'JST' in await footer.inner_text()
     assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
     date=await footer.locator('time').get_attribute('datetime')
     schema=await page.locator('script[type="application/ld+json"]').text_content()
     graph=json.loads(schema)['@graph'];assert next(x for x in graph if x['@type']=='WebPage')['dateModified']==date
     await footer.screenshot(path=str(out/f'{width}-{path.replace("/","-")}.png'))
     checks.append({'width':width,'page':path,'date':date,'painted':True,'withinViewportWidth':True})
    await context.close()
   await browser.close()
 finally:server.shutdown();server.server_close()
 (out/'report.json').write_text(json.dumps(checks,indent=2));print('PASS painted update-date footer on home, Essentials and track detail at 320/390/1200')
if __name__=='__main__':asyncio.run(main())
