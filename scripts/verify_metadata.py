from pathlib import Path
from html.parser import HTMLParser
import json,re,sys,hashlib,xml.etree.ElementTree as ET
from PIL import Image
D=Path(__file__).resolve().parents[1]/'dist'
origin='https://djnaoyaman.github.io/premiumcuts'
structure_only='--structure-only' in sys.argv
manifest=json.loads((D/'social-card-manifest.json').read_text())
cards={c['page']:c for c in manifest['pages']}
assert (manifest['width'],manifest['height'])==(1200,630)
assert len(cards)==len(manifest['pages'])
assert len({c['image'] for c in cards.values()})==len(cards)
class Head(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='meta':self.meta[a.get('property',a.get('name'))]=a.get('content')
  if t=='link':self.links.append(a)
count=0
for p in D.rglob('*.html'):
 s=p.read_text();h=Head();h.feed(s);count+=1
 assert len(re.findall('<h1(?: |>)',s))==1,p
 card=cards[p.relative_to(D).as_posix()]
 assert re.fullmatch(r'social/(?:[a-z0-9-]+/)*[a-z0-9-]+-[a-f0-9]{16}\.png',card['image']),card
 assert h.meta['og:image']==h.meta['twitter:image']==origin+'/'+card['image'],p
 assert h.meta['og:image:alt']==h.meta['twitter:image:alt']==card['alt'],p
 assert h.meta['og:image:width']=='1200' and h.meta['og:image:height']=='630',p
 assert h.meta['og:image:type']=='image/png',p
 if not structure_only:
  image=D/card['image'];assert image.exists(),image
  assert Image.open(image).size==(1200,630),image
  assert 1000<image.stat().st_size<5_000_000,image
 if p.name=='404.html':assert h.meta['robots']=='noindex';continue
 canonical=[x['href'] for x in h.links if x.get('rel')=='canonical'];assert len(canonical)==1,p
 assert len(re.findall(r'<(?:nav|div)\b[^>]*class="[^"]*\bbreadcrumb\b[^"]*"',s))==(0 if p.name=='index.html' else 1),p
 expected=origin+('/' if p.name=='index.html' else '/'+p.relative_to(D).as_posix())
 assert canonical[0]==expected,(p,canonical)
 assert h.meta['og:url']==expected,p
 for k in ['description','og:title','og:description','og:image','og:image:alt','twitter:title','twitter:description','twitter:image','twitter:image:alt']:assert h.meta.get(k),(p,k)
 assert h.meta['twitter:card']=='summary_large_image'
 for x in h.links:
  if x.get('rel') in ['icon','apple-touch-icon','manifest']:
   u=x['href'];assert u.startswith('/premiumcuts/'),(p,u);assert (D/u.removeprefix('/premiumcuts/')).exists(),u
 graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s).group(1))['@graph']
 assert graph[1]['url']==expected
 if p.name!='index.html':assert graph[2]['@type']=='BreadcrumbList' and graph[2]['itemListElement'][-1]['item']==expected,p
 assert 'mossyelf' not in s,p
urls=[x.text for x in ET.parse(D/'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls)==len(set(urls))==count-1
assert all('404.html' not in x and '?' not in x and x.startswith(origin+'/') for x in urls)
assert count==len(cards)
if not structure_only:
 assert Image.open(D/'og.png').size==(1200,630)
 report=json.loads((D/'social-card-report.json').read_text())
 assert {c['page'] for c in report['pages']}==set(cards)
 for c in report['pages']:
  assert c['headingInside'],c
  assert c['fontsLoaded'] and c['capture']['width']==1200 and c['capture']['height']==630,c
  assert c['heading']['color']=='rgb(18, 104, 135)',c
  assert c['heading']['background']=='rgb(242, 232, 215)',c
  assert c['sha256']==hashlib.sha256((D/c['image']).read_bytes()).hexdigest(),c
 home=cards['index.html']['image']
 assert (D/'og.png').read_bytes()==(D/home).read_bytes()
assert Image.open(D/'apple-touch-icon.png').size==(180,180)
print(f'{count} pages: metadata, breadcrumbs, canonical, assets, sitemap PASS; '+('rendered image checks NOT RUN (--structure-only)' if structure_only else 'all page-specific image dimensions, hashes, fonts and palette PASS'))
