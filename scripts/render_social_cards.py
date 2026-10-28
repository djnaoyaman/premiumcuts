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
import sys

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
    cards = manifest['pages']
    sample = '--sample' in sys.argv
    if sample:
        selected = {'index.html','tracks.html','features/essentials.html','my-spin.html','about.html','tracks/001-a-01.html','volumes/001.html','all-tracks.html'}
        cards = [c for c in cards if c['page'] in selected]
        assert len(cards) == len(selected)
    results = []
    completed = 0
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            # No autoplay/random player state, requests to YouTube, or user data.
            context = await browser.new_context(
                viewport={'width': WIDTH, 'height': HEIGHT + 400},
                device_scale_factor=1,
                locale='ja-JP', reduced_motion='reduce',
            )
            async def static_assets(route):
                if route.request.resource_type in {'script', 'media', 'websocket'}:
                    await route.abort()
                else:
                    await route.continue_()
            await context.route('**/*', static_assets)
            # Cache remote font bytes across pages, and fail rather than silently
            # publishing substitute typography if the site's fonts cannot load.
            font_cache = {}
            async def font_route(route):
                url = route.request.url
                async def fetch_font():
                    response = await route.fetch()
                    assert response.ok, f'Font request failed: {url} ({response.status})'
                    return await response.body(), response.headers
                if url not in font_cache:
                    font_cache[url] = asyncio.create_task(fetch_font())
                body, headers = await font_cache[url]
                await route.fulfill(status=200, body=body, content_type=headers.get('content-type', 'application/octet-stream'))
            await context.route('https://fonts.googleapis.com/**', font_route)
            await context.route('https://fonts.gstatic.com/**', font_route)
            async def worker(batch):
                nonlocal completed
                page = await context.new_page()
                for card in batch:
                    if sample:
                        print('Capturing '+card['page'], flush=True)
                    response = await page.goto(origin + BASE + '/' + card['page'], wait_until='networkidle')
                    assert response and response.ok, card['page']
                    await asyncio.wait_for(page.evaluate('document.fonts.ready'), timeout=30)
                    font_status = await asyncio.wait_for(page.evaluate('''async () => {
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
                    }'''), timeout=30)
                    assert all(f['loaded'] for f in font_status), (card['page'], font_status)
                    # Retain the original opening block and its exact geometry.
                    # Hide later sections rather than crop through controls or text;
                    # visibility preserves the public page's spacing and paper grain.
                    framing = await page.evaluate('''() => {
                        const main = document.querySelector('main');
                        const children = [...main.children];
                        let keep, kind;
                        if (main.querySelector(':scope > .hero')) {
                            const hero = main.querySelector(':scope > .hero');
                            keep = [hero]; kind = 'home hero';
                            for (const e of hero.children) {
                                if (!e.matches('.hero-top,.hero-content')) e.style.visibility = 'hidden';
                            }
                        } else {
                            const hero = main.querySelector(':scope > .song-hero,:scope > .volume-hero,:scope > .essentials-heading,:scope > .catalog-heading');
                            if (hero) {
                                keep = [hero, ...main.querySelectorAll(':scope > .breadcrumb')];
                                kind = hero.className;
                            } else if (main.classList.contains('about-page')) {
                                keep = children.filter(e => e.matches('.breadcrumb,.eyebrow,h1,.about-body,p'));
                                const sections = main.querySelectorAll('.about-body > section');
                                for (const e of [...sections].slice(1)) e.style.visibility = 'hidden';
                                kind = 'about opening';
                            } else {
                                keep = children.filter(e => e.matches('.breadcrumb,h1'));
                                const lead = main.querySelector(':scope > p');
                                if (lead) keep.push(lead);
                                kind = 'page title and lead';
                            }
                        }
                        for (const e of children) if (!keep.includes(e)) e.style.visibility = 'hidden';
                        return kind;
                    }''')
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
                                    'heading': styles, 'fontsLoaded': True, 'framing': framing})
                    completed += 1
                    if completed % 50 == 0 or completed == len(cards):
                        print(f'Rendered {completed}/{len(cards)} actual-page social cards', flush=True)
                await page.close()
            # Three pages share one browser and cached font responses. Keep CPU
            # and memory bounded while avoiding a serial full-catalog render.
            workers = min(3, len(cards))
            await asyncio.gather(*(worker(cards[i::workers]) for i in range(workers)))
            await context.close()
            await browser.close()
    finally:
        server.shutdown()
        server.server_close()
    results.sort(key=lambda c:c['page'])
    home = next(c for c in results if c['page'] == 'index.html')
    # Keep old inbound image URLs useful while all metadata uses versioned URLs.
    shutil.copyfile(DIST / home['image'], DIST / 'og.png')
    report_name = 'social-card-sample-report.json' if sample else 'social-card-report.json'
    (DIST / report_name).write_text(json.dumps({
        'renderer': 'Chromium / original opening block with following sections excluded',
        'width': WIDTH, 'height': HEIGHT, 'pages': results,
    }, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    asyncio.run(render())
