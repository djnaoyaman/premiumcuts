"""Render approved fullscreen ART with actual DOM and mocked YouTube (not audio verification)."""
import asyncio,json
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from verify_back_to_top_browser import ROOT,Handler
from verify_essentials_experience_browser import MOCK
from playwright.async_api import async_playwright
async def main():
 out=ROOT/'qa/fullscreen-art';out.mkdir(parents=True,exist_ok=True)
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}';report=[]
 try:
  async with async_playwright() as pw:
   browser=await pw.chromium.launch()
   for width in [320,390,1200]:
    context=await browser.new_context(viewport={'width':width,'height':900});await context.add_init_script(MOCK)
    async def route(r):
     if r.request.url.startswith(origin):await r.continue_()
     else:await r.abort()
    await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/player.html',wait_until='networkidle')
    assert await page.locator('#art-disc').count()==1
    await page.locator('#pc-full').click();await page.locator('[data-pc-mode="art"]').click()
    result=await page.evaluate('''()=>{const items=[...PREMIUM_AUDIO,...PREMIUM_MYSPIN];let overflow=[];for(const t of items){PremiumPlayer.play(t.id,t.id.startsWith('myspin-')?'myspin':'all');PremiumFullscreenArt.sync();for(const n of document.querySelectorAll('#label-copy text')){const b=n.getBBox();if(Math.max(...[b.x,b.x+b.width].flatMap(x=>[b.y,b.y+b.height].map(y=>Math.hypot(x,y))))>86)overflow.push({id:t.id,text:n.textContent,b});}}return {count:items.length,metadata:Object.keys(PREMIUM_ART).length,overflow}}''')
    assert result['overflow']==[],result
    assert result['count']==result['metadata'],result
    await page.evaluate("PremiumPlayer.play('001-b-12','all');__provider.onStateChange({data:1});PremiumFullscreenArt.sync();document.getElementById('pc-auto').checked=false")
    await page.wait_for_timeout(350);first=await page.locator('#disc-spin').get_attribute('transform');await page.wait_for_timeout(350);assert first!=await page.locator('#disc-spin').get_attribute('transform')
    await page.evaluate("__provider.onStateChange({data:2});PremiumFullscreenArt.sync()");paused=await page.locator('#disc-spin').get_attribute('transform');await page.wait_for_timeout(350);assert paused==await page.locator('#disc-spin').get_attribute('transform');assert await page.locator('#pc-player').get_attribute('data-needle')=='down'
    await page.screenshot(path=str(out/f'{width}-paused-label.png'))
    await page.evaluate("__provider.onStateChange({data:1});__provider.onStateChange({data:0});PremiumFullscreenArt.sync()")
    await page.wait_for_timeout(850);assert '23.18996342096852' in (await page.locator('#tonearm').get_attribute('transform'));await page.screenshot(path=str(out/f'{width}-innermost-groove.png'))
    await page.wait_for_timeout(900);assert await page.locator('#pc-player').get_attribute('data-needle')=='up'
    await page.evaluate("PremiumPlayer.playReference({track:'001-a-11',video:'i5qBz24yrAU',title:'Reference rendition',artist:'Reference artist'});PremiumFullscreenArt.sync()")
    assert 'Reference rendition' in await page.locator('#label-copy').text_content();assert '発売 未確認' in await page.locator('#label-copy').text_content()
    await page.evaluate('PremiumPlayer.stop();PremiumFullscreenArt.sync()');assert await page.locator('#pc-player').get_attribute('data-needle')=='up'
    await page.locator('#pc-close-full').click();assert not await page.locator('#art-disc').is_visible();assert await page.locator('.pc-original-label').is_visible()
    assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth');report.append({'width':width,**result});await context.close()
   context=await browser.new_context(reduced_motion='reduce');await context.add_init_script(MOCK);await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/player.html',wait_until='networkidle');await page.locator('#pc-full').click();await page.evaluate("__provider.onStateChange({data:1});PremiumFullscreenArt.sync()");await page.wait_for_timeout(100);a=await page.locator('#disc-spin').get_attribute('transform');await page.wait_for_timeout(350);assert a==await page.locator('#disc-spin').get_attribute('transform');await context.close();await browser.close()
 finally:server.shutdown();server.server_close()
 (out/'report.json').write_text(json.dumps(report,indent=2));print('PASS fullscreen ART all playable labels, 320/390/1200, rotation, pause/end/stop, reference unknowns, compact fallback, reduced motion')
if __name__=='__main__':asyncio.run(main())
