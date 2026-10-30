"""Cross-engine painted tonearm regression; provider mocked, no real audio claims."""
import asyncio,json,io
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from PIL import Image,ImageChops
from verify_back_to_top_browser import ROOT,Handler
from verify_essentials_experience_browser import MOCK
from playwright.async_api import async_playwright
async def verify_disc_tap(page,context):
 # Real hit testing + central transport + GA hooks, with only the provider mocked.
 await page.evaluate("""window.__tapEvents=[];window.gtag=(...args)=>__tapEvents.push(args);
 window.__testTime=72;PremiumPlayer.play('cd-03-d1-21','all');__provider.onStateChange({data:1});
 document.getElementById('pc-seek').value=72;PremiumFullscreenArt.sync();__audioCalls.length=0;__tapEvents.length=0""")
 hit=page.locator('#pc-art-toggle');await hit.scroll_into_view_if_needed()
 b=await hit.bounding_box();x=b['x']+b['width']/2;y=b['y']+b['height']/2
 await page.mouse.click(x,y)
 assert await page.evaluate("__audioCalls.map(x=>x[0]).join(',')")=='pause'
 assert await page.evaluate("PremiumPlayer.getState().artState")=='paused'
 await page.wait_for_timeout(350);a=await page.locator('#disc-spin').get_attribute('transform')
 await page.wait_for_timeout(120);assert a==await page.locator('#disc-spin').get_attribute('transform')
 assert await page.locator('#pc-player').get_attribute('data-needle')=='down'
 assert await hit.get_attribute('aria-label')=='レコードを再生'
 await page.touchscreen.tap(x,y)
 assert await page.evaluate("__audioCalls.map(x=>x[0]).join(',')")=='pause,play'
 assert await page.evaluate("PremiumPlayer.getState().current")=='cd-03-d1-21'
 assert await page.evaluate("Number(document.getElementById('pc-seek').value)") == 72
 await page.wait_for_timeout(120);assert a!=await page.locator('#disc-spin').get_attribute('transform')
 # SVG's square corners and painted arm must not act as the circular button.
 await page.mouse.click(b['x']+2,b['y']+2)
 pivot=await page.locator('#tonearm circle').first.evaluate("e=>{const p=new DOMPoint(850,70).matrixTransform(e.getScreenCTM());return {x:p.x,y:p.y}}")
 await page.mouse.click(pivot['x'],pivot['y'])
 await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+30,y,steps=4);await page.mouse.move(x,y,steps=4);await page.mouse.up()
 assert await page.evaluate('__audioCalls.length')==2
 await hit.focus();await page.keyboard.press('Enter');await page.keyboard.press('Space')
 assert await page.evaluate("__audioCalls.map(x=>x[0]).join(',')")=='pause,play,pause,play'
 events=await page.evaluate("__tapEvents.filter(e=>e[0]==='event').map(e=>[e[1],e[2].action||e[2].state])")
 assert events==[['pc_player_intent','toggle'],['pc_playback_state','paused'],['pc_player_intent','toggle'],['pc_playback_state','playing']]*2,events
 # Leaving ART disables both focus and synthetic/assistive activation.
 await page.locator('[data-pc-mode="hybrid"]').click()
 assert await hit.get_attribute('tabindex')=='-1'
 await hit.dispatch_event('click',{'detail':0})
 assert await page.evaluate('__audioCalls.length')==4
 await page.locator('[data-pc-mode="art"]').click()
 await page.locator('#pc-close-full').click();await hit.dispatch_event('click',{'detail':0})
 assert await page.evaluate('__audioCalls.length')==4
 await page.locator('#pc-full').click()
 await hit.focus();await page.keyboard.press('Enter')
 assert await page.evaluate('__audioCalls.length')==5
 await page.locator('#pc-player').evaluate('e=>e.scrollTop=0')

