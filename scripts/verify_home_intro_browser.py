"""Observe the real homepage sweep, its timing and interruption safeguards."""
from pathlib import Path
from http.server import ThreadingHTTPServer
from functools import partial
from threading import Thread
import asyncio
import json
from playwright.async_api import async_playwright
from verify_back_to_top_browser import Handler

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/home-intro'
TRACE='''(() => {
 const native=window.scrollTo.bind(window); window.__introTrace=[];
 window.scrollTo=(...args)=>{native(...args);window.__introTrace.push({time:performance.now(),y:window.scrollY});};
})()'''

async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')))
    Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}'
    reports=[]
    try:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch()
            async def context(width=1200,reduced=False):
                ctx=await browser.new_context(viewport={'width':width,'height':844},has_touch=True,
                     reduced_motion='reduce' if reduced else 'no-preference',record_video_dir=str(OUT/'video'))
                async def route(r):
                    if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):await r.continue_()
                    else:await r.abort()
                await ctx.route('**/*',route)
                await ctx.add_init_script(TRACE)
                return ctx,await ctx.new_page()
            for width in [1200,390]:
                ctx,page=await context(width)
                await page.goto(origin+'/premiumcuts/',wait_until='domcontentloaded')
                await page.wait_for_function('window.__introTrace.length>3 && window.__introTrace.at(-1).y===0')
                trace=await page.evaluate('window.__introTrace')
                assert trace[0]['y']>844 and trace[-1]['y']==0,trace
                duration=trace[-1]['time']-trace[0]['time']
                assert 600<=duration<=1000,duration
                assert all(b['y']<=a['y'] for a,b in zip(trace,trace[1:])),trace
                assert await page.evaluate('document.activeElement===document.body')
                await page.screenshot(path=str(OUT/f'{width}-finished.png'))
                reports.append({'case':f'{width}-complete','durationMs':duration,'trace':trace})
                await page.reload(wait_until='networkidle')
                assert await page.evaluate('window.__introTrace.length')==0
                await ctx.close()
            for event in ['wheel','touchstart','keydown']:
                ctx,page=await context(390)
                await page.goto(origin+'/premiumcuts/',wait_until='domcontentloaded')
                await page.wait_for_function('window.__introTrace.length>=2 && window.scrollY>0')
                if event=='wheel':await page.mouse.wheel(0,1)
                elif event=='keydown':await page.keyboard.press('Escape')
                else:await page.dispatch_event('body','touchstart')
                count=await page.evaluate('window.__introTrace.length')
                await page.wait_for_timeout(800)
                assert await page.evaluate('window.__introTrace.length')==count,event
                reports.append({'case':event+'-cancel','scrollY':await page.evaluate('window.scrollY'),'traceCount':count})
                await ctx.close()
            for path,reduced in [('/',True),('/#collection',False),('/tracks.html',False),('/about.html',False)]:
                ctx,page=await context(390,reduced)
                await page.goto(origin+'/premiumcuts'+path,wait_until='networkidle')
                await page.wait_for_timeout(1000)
                assert await page.evaluate('window.__introTrace.length')==0,(path,reduced)
                reports.append({'case':'skip','path':path,'reduced':reduced})
                await ctx.close()
            # First encounter via an internal link runs, but a history return
            # skips even when the once-per-session flag is deliberately cleared.
            ctx,page=await context()
            await page.goto(origin+'/premiumcuts/about.html',wait_until='networkidle')
            await page.locator('header .brand').click()
            await page.wait_for_function('window.__introTrace.some(x=>x.y>1000) && window.scrollY===0')
            await page.locator('header nav a').filter(has_text='About').click()
            await page.wait_for_url('**/about.html')
            await page.evaluate("sessionStorage.removeItem('premium-cuts-home-intro-v1');window.__introTrace=[]")
            await page.go_back(wait_until='domcontentloaded')
            await page.wait_for_timeout(1200)
            assert not await page.evaluate('window.__introTrace.some(x=>x.y>1000)')
            reports.append({'case':'SPA first-entry and history-skip','passed':True})
            await ctx.close();await browser.close()
    finally:server.shutdown();server.server_close()
    (OUT/'report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    print('PASS actual Chromium: fast upward sweep, desktop/mobile, once/session, input cancellation, reduced motion, anchors, other pages and SPA history')

if __name__=='__main__':asyncio.run(main())
