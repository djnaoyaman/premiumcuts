"""Static, public-only metadata enrichment. No catalog or playback mutations."""
from pathlib import Path
import html,json,re,hashlib,shutil
from PIL import Image

def breadcrumb_markup(parts,current_id=''):
 """One accessible breadcrumb component for every generated page."""
 items=[]
 for i,(name,href) in enumerate(parts):
  separator='<span class="breadcrumb-separator" aria-hidden="true">/</span>' if i else ''
  if href:
   content=f'<a href="{html.escape(href,quote=True)}">{html.escape(name)}</a>'
  else:
   current_attr=f' id="{html.escape(current_id,quote=True)}"' if current_id else ''
   content=f'<span{current_attr} aria-current="page">{html.escape(name)}</span>'
  items.append(f'<li>{separator}{content}</li>')
 return '<nav class="breadcrumb" aria-label="パンくず"><ol>'+''.join(items)+'</ol></nav>'


def page_breadcrumbs(rel,label,catalog,base_path):
 home=('HOME',base_path+'/')
 labels={'/tracks.html':'Songs','/my-spin.html':'Spinout','/features/essentials.html':'Essentials','/all-tracks.html':'すべての曲','/about.html':'About','/player.html':'Player'}
 if rel in labels:return [home,(labels[rel],None)]
 volumes={v['id']:v for v in catalog['volumes']}
 if rel.startswith('/volumes/'):
  v=volumes.get(Path(rel).stem)
  if v:return [home,('Works',base_path+'/#collection'),(v['display_code']+' '+v['title'],None)]
 if rel.startswith('/tracks/'):
  tid=Path(rel).stem
  spin=next((t for t in catalog['myspin'] if t['id']==tid),None)
  if spin:return [home,('Spinout',base_path+'/my-spin.html'),(spin['title'],None)]
  t=next((t for t in catalog['tracks'] if t['id']==tid),None)
  if t:
   v=volumes[t['volume']]
   return [home,('Songs',base_path+'/tracks.html'),(v['display_code']+' '+v['title'],base_path+'/volumes/'+v['id']+'.html'),(t['title'],None)]
 return [home,(label,None)]