async def main():
 out=ROOT/'qa/tonearm';out.mkdir(parents=True,exist_ok=True);report=[]
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
 try:
  async with async_playwright() as pw:
   for engine in [pw.chromium,pw.webkit]:
    browser=await engine.launch()
    for width,height in [(320,900),(390,844),(844,390),(1200,900)]:
     context=await browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,has_touch=True);await context.add_init_script(MOCK.replace('this.getCurrentTime=()=>0','this.getCurrentTime=()=>window.__testTime||0').replace('this.pauseVideo=()=>{}',"this.pauseVideo=()=>{__audioCalls.push(['pause']);o.events.onStateChange({data:2})}").replace('this.playVideo=()=>{}',"this.playVideo=()=>{__audioCalls.push(['play']);o.events.onStateChange({data:1})}"))
     async def route(r):
      if r.request.url.startswith(origin):await r.continue_()
      else:await r.abort()
     await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/player.html',wait_until='networkidle');await page.locator('#pc-full').click();await page.locator('[data-pc-mode="art"]').click()
     for state in ['stopped','playing','paused','inner','ended-return']:
      await page.evaluate("window.__testTime=0;document.getElementById('pc-auto').checked=false;PremiumPlayer.play('cd-03-d1-21','all');__provider.onStateChange({data:1});PremiumFullscreenArt.sync()")
      if state=='stopped':await page.evaluate('PremiumPlayer.stop();PremiumFullscreenArt.sync()')
      elif state=='paused':await page.evaluate('__provider.onStateChange({data:2});PremiumFullscreenArt.sync()')
      elif state=='inner':
       await page.evaluate("window.__testTime=180;__provider.onStateChange({data:2});document.getElementById('pc-seek').value=180;PremiumFullscreenArt.sync()")
      elif state=='ended-return':await page.evaluate('__provider.onStateChange({data:0});PremiumFullscreenArt.sync()')
      await page.wait_for_timeout(1900)
      # Freeze motion for pixel comparison, not SVG layout/paint.
      await page.evaluate("document.getElementById('pc-player').dataset.playing='false';window.__realGetState=PremiumPlayer.getState;window.PremiumPlayer.getState=(()=>{const s=PremiumPlayer.getState();return ()=>({...s,playing:false})})()")
      await page.wait_for_timeout(120)
      if width==390 and state in ['stopped','paused']:
       await page.locator('#art-disc').evaluate("e=>e.style.borderRadius='50%'")
       await page.screenshot(path=str(out/f'{engine.name}-{width}-{state}-old-circular-viewport.png'))
       await page.locator('#art-disc').evaluate("e=>e.style.borderRadius=''")
      path=out/f'{engine.name}-{width}-{state}.png';visible=await page.screenshot(path=str(path))
      await page.locator('#tonearm').evaluate("e=>e.style.visibility='hidden'");hidden=await page.screenshot();await page.locator('#tonearm').evaluate("e=>e.style.visibility='visible'")
      a=Image.open(io.BytesIO(visible)).convert('RGB');b=Image.open(io.BytesIO(hidden)).convert('RGB');diff=ImageChops.difference(a,b);count=sum(1 for p in diff.getdata() if max(p)>20)
      assert count>35,(engine.name,width,state,'tonearm not painted',count)
      geometry=await page.evaluate("()=>{const e=document.querySelector('#tonearm'),s=document.querySelector('.pc-stage').getBoundingClientRect(),pts=[...e.querySelectorAll('path,rect,circle')].flatMap(n=>{const b=n.getBBox(),m=n.getScreenCTM();return [b.x,b.x+b.width].flatMap(x=>[b.y,b.y+b.height].map(y=>new DOMPoint(x,y).matrixTransform(m)))}),x=Math.min(...pts.map(p=>p.x)),y=Math.min(...pts.map(p=>p.y)),r=Math.max(...pts.map(p=>p.x)),b=Math.max(...pts.map(p=>p.y));return {arm:[x,y,r-x,b-y],stage:[s.x,s.y,s.width,s.height],angle:e.getAttribute('transform')}}")
      x,y,w,h=geometry['arm'];sx,sy,sw,sh=geometry['stage']
      assert x>=sx-sw*.01 and x+w<=sx+sw*1.01 and y>=max(0,sy)-sh*.01 and y+h<=min(height,sy+sh)+sh*.01,(engine.name,width,state,'arm clipped',geometry)
      if state=='inner':assert '23.18996342096852' in geometry['angle'],geometry
      await page.evaluate('PremiumPlayer.getState=window.__realGetState')
      report.append({'engine':engine.name,'width':width,'state':state,'painted_pixels':count,**geometry})
     await verify_disc_tap(page,context)
     report.append({'engine':engine.name,'width':width,'disc_tap':'passed'})
     if height<500:
      await page.locator('#pc-toggle').scroll_into_view_if_needed()
      controls=await page.locator('#pc-toggle').bounding_box()
      assert controls and controls['y']>=0 and controls['y']+controls['height']<=height,(engine.name,'landscape controls inaccessible',controls)
      await page.screenshot(path=str(out/f'{engine.name}-{width}-controls-scrolled.png'))
      await page.locator('#pc-player').evaluate('e=>e.scrollTop=0')
      await page.wait_for_timeout(100)
      assert await page.locator('#pc-player').evaluate('e=>e.scrollTop')==0
     await context.close()
    await browser.close()
 finally:server.shutdown();server.server_close();(out/'report.json').write_text(json.dumps(report,indent=2))
 print('PASS painted tonearm Chromium/WebKit, mobile/landscape/desktop, stopped/play/pause/inner/return and disc tap/keyboard/GA/isolation')
if __name__=='__main__':asyncio.run(main())
