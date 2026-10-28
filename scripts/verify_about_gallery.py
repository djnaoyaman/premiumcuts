"""Verify generated About-only poster gallery and its image assets."""
from pathlib import Path
from html.parser import HTMLParser
import ast, hashlib
from urllib.parse import urlsplit, parse_qs
from PIL import Image

root = Path(__file__).resolve().parents[1]
class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

about = (root/'dist/about.html').read_text()
# The archived markup stays restorable, but must not create live DOM elements.
assert '<!-- ABOUT GALLERY PAUSED\n' in about
active_tags = Tags(about).tags
assert not any('about-poster' in a.get('class', '') or a.get('class') == 'about-gallery' for t,a in active_tags)
assert not any('about-poster-' in a.get('src', '') for t,a in active_tags)
archived = about.split('<!-- ABOUT GALLERY PAUSED\n', 1)[1].split('\nEND ABOUT GALLERY PAUSED -->', 1)[0]
tags = Tags(archived).tags
source = ast.parse((root/'build.py').read_text())
manifest = next(ast.literal_eval(node.value) for node in source.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'about_posters' for target in node.targets))
assert len(manifest) >= 14 and len(manifest) % 2 == 0
posters = [a for t,a in tags if t == 'img' and 'about-poster-' in a.get('src', '')]
assert len(posters) == len(manifest)
assert 'about-portrait' not in about
assert 'couple-french-transparent.webp' not in about
assert about.index('デザインについて。') < about.index('<section class="about-gallery"') < about.index('<footer')
assert about.count('id="about-gallery-title"') == 1
assert 'about-gallery-story' not in about and 'about-gallery-coda' not in about
assert 'Married in 2013.' not in about and 'Influenced by Saya.' not in about
assert len([a for t,a in tags if t == 'figure' and a.get('class') == 'about-poster']) == len(manifest)
sequence = [entry[0] for entry in manifest]
assert len(set(sequence)) == len(sequence)
for number, image in zip(sequence, posters):
    name = f'about-poster-{number}.webp'
    assert urlsplit(image['src']).path.endswith('/assets/'+name)
    assert image.get('loading') == 'lazy' and image.get('decoding') == 'async'
    assert image.get('alt')
    links = [a for t,a in tags if t == 'a' and urlsplit(a.get('href', '')).path.endswith('/assets/'+name)]
    assert len(links) == 1 and links[0].get('target') == '_blank'
    assert 'noopener' in links[0].get('rel', '')
    asset = root/'dist/assets'/name
    digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
    assert parse_qs(urlsplit(image['src']).query) == {'v': [digest]}
    assert links[0]['href'] == image['src']
    with Image.open(asset) as im:
        assert im.format == 'WEBP'
        assert (int(image['width']), int(image['height'])) == im.size
        assert min(im.size) >= 768
        assert not im.getexif() and not any(k in im.info for k in ('exif','xmp'))
        assert getattr(im, 'n_frames', 1) == 1
    assert asset.stat().st_size < 800_000
# Each curated row pairs equal natural formats without stretching or cropping.
for left, right in zip(posters[::2], posters[1::2]):
    assert int(left['width']) * int(right['height']) == int(right['width']) * int(left['height'])
assert about.count('Paris, 2002') == 2  # caption and link label, only poster 01
assert '<section class="about-gallery"' not in (root/'dist/index.html').read_text()
css = (root/'dist/style.css').read_text()
assert '.about-poster-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))' in css
assert '@media(max-width:700px)' in css and '.about-poster-grid{gap:24px 12px}' in css
assert '.about-poster-grid{grid-template-columns:1fr' not in css
assert '.about-poster img{display:block;width:100%;height:auto}' in css
print(f'PASS gallery commented out; {len(manifest)} restorable uncropped About-only posters; asset sizes; alt/lazy dimensions; accessible enlarge links; responsive rules')
