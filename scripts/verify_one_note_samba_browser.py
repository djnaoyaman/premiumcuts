"""Feature reading/layout and real-browser player integration with a mocked provider."""
import asyncio
import json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT, Handler
from playwright.async_api import async_playwright

MOCK = '''(() => {
  window.__audioCalls=[];
  window.YT={Player:function(id,options){let video='';window.__provider=options.events;
    this.loadVideoById=id=>{video=id;__audioCalls.push(['load',id])};
    this.cueVideoById=id=>{video=id;__audioCalls.push(['cue',id])};
    this.getVideoData=()=>({video_id:video});this.getDuration=()=>180;this.getCurrentTime=()=>0;
    this.pauseVideo=()=>__audioCalls.push(['pause']);this.stopVideo=()=>__audioCalls.push(['stop']);
    this.playVideo=()=>__audioCalls.push(['play']);this.seekTo=()=>{};
    setTimeout(()=>options.events.onReady(),0);
  }};
})();'''

async def main():
    out = ROOT / 'qa/one-note-samba'
    out.mkdir(parents=True, exist_ok=True)
    expected = [v['id'] for v in json.loads((ROOT / 'one_note_samba.json').read_text())['versions']]
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT / 'dist')))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    report = []
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            for width in [390, 1200]:
                context = await browser.new_context(viewport={'width':width,'height':900}, reduced_motion='reduce')
                await context.add_init_script(MOCK)
                async def route(r):
                    if r.request.url.startswith((origin,'https://fonts.googleapis.com/','https://fonts.gstatic.com/')):
                        await r.continue_()
                    else:
                        await r.abort()
                await context.route('**/*',route)
                page = await context.new_page()
                await page.goto(origin+'/premiumcuts/features/one-note-samba.html',wait_until='networkidle')
                await page.evaluate('document.fonts.ready')
                state = await page.evaluate('PremiumPlayer.getState()')
                assert state['scope']=='feature:one-note-samba' and state['queue']==expected and not state['wantsPlay']
                assert not await page.evaluate("__audioCalls.some(x=>x[0]==='load'||x[0]==='play')")
                assert await page.locator('.spinout-story section').count()==6
                assert await page.locator('.spinout-version').count()==10
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                await page.screenshot(path=str(out/f'{width}-history.png'))
                await page.locator('#pc-fold').click()
                await page.locator('#feature-versions-title').scroll_into_view_if_needed()
                await page.screenshot(path=str(out/f'{width}-versions.png'))
                play = page.locator('.spinout-version [data-play-id]').first
                await play.focus();await page.keyboard.press('Enter')
                await page.evaluate('__provider.onStateChange({data:1})')
                count = await page.evaluate('__audioCalls.length')
                await page.locator('.spinout-version h3 a').first.click()
                await page.wait_for_url('**/tracks/'+expected[0]+'.html')
                assert await page.evaluate("PremiumPlayer.getState().scope==='feature:one-note-samba' && PremiumPlayer.getState().playing")
                assert await page.evaluate('__audioCalls.length')==count
                await page.go_back();await page.wait_for_url('**/features/one-note-samba.html')
                await page.wait_for_function("document.querySelector('.spinout-story')")
                assert await page.evaluate('PremiumPlayer.getState().queue')==expected
                await page.locator('header nav a').filter(has_text='Spinout').click()
                await page.wait_for_url('**/my-spin.html')
                assert await page.evaluate('PremiumPlayer.getState().queue.length')==11
                assert await page.evaluate('__audioCalls.length')==count
                shelf = page.locator('.spinout-feature-card')
                await shelf.focus();await page.keyboard.press('Enter')
                await page.wait_for_url('**/features/one-note-samba.html')
                assert await page.evaluate('PremiumPlayer.getState().queue')==expected
                await page.evaluate('__provider.onError({data:101})')
                assert not await page.evaluate('PremiumPlayer.getState().wantsPlay')
                report.append({'width':width,'versions':10,'noOverflow':True,'coldLoadSilent':True,'keyboardAndSPA':True,'mockedProviderOnly':True})
                await context.close()
            context = await browser.new_context(java_script_enabled=False, viewport={'width':390,'height':900})
            page = await context.new_page()
            await page.goto(origin+'/premiumcuts/features/one-note-samba.html')
            assert await page.locator('.spinout-story').is_visible()
            assert await page.locator('.spinout-version a[href^="https://www.youtube.com/"]').count()==10
            await context.close();await browser.close()
    finally:
        server.shutdown();server.server_close()
    (out/'report.json').write_text(json.dumps(report,indent=2))
    print('PASS feature history/layout, exact10 context, keyboard SPA/audio continuity, provider error and no-JS reading fallback')

if __name__=='__main__':
    asyncio.run(main())