def enrich(dist,origin,base_path):
 esc=html.escape
 # Social images are literal crops of the generated page, rendered after this build.
 # Changing page content, styles or the renderer changes the public image URL.
 social_dir=dist/'social'
 if social_dir.exists():shutil.rmtree(social_dir)
 social_dir.mkdir()
 (dist/'og.png').unlink(missing_ok=True)
 render_source=(Path(__file__).parent/'scripts/render_social_cards.py').read_bytes()
 style_source=(dist/'style.css').read_bytes()+(dist/'player.css').read_bytes()
 cards=[]
 def social_image(page,markup,title):
  rel=page.relative_to(dist).as_posix()
  digest=hashlib.sha256(markup.encode()+style_source+render_source).hexdigest()[:16]
  image='social/'+Path(rel).with_suffix('').as_posix()+'-'+digest+'.png'
  alt=title+' — ページの書体・配色・レイアウトをそのまま写したプレビュー'
  cards.append({'page':rel,'image':image,'alt':alt})
  return origin+'/'+image,alt
 icon=Image.open(dist/'apple-touch-icon.png')
 for size in [32,48,192,512]:icon.resize((size,size),Image.Resampling.LANCZOS).save(dist/f'icon-{size}.png')
 icon.save(dist/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
 (dist/'site.webmanifest').write_text(json.dumps({'name':'Premium Cuts Listed','short_name':'Premium Cuts','lang':'ja','start_url':base_path+'/','scope':base_path+'/','display':'browser','background_color':'#f2e8d7','theme_color':'#f2e8d7','icons':[{'src':base_path+f'/icon-{s}.png','sizes':f'{s}x{s}','type':'image/png','purpose':'any'} for s in [192,512]]},ensure_ascii=False),encoding='utf-8')
 catalog=json.loads((dist/'catalog-public.json').read_text())
 pages=sorted(p for p in dist.rglob('*.html') if p.name!='404.html')
 for page in pages:
  s=page.read_text().replace('rel="apple-touch-icon"','rel="apple-touch-icon" sizes="180x180"');rel='/'+page.relative_to(dist).as_posix();url=origin+('/' if rel=='/index.html' else rel)
  title=html.unescape(re.search(r'<title>(.*?)</title>',s).group(1))
  desc=html.unescape(re.search(r'<meta name="description" content="([^"]*)"',s).group(1))
  image_url,image_alt=social_image(page,s,title)
  s=re.sub(r'<meta property="og:image"[^>]*>',f'<meta property="og:image" content="{image_url}">',s)
  label=title.split(' | ')[0]
  if rel=='/tracks.html':label='Songs'
  elif rel=='/my-spin.html':label='Spinout'
  elif rel=='/features/essentials.html':label='Essentials'
  crumbs=[]
  if rel!='/index.html':
   parts=page_breadcrumbs(rel,label,catalog,base_path)
   markup=breadcrumb_markup(parts,'catalog-breadcrumb-current' if rel=='/tracks.html' else '')
   match=re.search(r'<(?P<tag>div|nav)\b(?P<attrs>[^>]*\bclass="[^"]*\bbreadcrumb\b[^"]*"[^>]*)>(?P<body>.*?)</(?P=tag)>',s)
   if match:s=s[:match.start()]+markup+s[match.end():]
   else:s=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+markup,s,count=1)
   for i,(name,href) in enumerate(parts,1):
    item=url if not href else (origin+href[len(base_path):] if base_path and href.startswith(base_path+'/') else origin+href)
    crumbs.append({'@type':'ListItem','position':i,'name':name,'item':item})
  graph=[{'@type':'WebSite','@id':origin+'/#website','url':origin+'/','name':'Premium Cuts Listed','inLanguage':'ja'}, {'@type':'WebPage','@id':url+'#webpage','url':url,'name':title,'description':desc,'inLanguage':'ja','isPartOf':{'@id':origin+'/#website'}}]
  if crumbs:graph.append({'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':crumbs});graph[1]['breadcrumb']={'@id':url+'#breadcrumb'}
  extra=f'''<meta property="og:site_name" content="Premium Cuts Listed"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/png"><meta property="og:image:alt" content="{esc(image_alt)}"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{image_url}"><meta name="twitter:image:alt" content="{esc(image_alt)}"><link rel="icon" href="{base_path}/icon-32.png" type="image/png" sizes="32x32"><link rel="icon" href="{base_path}/icon-48.png" type="image/png" sizes="48x48"><link rel="manifest" href="{base_path}/site.webmanifest"><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')}</script>'''
  s=s.replace('</head>',extra+'</head>');page.write_text(s,encoding='utf-8')
 # Real HTTP 404 on GitHub Pages, not a soft-404 redirect; no indexing or sitemap entry.
 s=(dist/'tracks.html').read_text()
 not_found_crumb=breadcrumb_markup([('HOME',base_path+'/'),('404',None)])
 s=re.sub(r'<main\b.*?</main>',f'<main id="main" class="wrap about-page">{not_found_crumb}<h1>この棚には、<br><i>見つかりませんでした。</i></h1><p>ページが移動したか、URLが間違っているようです。</p><p><a class="text-link" href="{base_path}/tracks.html">Songsから探す ↗</a></p></main>',s,flags=re.S)
 s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s)
 s=re.sub(r'<title>.*?</title>','<title>ページが見つかりません | Premium Cuts Listed</title>',s)
 s=re.sub(r'<link rel="canonical"[^>]*>','',s)
 s=re.sub(r'<meta (?:property|name)="(?:og:title|twitter:title)"[^>]*>',lambda m:re.sub(r'content="[^"]*"','content="ページが見つかりません | Premium Cuts Listed"',m.group(0)),s)
 s=re.sub(r'<meta (?:property|name)="(?:description|og:description|twitter:description)"[^>]*>',lambda m:re.sub(r'content="[^"]*"','content="ページが移動したか、URLが間違っているようです。Songsから探してください。"',m.group(0)),s)
 s=re.sub(r'<meta property="og:url"[^>]*>',f'<meta property="og:url" content="{origin}/404.html">',s)
 s=s.replace('class="selected"','class=""')
 s=s.replace('</head>','<meta name="robots" content="noindex"></head>')
 image_url,image_alt=social_image(dist/'404.html',s,'ページが見つかりません | Premium Cuts Listed')
 for key in ('og:image','twitter:image'):
  s=re.sub(r'(<meta (?:property|name)="'+key+r'" content=")[^"]*',lambda m:m[1]+image_url,s)
 for key in ('og:image:alt','twitter:image:alt'):
  s=re.sub(r'(<meta (?:property|name)="'+key+r'" content=")[^"]*',lambda m:m[1]+esc(image_alt),s)
 (dist/'404.html').write_text(s,encoding='utf-8')
 (dist/'social-card-manifest.json').write_text(json.dumps({'schema':1,'width':1200,'height':630,'pages':cards},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (dist/'llms.txt').write_text(f'''# Premium Cuts Listed\n\nPublic music-track archive and listening guide. This file is a navigation aid, not a ranking or indexing guarantee.\n\n- [About]({origin}/about.html): scope and editorial background.\n- [Songs]({origin}/tracks.html): original Premium Cuts track placements, in published order.\n- [Essentials]({origin}/features/essentials.html): the owner's explicitly selected subset of Songs.\n- [Spinout]({origin}/my-spin.html): an independent derived selection, not original Premium Cuts contents.\n- [All tracks]({origin}/all-tracks.html): category-separated public index.\n- [Sitemap]({origin}/sitemap.xml): canonical public pages.\n\nTrack pages distinguish verified release information, references, interpretation and unresolved information. Read their cited sources and uncertainty notes. Embedded YouTube availability varies; the archive does not host the recordings. Query filters are views of Songs, not separate releases.\n''',encoding='utf-8')
