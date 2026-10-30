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
async def main():
 out=ROOT/'qa/tonearm';out.mkdir(parents=True,exist_ok=True);report=[]
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT/'dist')));Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
 try:
  async with async_playwright() as pw:
   for engine in [pw.chromium,pw.webkit]:
    browser=await engine.launch()
    for width,height in [(320,900),(390,844),(844,390),(1200,900)]:
     context=await browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1);await context.add_init_script(MOCK)
     async def route(r):
      if r.request.url.startswith(origin):await r.continue_()
      else:await r.abort()
     await context.route('**/*',route);page=await context.new_page();await page.goto(origin+'/premiumcuts/player.html',wait_until='networkidle');await page.locator('#pc-full').click();await page.locator('[data-pc-mode="art"]').click()
     for state in ['stopped','playing','paused','inner','ended-return']:
      await page.evaluate("document.getElementById('pc-auto').checked=false;PremiumPlayer.play('cd-03-d1-21','all');__provider.onStateChange({data:1});PremiumFullscreenArt.sync()")
      if state=='stopped':await page.evaluate('PremiumPlayer.stop();PremiumFullscreenArt.sync()')
      elif state=='paused':await page.evaluate('__provider.onStateChange({data:2});PremiumFullscreenArt.sync()')
      elif state=='inner':
       await page.evaluate("document.getElementById('pc-seek').value=document.getElementById('pc-seek').max;__provider.onStateChange({data:2});PremiumFullscreenArt.sync()")
      elif state=='ended-return':await page.evaluate('__provider.onStateChange({data:0});PremiumFullscreenArt.sync()')
      await page.wait_for_timeout(800 if state=='inner' else 1900)
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
      geometry=await page.evaluate("()=>{const e=document.querySelector('#tonearm'),p=e.getBoundingClientRect(),s=document.querySelector('.pc-stage').getBoundingClientRect();return {arm:[p.x,p.y,p.width,p.height],stage:[s.x,s.y,s.width,s.height],angle:e.getAttribute('transform')}}")
      await page.evaluate('PremiumPlayer.getState=window.__realGetState')
      report.append({'engine':engine.name,'width':width,'state':state,'painted_pixels':count,**geometry})
     await context.close()
    await browser.close()
 finally:server.shutdown();server.server_close();(out/'report.json').write_text(json.dumps(report,indent=2))
 print('PASS painted tonearm Chromium/WebKit, mobile/landscape/desktop, stopped/play/pause/inner/return')
if __name__=='__main__':asyncio.run(main())
