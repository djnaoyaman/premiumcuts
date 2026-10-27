"""Verify generated About-only poster gallery and its image assets."""
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image

root = Path(__file__).resolve().parents[1]
class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

about = (root/'dist/about.html').read_text()
tags = Tags(about).tags
posters = [a for t,a in tags if t == 'img' and 'about-poster-' in a.get('src', '')]
assert len(posters) == 4
assert 'about-portrait' not in about
assert 'couple-french-transparent.webp' not in about
assert about.index('デザインについて。') < about.index('about-gallery') < about.index('<footer')
assert about.count('id="about-gallery-title"') == 1
assert len([a for t,a in tags if t == 'figure' and a.get('class') == 'about-poster']) == 4
for i, image in enumerate(posters, 1):
    name = f'about-poster-{i:02}.webp'
    assert image['src'].endswith('/assets/'+name)
    assert image.get('width') == '1024' and image.get('height') == '1536'
    assert image.get('loading') == 'lazy' and image.get('decoding') == 'async'
    assert image.get('alt')
    links = [a for t,a in tags if t == 'a' and a.get('href', '').endswith('/assets/'+name)]
    assert len(links) == 1 and links[0].get('target') == '_blank'
    assert 'noopener' in links[0].get('rel', '')
    asset = root/'dist/assets'/name
    with Image.open(asset) as im:
        assert im.size == (1024, 1536) and im.format == 'WEBP'
        assert not im.getexif() and not any(k in im.info for k in ('exif','xmp'))
        assert getattr(im, 'n_frames', 1) == 1
    assert asset.stat().st_size < 800_000
assert about.count('Paris, 2002') == 2  # caption and link label, only poster 01
assert 'about-gallery' not in (root/'dist/index.html').read_text()
css = (root/'dist/style.css').read_text()
assert '.about-poster-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))' in css
assert '@media(max-width:700px)' in css and '.about-poster-grid{grid-template-columns:1fr;' in css
assert 'object-fit:contain' in css
print('PASS four uncropped About-only posters; asset sizes; alt/lazy dimensions; accessible enlarge links; responsive rules')
