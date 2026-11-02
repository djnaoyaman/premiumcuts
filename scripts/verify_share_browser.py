"""PROPOSED Actions-only share QA. Not executed by this local review.

Place in scripts/ after accepting the navigation integration. Uses existing server
and provider-mock conventions. All outbound requests are aborted. Consequently
these screenshots are offline layout evidence, not font-faithful social cards;
the existing complete 717-card renderer/check remains mandatory and unchanged.
"""
import asyncio,json
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit
from playwright.async_api import async_playwright
from verify_back_to_top_browser import ROOT,Handler
from verify_essentials_experience_browser import MOCK

OUT=ROOT/'qa/share'
SHARE_MOCK=r'''(() => {
 window.__shareAudit={share:[],copy:[],mode:'success',resolve:null,reject:null};
 const action=(kind,data)=>{
   const a=window.__shareAudit; a[kind].push(data);
   if(a.mode==='cancel')return Promise.reject(new DOMException('Cancelled','AbortError'));
   if(a.mode==='reject')return Promise.reject(new DOMException('Denied','NotAllowedError'));
   if(a.mode==='throw')throw new Error('mock failure');
   if(a.mode==='pending')return new Promise((r,j)=>{a.resolve=r;a.reject=j});
   return Promise.resolve();
 };
 Object.defineProperty(navigator,'share',{configurable:true,value:data=>action('share',data)});
 Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:value=>action('copy',value)}});
 window.__shareDocumentToken=Math.random();
})();'''
PAGES=['/','/tracks.html','/about.html','/features/essentials.html','/features/one-note-samba.html','/my-spin.html','/volumes/001.html','/tracks/001-a-01.html','/player.html']
# Songs may change document.title for a private filter; the public OG title remains canonical.
async def payload(page):
 return await page.evaluate("({title:document.querySelector('meta[property=\"og:title\"]').content,url:document.querySelector('link[rel=canonical]').href})")
async def audit(page):return await page.evaluate('({share:__shareAudit.share,copy:__shareAudit.copy})')
async def reset(page,mode='success'):
 await page.evaluate('(mode)=>{__shareAudit.share=[];__shareAudit.copy=[];__shareAudit.mode=mode}',mode)
async def ready(page):
 await page.wait_for_function("document.querySelector('[data-share-native]')?.disabled===false")
async def canonical_current(page):
 await page.wait_for_function("document.querySelector('[data-page-share]')?.dataset.shareUrl===document.querySelector('link[rel=canonical]')?.href && document.querySelector('[data-page-share]')?.dataset.shareTitle===document.querySelector('meta[property=\"og:title\"]')?.content")
