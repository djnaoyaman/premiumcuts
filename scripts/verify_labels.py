"""Keep equivalent catalog labels consistent without touching music membership."""
from pathlib import Path
import html, json, re

P = Path(__file__).resolve().parents[1]
catalog = json.loads((P / 'dist/catalog-public.json').read_text())
volumes = {v['id']: v for v in catalog['volumes']}
index = (P / 'dist/all-tracks.html').read_text()
songs = (P / 'dist/tracks.html').read_text()
index_tags = re.findall(r'<a class="volume-tag"[^>]*>(.*?)</a>', index)
songs_tags = re.findall(r'<a class="volume-tag"[^>]*>(.*?)</a>', songs)
assert len(index_tags) == len(songs_tags) == 675
assert index_tags == songs_tags, 'The same work must use the same public label in both indexes'
for tag, track in zip(index_tags, catalog['tracks']):
    assert html.unescape(tag).startswith(volumes[track['volume']]['display_code'] + ' / ')

css = (P / 'src/style.css').read_text()
shared = 'body .essential-badge,body .volume-tag,body .mix-marker'
rule = re.search(re.escape(shared) + r'\{([^}]+)\}', css).group(1)
for declaration in ['display:inline-flex', 'align-items:center', 'min-height:28px', 'padding:5px 8px', 'border:1px solid currentColor', 'border-radius:0', 'font-size:10px', 'line-height:1.4', 'overflow-wrap:anywhere']:
    assert declaration in rule, declaration
assert shared + '{font-size:9px}' in css
assert '.catalog-meta>.essential-badge{font-size:7px' not in css
assert '.volume-tag{max-width:100px' not in css
assert '.all-category .catalog-row{grid-template-columns:minmax(0,1fr)}' in css
assert '--paper:#f2e8d7;--blue:#126887' in css
print('PASS 675 identical public work labels; common square geometry, narrow layout, original palette')
