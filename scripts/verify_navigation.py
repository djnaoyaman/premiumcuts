"""Generated navigation semantics and responsive CSS scope regressions."""
from pathlib import Path
import html, json, re

P = Path(__file__).resolve().parents[1]
D = P / 'dist'
checked = 0
for page in D.rglob('*.html'):
    markup = page.read_text()
    main = re.search(r'<main\b.*?</main>', markup, re.S).group()
    crumbs = re.findall(r'<nav class="breadcrumb" aria-label="パンくず">(.*?)</nav>', main)
    assert len(crumbs) == (0 if page.name == 'index.html' else 1), page
    if not crumbs:
        continue
    crumb = crumbs[0]
    assert crumb.startswith('<ol>') and crumb.endswith('</ol>'), page
    assert crumb.count('aria-current="page"') == 1, page
    parts = re.findall(r'<li>(.*?)</li>', crumb)
    names = []
    for index, part in enumerate(parts):
        assert ('class="breadcrumb-separator" aria-hidden="true"' in part) == bool(index), page
        part = re.sub(r'<span class="breadcrumb-separator".*?</span>', '', part)
        names.append(html.unescape(re.sub(r'<[^>]+>', '', part)))
    assert names[0] == 'HOME' and len(names) >= 2, page
    assert 'aria-current="page"' in parts[-1] and '<a ' not in parts[-1], page
    if page.name != '404.html':
        graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', markup).group(1))['@graph']
        assert names == [p['name'] for p in graph[2]['itemListElement']], page
    checked += 1

def current(relative):
    return html.unescape(re.search(r'<span[^>]*aria-current="page">(.*?)</span>', (D / relative).read_text()).group(1))

for relative, name in [('tracks.html', 'Songs'), ('my-spin.html', 'Spinout'), ('features/essentials.html', 'Essentials'), ('about.html', 'About'), ('all-tracks.html', 'すべての曲'), ('404.html', '404')]:
    assert current(relative) == name, relative
assert current('tracks/001-a-03.html') == 'Tant de nuits (Bitter Sweet Samba)'
assert current('tracks/myspin-cliff-richard-one-note-samba.html') == 'One Note Samba'
assert 'id="catalog-breadcrumb-current" aria-current="page"' in (D / 'tracks.html').read_text()
assert 'class="selected"' not in (D / '404.html').read_text().split('</header>')[0]

css = (P / 'src/style.css').read_text()
selectors = re.findall(r'(?:^|[{}])\s*([^{}]+)\{', css)
for group in selectors:
    for selector in group.split(','):
        assert not re.match(r'^nav(?:\b|[>:])', selector.strip()), selector
assert '.volume-pagination,.song-pagination{display:flex' in css
assert 'header nav>a:last-child{display:inline-flex}' in css
assert '.breadcrumb ol{display:flex;flex-wrap:wrap;align-items:baseline' in css
assert 'overflow-wrap:anywhere' in css
print(f'PASS {checked} common breadcrumbs, current-page semantics, JSON-LD parity, responsive navigation scope')

# Spinout is a display-only rename, between Remix and About on every page.
expected_nav = ['Works', 'Songs', 'Essentials', 'Remix', 'Spinout', 'About']
for page in D.rglob('*.html'):
    markup = page.read_text()
    nav = re.search(r'<nav aria-label="メインナビゲーション">(.*?)</nav>', markup).group(1)
    links = re.findall(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', nav)
    assert [text for url, text in links] == expected_nav, page
    assert links[4][0] == '/premiumcuts/my-spin.html', page
spin = (D / 'my-spin.html').read_text()
assert '<h1>Spinout.</h1>' in spin
assert '<option value="myspin">Spinout</option>' in (D / 'player.html').read_text()
catalog = json.loads((D / 'catalog-public.json').read_text())
assert len(catalog['myspin']) == 11
for track in catalog['myspin']:
    assert track['id'].startswith('myspin-')
    markup = (D / 'tracks' / (track['id'] + '.html')).read_text()
    assert 'data-play-scope="myspin"' in markup and 'Spinoutへ戻る' in markup
print('PASS all-page navigation order and Spinout label; legacy URLs, 11 IDs and player scope retained')

assert 'const PREMIUM_MYSPIN=' in (D / 'data.js').read_text()
assert 'PREMIUM_MYSPINOUT' not in (D / 'data.js').read_text()