async def main():
 OUT.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')))
 Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}';report=[]
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch()
   async def new_context(width=390,js=True):
    context=await browser.new_context(viewport={'width':width,'height':900},locale='ja-JP',java_script_enabled=js,reduced_motion='reduce')
    blocked=[]
    async def route(r):
     u=urlsplit(r.request.url)
     if u.scheme=='http' and u.netloc==urlsplit(origin).netloc:await r.continue_()
     else:blocked.append(r.request.url);await r.abort()
    await context.route('**/*',route)
    if js:await context.add_init_script(MOCK+'\n'+SHARE_MOCK)
    return context,await context.new_page(),blocked
   for width in [320,390,768,1280]:
    for route in PAGES:
     ctx,page,blocked=await new_context(width)
     await page.goto(origin+'/premiumcuts'+route+'?private_filter=do-not-share#private-state',wait_until='networkidle');await ready(page)
     assert await audit(page)=={'share':[],'copy':[]}
     expected=await payload(page);assert '?' not in expected['url'] and '#' not in expected['url']
     before=await page.evaluate('PremiumPlayer.getState()')
     copy=page.locator('[data-share-copy]');await copy.focus();await page.keyboard.press('Enter')
     await page.wait_for_function("document.querySelector('[data-share-status]').textContent==='URLをコピーしました。'")
     assert (await audit(page))['copy']==[expected['url']]
     share=page.locator('[data-share-native]');await share.focus();await page.keyboard.press('Space')
     await page.wait_for_function("document.querySelector('[data-share-status]').textContent==='共有操作が完了しました。'")
     assert (await audit(page))['share']==[expected],(width,route,await audit(page),expected)
     assert await page.evaluate('PremiumPlayer.getState()')==before
     await reset(page,'reject');await copy.click();field=page.locator('input[data-share-url]');assert await field.count()==1
     assert await field.input_value()==expected['url'];assert await field.evaluate('e=>document.activeElement===e && e.selectionEnd===e.value.length')
     assert await page.locator('[data-share-manual]').get_attribute('open') is not None
     assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,route)
     for b in [copy,share,field]:
      await b.evaluate("e=>e.scrollIntoView({block:'start',behavior:'instant'})")
      rect=await b.bounding_box();assert rect and rect['height']>=44 and rect['x']>=0 and rect['x']+rect['width']<=width,(width,route,rect)
     assert await field.evaluate("e=>{const r=e.getBoundingClientRect();return [r.left+8,r.right-8].every(x=>e.contains(document.elementFromPoint(x,r.top+r.height/2)))}"),(width,route,'manual field obscured')
     # Viewport evidence keeps the share/footer controls readable even on long catalogs.
     name=f'{width}-{route.strip("/").replace("/","-").replace(".html","") or "home"}.png'
     await page.screenshot(path=str(OUT/name))
     report.append({'width':width,'route':route,'payload':expected,'screenshot':name,'externalRequestsAborted':len(blocked),'fonts':'offline fallback; not social-render validation'})
     await ctx.close()
   for width in [390,1280]:
    ctx,page,blocked=await new_context(width);await page.goto(origin+'/premiumcuts/',wait_until='networkidle');await ready(page)
    token=await page.evaluate('__shareDocumentToken')
    # Cancellation is not a copy, and keyboard focus stays on the initiating button.
    await reset(page,'cancel');await page.locator('[data-share-native]').focus();await page.keyboard.press('Enter')
    await page.wait_for_function("document.querySelector('[data-share-status]').textContent==='共有をキャンセルしました。'")
    assert (await audit(page))['copy']==[];assert await page.locator('[data-share-manual]').get_attribute('open') is None
    assert await page.locator('[data-share-native]').evaluate('e=>document.activeElement===e')
    # Busy events explicitly exercise the guard rather than waiting for aria-disabled.
    await reset(page,'pending');await page.locator('[data-share-native]').click()
    await page.locator('[data-share-native]').evaluate('e=>e.click()');await page.locator('[data-share-copy]').evaluate('e=>e.click()')
    a=await audit(page);assert len(a['share'])==1 and not a['copy']
    await page.evaluate('__shareAudit.resolve()');await page.wait_for_function("document.querySelector('[data-share-actions]').getAttribute('aria-busy')==='false'")
    # Real SPA transition while share is pending must replace only share metadata.
    await reset(page,'pending');await page.locator('[data-share-native]').click();await page.evaluate('window.__oldShareResolve=__shareAudit.resolve')
    await page.locator('header nav a[href="/premiumcuts/about.html"]').click();await page.wait_for_url('**/about.html');await canonical_current(page)
    assert await page.evaluate('__shareDocumentToken')==token
    await reset(page);await page.locator('[data-share-copy]').click();await page.evaluate('__oldShareResolve()')
    await page.wait_for_function("document.querySelector('[data-share-status]').textContent==='URLをコピーしました。'")
    assert (await audit(page))['copy']==[(await payload(page))['url']]
    await page.locator('header nav a[href="/premiumcuts/tracks.html"]').click();await page.wait_for_url('**/tracks.html');await canonical_current(page)
    await page.locator('a.catalog-title').first.click();await page.wait_for_url('**/tracks/*.html');await canonical_current(page)
    await page.go_back(wait_until='domcontentloaded');await page.wait_for_url('**/tracks.html');await canonical_current(page)
    await page.go_forward(wait_until='domcontentloaded');await page.wait_for_url('**/tracks/*.html');await canonical_current(page)
    # Synthetic lifecycle test is supplemental; it is not a physical BFCache claim.
    await reset(page,'pending');await page.locator('[data-share-native]').click();await page.evaluate("window.__lateReject=__shareAudit.reject;dispatchEvent(new PageTransitionEvent('pagehide'));__lateReject(new Error('late'))")
    await page.wait_for_function("document.querySelector('[data-share-actions]').getAttribute('aria-busy')==='false'")
    assert await page.locator('[data-share-status]').inner_text()==''
    report.append({'width':width,'case':'cancel, busy, SPA pending, Back/Forward and pagehide','passed':True})
    await ctx.close()
   ctx,page,blocked=await new_context(390,False);await page.goto(origin+'/premiumcuts/about.html',wait_until='networkidle')
   assert await page.locator('[data-share-native]').is_disabled();assert await page.locator('[data-share-copy]').is_disabled()
   summary=page.locator('[data-share-manual] summary');await summary.focus();await page.keyboard.press('Enter')
   assert await page.locator('input[data-share-url]').is_visible();assert await page.locator('input[data-share-url]').input_value()=='https://djnaoyaman.github.io/premiumcuts/about.html'
   # Native scrolling is still available when scripts are disabled.
   rect=await page.locator('input[data-share-url]').bounding_box();await page.mouse.wheel(0,max(0,rect['y']-24));await page.wait_for_timeout(250)
   assert await page.locator('input[data-share-url]').evaluate("e=>{const r=e.getBoundingClientRect();return [r.left+8,r.right-8].every(x=>e.contains(document.elementFromPoint(x,r.top+r.height/2)))}")
   await page.screenshot(path=str(OUT/'390-no-js.png'));await ctx.close()
   ctx,page,blocked=await new_context();await page.goto(origin+'/premiumcuts/404.html',wait_until='networkidle');assert await page.locator('[data-page-share]').count()==0;await ctx.close()
   await browser.close()
 finally:server.shutdown();server.server_close()
 (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS mocked share/copy, clean payload, 4 widths, SPA/history/lifecycle, no-JS and 404; outbound blocked; not physical iOS or social-card validation')
if __name__=='__main__':asyncio.run(main())
