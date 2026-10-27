"""Static, public-only metadata enrichment. No catalog or playback mutations."""
from pathlib import Path
from html.parser import HTMLParser
import html,json,re
from PIL import Image,ImageDraw,ImageFont

class Crumbs(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.href=None
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href')
 def handle_endtag(self,tag):
  if tag=='a':self.href=None
 def handle_data(self,data):
  for text in ([data] if self.href else data.split(' / ')):
   text=text.strip(' /\n')
   if text:self.parts.append((text,self.href))

def enrich(dist,origin,base_path):
 esc=html.escape
 # Keep the existing social-card composition, palette and information density;
 # render its headline with the site's actual DM Serif Display, never stretch text.
 font=Path(__file__).parent/'src/fonts/DMSerifDisplay-Regular.ttf'
 im=Image.new('RGB',(1200,630),'#f2e8d7');d=ImageDraw.Draw(im)
 d.line((50,65,1150,65),fill='#126887',width=2)
 for xy,text,size in [((60,120),'Premium',100),((60,240),'Cuts Listed.',92),((65,520),'THE PREMIUM CUTS ARCHIVE / TAPES + MIX CDS',23)]:
  d.text(xy,text,font=ImageFont.truetype(str(font if size>30 else font.parent/'DMSans.ttf'),size),fill='#126887')
 for x in range(810,1140,40):d.rectangle((x,115,x+18,460),fill='#126887')
 im.save(dist/'og.png')
 icon=Image.open(dist/'apple-touch-icon.png')
 for size in [32,48,192,512]:icon.resize((size,size),Image.Resampling.LANCZOS).save(dist/f'icon-{size}.png')
 icon.save(dist/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
 (dist/'site.webmanifest').write_text(json.dumps({'name':'Premium Cuts Listed','short_name':'Premium Cuts','lang':'ja','start_url':base_path+'/','scope':base_path+'/','display':'browser','background_color':'#f2e8d7','theme_color':'#f2e8d7','icons':[{'src':base_path+f'/icon-{s}.png','sizes':f'{s}x{s}','type':'image/png','purpose':'any'} for s in [192,512]]},ensure_ascii=False),encoding='utf-8')
 pages=list(dist.rglob('*.html'))
 for page in pages:
  s=page.read_text().replace('rel="apple-touch-icon"','rel="apple-touch-icon" sizes="180x180"');rel='/'+page.relative_to(dist).as_posix();url=origin+('/' if rel=='/index.html' else rel)
  title=html.unescape(re.search(r'<title>(.*?)</title>',s).group(1))
  desc=html.unescape(re.search(r'<meta name="description" content="([^"]*)"',s).group(1))
  label=title.split(' | ')[0]
  if rel=='/tracks.html':label='Songs'
  elif rel=='/my-spin.html':label='Spin'
  elif rel=='/features/essentials.html':label='Essentials'
  crumbs=[]
  if rel!='/index.html':
   match=re.search(r'<div class="breadcrumb">(.*?)</div>',s)
   if match:
    body=match.group(1)
    if not re.search(r'>HOME</a>',body):body=f'<a href="{base_path}/">HOME</a> / '+body
    s=s[:match.start()]+f'<div class="breadcrumb">{body}</div>'+s[match.end():]
   else:
    body=f'<a href="{base_path}/">HOME</a> / {esc(label)}'
    s=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+f'<div class="breadcrumb">{body}</div>',s,count=1)
   parser=Crumbs();parser.feed(body)
   for i,(name,href) in enumerate(parser.parts,1):
    item=url if not href else (origin+href[len(base_path):] if base_path and href.startswith(base_path+'/') else origin+href)
    crumbs.append({'@type':'ListItem','position':i,'name':name,'item':item})
  graph=[{'@type':'WebSite','@id':origin+'/#website','url':origin+'/','name':'Premium Cuts Listed','inLanguage':'ja'}, {'@type':'WebPage','@id':url+'#webpage','url':url,'name':title,'description':desc,'inLanguage':'ja','isPartOf':{'@id':origin+'/#website'}}]
  if crumbs:graph.append({'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':crumbs});graph[1]['breadcrumb']={'@id':url+'#breadcrumb'}
  extra=f'''<meta property="og:site_name" content="Premium Cuts Listed"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/png"><meta property="og:image:alt" content="Premium Cuts Listed — ブルーとクリーム色のアーカイブロゴ"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{origin}/og.png"><meta name="twitter:image:alt" content="Premium Cuts Listed — ブルーとクリーム色のアーカイブロゴ"><link rel="icon" href="{base_path}/icon-32.png" type="image/png" sizes="32x32"><link rel="icon" href="{base_path}/icon-48.png" type="image/png" sizes="48x48"><link rel="manifest" href="{base_path}/site.webmanifest"><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')}</script>'''
  s=s.replace('</head>',extra+'</head>');page.write_text(s,encoding='utf-8')
 # Real HTTP 404 on GitHub Pages, not a soft-404 redirect; no indexing or sitemap entry.
 s=(dist/'tracks.html').read_text()
 s=re.sub(r'<main\b.*?</main>',f'<main id="main" class="wrap about-page"><div class="breadcrumb"><a href="{base_path}/">HOME</a> / 404</div><h1>この棚には、<br><i>見つかりませんでした。</i></h1><p>ページが移動したか、URLが間違っているようです。</p><p><a class="text-link" href="{base_path}/tracks.html">Songsから探す ↗</a></p></main>',s,flags=re.S)
 s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s)
 s=re.sub(r'<title>.*?</title>','<title>ページが見つかりません | Premium Cuts Listed</title>',s)
 s=re.sub(r'<link rel="canonical"[^>]*>','',s)
 s=re.sub(r'<meta (?:property|name)="(?:og:title|twitter:title)"[^>]*>',lambda m:re.sub(r'content="[^"]*"','content="ページが見つかりません | Premium Cuts Listed"',m.group(0)),s)
 s=re.sub(r'<meta (?:property|name)="(?:description|og:description|twitter:description)"[^>]*>',lambda m:re.sub(r'content="[^"]*"','content="ページが移動したか、URLが間違っているようです。Songsから探してください。"',m.group(0)),s)
 s=re.sub(r'<meta property="og:url"[^>]*>',f'<meta property="og:url" content="{origin}/404.html">',s)
 s=s.replace('</head>','<meta name="robots" content="noindex"></head>')
 (dist/'404.html').write_text(s,encoding='utf-8')
 (dist/'llms.txt').write_text(f'''# Premium Cuts Listed\n\nPublic music-track archive and listening guide. This file is a navigation aid, not a ranking or indexing guarantee.\n\n- [About]({origin}/about.html): scope and editorial background.\n- [Songs]({origin}/tracks.html): original Premium Cuts track placements, in published order.\n- [Essentials]({origin}/features/essentials.html): the owner's explicitly selected subset of Songs.\n- [Spin]({origin}/my-spin.html): an independent derived selection, not original Premium Cuts contents.\n- [All tracks]({origin}/all-tracks.html): category-separated public index.\n- [Sitemap]({origin}/sitemap.xml): canonical public pages.\n\nTrack pages distinguish verified release information, references, interpretation and unresolved information. Read their cited sources and uncertainty notes. Embedded YouTube availability varies; the archive does not host the recordings. Query filters are views of Songs, not separate releases.\n''',encoding='utf-8')
