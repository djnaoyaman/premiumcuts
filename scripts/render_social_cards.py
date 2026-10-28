"""Render social images from real pages and styles, not a parallel poster design.

Run after build.py. Only the fixed listening overlay is suppressed; main content
is captured at its native desktop width, with its original typography and spacing.
The web page itself and all source styles are left untouched.
"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from threading import Thread
from urllib.parse import urlsplit, unquote
import asyncio
import hashlib
import json
import os
import shutil

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
BASE = os.environ.get('BASE_PATH', '/premiumcuts').rstrip('/')
WIDTH, HEIGHT = 1200, 630


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        route = unquote(urlsplit(path).path)
        if BASE and route.startswith(BASE + '/'):
            route = route[len(BASE):]
        return super().translate_path(route)

    def log_message(self, *args):
        pass


async def render():
    manifest = json.loads((DIST / 'social-card-manifest.json').read_text())
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(DIST)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    results = []
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            # No autoplay/random player state, requests to YouTube, or user data.
            context = await browser.new_context(
                viewport={'width': WIDTH, 'height': HEIGHT + 400},
                device_scale_factor=1, java_script_enabled=False,
                locale='ja-JP', reduced_motion='reduce',
            )
            # Cache remote font bytes across pages, and fail rather than silently
            # publishing substitute typography if the site's fonts cannot load.
            font_cache = {}
            async def font_route(route):
                url = route.request.url
                if url not in font_cache:
                    response = await route.fetch()
                    assert response.ok, f'Font request failed: {url} ({response.status})'
                    font_cache[url] = (await response.body(), response.headers)
                body, headers = font_cache[url]
                await route.fulfill(status=200, body=body, headers=headers)
            await context.route('https://fonts.googleapis.com/**', font_route)
            await context.route('https://fonts.gstatic.com/**', font_route)
            page = await context.new_page()
            for n, card in enumerate(manifest['pages'], 1):
                response = await page.goto(origin + BASE + '/' + card['page'], wait_until='networkidle')
                assert response and response.ok, card['page']
                await page.evaluate('document.fonts.ready')
                font_status = await page.evaluate('''async () => {
                    const samples = [
                      ['400 24px "DM Serif Display"', 'Premium Cuts'],
                      ['italic 24px "DM Serif Display"', 'Listed.'],
                      ['400 14px "DM Sans"', 'Premium Cuts'],
                      ['500 14px "Noto Sans JP"', '音楽の世界は広かった。'],
                      ['600 14px "Syne"', 'PREMIUM CUTS']
                    ];
                    return Promise.all(samples.map(async ([font, text]) => {
                      const loaded = await document.fonts.load(font, text);
                      return {font, loaded: loaded.length > 0 && loaded.every(f => f.status === 'loaded')};
                    }));
                }''')
                assert all(f['loaded'] for f in font_status), (card['page'], font_status)
                # This capture-only rule removes a transient, user-controlled
                # overlay, never changes the site's visual content or layout.
                await page.add_style_tag(content='.pc-player{visibility:hidden!important}')
                main = await page.locator('main').bounding_box()
                title = await page.locator('main h1').bounding_box()
                assert main and title, card['page']
                header = await page.locator('body > header').bounding_box()
                assert header, card['page']
                top = round(header['y'] + header['height'])
                assert 0 <= title['y'] - top and title['y'] + title['height'] <= top + HEIGHT, (card['page'], title)
                assert title['x'] >= 0 and title['x'] + title['width'] <= WIDTH, (card['page'], title)
                image = DIST / card['image']
                image.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(image), clip={'x': 0, 'y': top, 'width': WIDTH, 'height': HEIGHT}, animations='disabled')
                styles = await page.locator('main h1').evaluate('''e => {
                  const s=getComputedStyle(e), b=getComputedStyle(document.body);
                  return {fontFamily:s.fontFamily,fontSize:s.fontSize,fontStyle:s.fontStyle,
                    color:s.color,background:b.backgroundColor};
                }''')
                results.append({**card, 'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                                'capture': {'x': 0, 'y': top, 'width': WIDTH, 'height': HEIGHT},
                                'heading': styles, 'fontsLoaded': True})
                if n % 50 == 0 or n == len(manifest['pages']):
                    print(f'Rendered {n}/{len(manifest["pages"])} actual-page social cards', flush=True)
            await context.close()
            await browser.close()
    finally:
        server.shutdown()
        server.server_close()
    home = next(c for c in results if c['page'] == 'index.html')
    # Keep old inbound image URLs useful while all metadata uses versioned URLs.
    shutil.copyfile(DIST / home['image'], DIST / 'og.png')
    (DIST / 'social-card-report.json').write_text(json.dumps({
        'renderer': 'Chromium / actual page main-content crop',
        'width': WIDTH, 'height': HEIGHT, 'pages': results,
    }, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    asyncio.run(render())
