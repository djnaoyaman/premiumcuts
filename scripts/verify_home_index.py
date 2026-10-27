"""Owner-directed homepage and all-site index without altering catalog scope."""
from pathlib import Path
from html.parser import HTMLParser
import json
p=Path(__file__).resolve().parents[1]
c=json.loads((p/'dist/catalog-public.json').read_text());home=(p/'dist/index.html').read_text().replace('/premiumcuts/','/');allpage=(p/'dist/all-tracks.html').read_text();my=(p/'dist/my-spin.html').read_text()
assert 'テープから、<i>ひらく。</i>' in home and 'CDから、<i>ひらく。</i>' in home
assert home.index('class="collection wrap"')<home.index('class="essentials-teaser wrap"')<home.index('class="about-strip wrap"')
assert '個人制作の収録曲アーカイブ' not in home
assert 'Selection &amp; mix by' not in home # Existing displayed wording uses literal Selection & mix.
assert 'Selection & mix by Masanori Suzuki &amp; Me' in home
assert 'DJ Naoyaman が世界中を巡りコレクト。' in my
n=len(c['tracks'])+len(c['myspin']);assert f'<span class="index-number">{n}<small>' in home and f'<strong>{n} 曲目</strong>' in allpage
assert 'class="index-card songs-index" href="/all-tracks.html"' in home
assert all(f'id="{g}"' in allpage for g in ['songs-tape','songs-cd','my-spin'])
assert all('/tracks/'+t['id']+'.html' in allpage for t in c['tracks']+c['myspin'])
assert all('data-play-scope="myspin"' in row for row in allpage.split('class="essential-cut"')[1:])
assert 'data-play-scope="all"' not in allpage # No mixed all-site autoplay queue.
# Every generated source occurrence stays in the categorized index exactly once.
class Counter(HTMLParser):
 def __init__(self):super().__init__();self.rows=0
 def handle_starttag(self,tag,attrs):
  if tag=='li' and dict(attrs).get('class') in ['catalog-row','essential-cut']:self.rows+=1
x=Counter();x.feed(allpage);assert x.rows==n
print(f'PASS homepage hierarchy/copy; {n} categorized entries; no Essentials double count or mixed playback queue')

songs=(p/'dist/tracks.html').read_text()
assert '<h1>Premium Cuts<br><i>Songs</i></h1>' in songs
assert '<section class="essentials-heading songs-heading">' in songs
assert '<p class="song-lead">Premium Cutsすべての曲を、<em>ひとつの棚に。</em></p><p>ジャズ、ブラジル、フレンチ・ポップ。<br>こちらの世界もとてもひろかった。</p>' in songs

css=(p/'src/style.css').read_text()
assert '.essentials-teaser{background:#f08080;color:#10394a;' in css
assert 'text-align:right;justify-items:end' in css
assert '.essentials-teaser a:focus-visible{outline-color:currentColor}' in css

assert "background:var(--blue);color:var(--paper);min-height:300px" in css
assert ".songs-index>strong{font:500 21px/1.65 var(--sans)" in css
assert "class=\"index-card songs-index\"" in home
