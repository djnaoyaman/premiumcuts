from pathlib import Path
import json,html,re,shutil,unicodedata,collections,os,hashlib
from urllib.parse import quote
from PIL import Image,ImageDraw,ImageFont
from catalog_style import normalize_tracks
from artwork import record_art
P=Path(__file__).parent;D=P/'dist';e=html.escape
origin=os.environ.get('SITE_ORIGIN','https://premium-cuts-listed.mossyelf3.chatgpt.site').rstrip('/')
base_path=os.environ.get('BASE_PATH','').rstrip('/')
titles=['ON THE AIR','SINCERELY','COMMERCIALS','AUDIOSCAPE','JINGLES','COUNSELING','HOLIDAY MUSIC']
subtitles=['ラジオの向こうで、音楽に出会う。','一曲ずつ、気持ちをつないで。','日常の隙間に、小さな音楽を。','音が描く、もうひとつの風景。','短い合図から、次の曲へ。','気分に寄り添う、レコードの時間。','休日には、少し遠くの音楽を。']
# Editorial taglines describe the archive experience, not the mix creator's stated intent.
for path in ['tracks','volumes','features','assets']: (D/path).mkdir(parents=True,exist_ok=True)
# Replace the superseded, out-of-scope catalog completely.
for f in (D/'tracks').glob('*.html'):f.unlink()
for n in ['style.css','app.js','player.css','player.js']:shutil.copy2(P/'src'/n,D/n)
for asset in (D/'assets').glob('source-*.jpg'):asset.unlink()
corrections={
 ('001','A',10):('Karen Wyman',None,'KALEN WYMAN / NIGHT AND DAY','アーティスト名をKaren Wymanに修正。','https://www.stereo-records.com/detail.php?itemCd=12831'),
 ('001','A',14):(None,'Tuxedo Junction','THE LEADING FIGURES / TUXEDE JUNCTION','曲名をTuxedo Junctionに修正。','https://www.whosampled.com/The-Leading-Figures/covers/'),
 ('002','A',1):('The Peddlers','Irresistible You','PEDDRERS / IRRESISTABLE YOU','アーティスト名と曲名の綴りを修正。','https://www.originals.be/en/originals/9658'),
 ('002','B',11):('Erlon Chaves',None,'EARLON CHAVES / TESTAMENTO','アーティスト名をErlon Chavesに修正。','https://music.apple.com/gb/artist/erlon-chaves/1364970971'),
 ('002','B',13):('Trio Esperança','A Feiticeirinha (Georgy Girl)','TRIO ESPERANCA / GEOGY GIRL','GeogyをGeorgyに修正。ブラジルでの曲名も併記。','https://immub.org/album/bis-jovem-guarda-trio-esperanca'),
 ('003','B',1):('Yehudit Ravitz',None,'JUDIS RAVITZ / TAJ MAHAL','アーティスト名をディスコグラフィーの表記に修正。','https://stereo-ve-mono.com/40707'),
 ('004','B',3):('Łucja Prus',None,'LUCJA PRUS / GLUPI ALBO GRA','アーティスト名・曲名にポーランド語の文字を復元。','https://bibliotekapiosenki.pl/albumy/Prus_Lucja_Lucja_Prus_Wifon_1981/utwory'),
 ('005','B',1):('Lena Horne',None,'RENA HORNE / IT HAD BETTER BE TONIGHT','アーティスト名をLena Horneに修正。','https://music.apple.com/us/song/712244869'),
 ('005','B',13):('Marlene VerPlanck',None,'MARLENE VER PLANCK / MISSION IMPOSSIBLES','アーティスト名をMarlene VerPlanck、曲名をMission: Impossibleに修正。','https://s5da5ef0c5a91241a.jimcontent.com/download/version/1762794556/module/12340829021/name/20250317_Findbuch%20Sammlung%20Hazy%20Osterwald_LRA%20109.pdf'),
 ('006','A',5):('Alma Cogan',None,'ALMA KOGAN / I FEEL FINE','アーティスト名をAlma Coganに修正。','https://music.apple.com/us/song/695968643'),
 ('007','B',6):(None,'Montreal East','NICK AYOUB / MONTRIAL EAST','曲名をMontreal Eastに修正。','https://citizenfreak.com/titles/266017-ayoub-nick-quintet-the-montreal-scene'),
 ('007','B',1):('Serge Gainsbourg','Comment trouvez-vous ma sœur?','S. GAINSBOURG / COMMENT TROUVEZ-VOUZ MA SEUR?','アーティストの略記を展開し、フランス語の綴りを整形。',None),
}
# Ambiguous readings stay explicit. No silent identification from a similar name.
pending={key:'アーティスト・曲名・収録版を確認中。' for key in [('001', 'A', 11), ('001', 'A', 15), ('001', 'B', 4), ('001', 'B', 1), ('003', 'B', 2), ('005', 'A', 3), ('005', 'A', 13), ('005', 'B', 4), ('005', 'B', 5), ('006', 'A', 11), ('006', 'B', 6), ('006', 'B', 11), ('006', 'B', 15), ('007', 'A', 7), ('007', 'B', 5), ('007', 'B', 13)]}
# Fix key positions after explicit source position checks.
# Montreal East is side B 5, not 6 (Hawksworth is 4).
corrections[('007','B',5)]=corrections.pop(('007','B',6));pending.pop(('007','B',5))
counts=collections.defaultdict(int);tracks=[]
for line in (P/'selection.tsv').read_text().splitlines():
 v,side,artist,title=line.split('\t');counts[(v,side)]+=1;n=counts[(v,side)];key=(v,side,n)
 raw=artist.upper()+' / '+title.upper();note=None;source=None;status='transcribed'
 if key in corrections:
  a,t,raw,note,source=corrections[key];artist=a or artist;title=t or title;status='corrected'
 if key==('005','B',13): title='Mission: Impossible'
 if key==('001','A',15):artist='The Lipstics';title='Bim Ba Ba Bi Baaa'
 if key==('001','B',4):artist='Via Szbaba'
 if key in pending:note=pending[key];status='pending'
 if key==('003','A',5):raw='MARJU KUIT / MARTSIS MAI';artist='Marju Kuut';note='アーティストの綴りをMarju Kuutに修正。曲の歌唱名義・版は要照合。';source='https://www.jazzkaar.ee/jazzkaar-lopetab-kevadhooaja-marju-kuudiga/';status='pending'
 tracks.append(dict(id=f'{v}-{side.lower()}-{n:02}',volume=v,side=side,position=n,artist=artist,title=title,original=raw,status=status,note=note,source=source))
volumes=[dict(id=f'{i:03}',title=t,tagline=subtitles[i-1],count=sum(x['volume']==f'{i:03}' for x in tracks),a=counts[(f'{i:03}','A')],b=counts[(f'{i:03}','B')]) for i,t in enumerate(titles,1)]
# The numbered mix-CD series is distinct from the three-digit cassette series.
for t in tracks:t['format']='tape'
for v in volumes:
 v.update(format='tape',display_code='TAPE '+v['id'],pattern=int(v['id']))
tape_volumes=volumes.copy()
cd_data=json.loads((P/'cd_catalog.json').read_text())
cd_volumes=cd_data['volumes']
for artwork_index,v in enumerate(cd_volumes,8):v['pattern']=artwork_index
volumes+=cd_volumes
tracks+=cd_data['tracks']
normalize_tracks(tracks)
research=json.loads((P/'research.json').read_text())
articles={tid:a for a in research['articles'] for tid in a['ids']}
track_by_id={t['id']:t for t in tracks}
players=dict(research.get('players',{}))
for a in research['articles']:
 if a.get('youtube'):
  for tid in a['ids']:players[tid]=a['youtube']


# Explicit recording sources supplied after the editorial research pass.
players.update(json.loads((P/'audio_sources.json').read_text()))

features=json.loads((P/'features.json').read_text())
essentials=features['essentials']
essential_tracks=[track_by_id[i] for i in essentials['track_ids']]
assert len(essential_tracks)==24 and len({players[t['id']]['id'] for t in essential_tracks})==24
essential_videos={players[t['id']]['id'] for t in essential_tracks}
for t in tracks:
 t['essentials']=t['id'] in players and players[t['id']]['id'] in essential_videos

def essential_badge(t):
 return '<a class="essential-badge" href="/features/essentials.html">ESSENTIALS ↗</a>' if t['essentials'] else ''

def position_label(t):
 return f"{t['side']}{t['position']:02}" if t['format']=='tape' else f"{t['side']} · {t['position']:02}"
def location_label(t):
 return f"Side {t['side']} · {t['position']:02}" if t['format']=='tape' else f"Disc {t['disc']} · {t['position']:02}"

# Interludes are not counted as named songs. Their original positions are retained.
marks={
 '001':{'A':{0:['intro — tuning'],12:['intermission — on the air 1']},'B':{0:['intermission — on the air 2'],13:['outro — off the air'],15:['chao']}},
 '002':{'A':{0:['intro'],16:['intermission']},'B':{11:['intermission'],17:['outro']}},
 '003':{'A':{0:['OPENING SHOW'],8:['COMMERCIAL'],14:['THE MIDDLE']},'B':{10:['COMMERCIAL'],17:['CLOSING SHOW']}},
 '004':{'A':{0:['BREAK 1']},'B':{0:['BREAK 2'],12:['BREAK 3'],15:['AUDIOSCAPE']}},
 '005':{'A':{0:['JINGLE 1'],9:['JINGLE 2'],17:['JINGLE 3']},'B':{0:['JINGLE 4'],6:['JINGLE 5'],16:['JINGLE 6']}},
 '006':{'A':{0:['counseling 1'],13:['counseling 2'],16:['counseling 3']},'B':{11:['counseling 4'],14:['counseling 5']}},
 '007':{'A':{0:['JINGLE'],8:['JINGLE'],17:['JINGLE']},'B':{4:['JINGLE'],13:['JINGLE']}}}
public_tracks=[{k:v for k,v in t.items() if k in {'id','volume','side','position','artist','title','format','disc','mix_marker','essentials'}} for t in tracks]
(D/'data.js').write_text('const TRACKS='+json.dumps(public_tracks,ensure_ascii=False)+';\nconst VOLUMES='+json.dumps(volumes,ensure_ascii=False)+';')
(D/'data.js').write_text((D/'data.js').read_text()+'\nconst PREMIUM_AUDIO='+json.dumps([dict(id=t['id'],volume=t['volume'],title=t['title'],artist=t['artist'],videoId=players[t['id']]['id'],url=players[t['id']]['url']) for t in tracks if t['id'] in players],ensure_ascii=False)+';')
(P/'catalog.json').write_text(json.dumps({'volumes':volumes,'tracks':public_tracks,'markers':marks},ensure_ascii=False,indent=2))
(P/'tracks.json').unlink(missing_ok=True)

def pattern(i,cls=''):
 return f'<div class="pattern bauhaus-art {cls}" data-art="{i}" aria-hidden="true">{record_art(i)}</div>'

asset_version=hashlib.sha256(''.join((P/n).read_text() for n in ['build.py','features.json','artwork.py','catalog_style.py','cd_catalog.json','research.json','audio_sources.json','src/app.js','src/player.js','src/player.css','src/style.css']).encode()).hexdigest()[:12]
# Public-only catalog snapshots let open players receive newly published sources.
public_audio=[dict(id=t['id'],volume=t['volume'],title=t['title'],artist=t['artist'],videoId=players[t['id']]['id'],url=players[t['id']]['url']) for t in tracks if t['id'] in players]
(D/'catalog-public.json').write_text(json.dumps(dict(version=asset_version,tracks=public_tracks,volumes=volumes,audio=public_audio),ensure_ascii=False))
(D/'version.json').write_text(json.dumps(dict(version=asset_version,audio_count=len({t['videoId'] for t in public_audio}))))
def head(title,desc,path='/'):
 return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{origin}{path}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{origin}{path}"><meta property="og:image" content="{origin}/og.png"><meta property="og:locale" content="ja_JP"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#f2e8d7"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="stylesheet" href="/style.css?v={asset_version}"><link rel="stylesheet" href="/player.css?v={asset_version}"><script defer src="/data.js?v={asset_version}"></script><script defer src="/app.js?v={asset_version}"></script><script defer src="/player.js?v={asset_version}"></script></head>'''
def header(active=''):
 return '<a class="skip" href="#main">本文へ</a><header><a class="brand" href="/"><span class="brand-mark" aria-hidden="true"><svg class="asterisk-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="M32 3v58M3 32h58M11.5 11.5l41 41M11.5 52.5l41-41" fill="none" stroke="currentColor" stroke-width="3"/></svg></span><span>Premium Cuts<br><b>Listed.</b></span></a><nav aria-label="メインナビゲーション">'+''.join(f'<a class="{"selected" if k==active else ""}" href="{u}">{n}</a>' for k,u,n in [('player','/player.html','PLAYER'),('volumes','/#collection','作品から探す'),('tracks','/tracks.html','すべての曲'),('essentials','/features/essentials.html','Essentials'),('about','/about.html','このサイトについて')])+'</nav><span class="header-meta">LES BONNES<br>VIBRATIONS.</span></header>'
def footer():return (P/'src/player-shell.html').read_text()+'<footer><a class="footer-logo" href="/">Premium Cuts Listed<span>Une collection de bonnes vibrations.</span></a><p>Selection & mix by Masanori Suzuki<br>個人制作の収録曲アーカイブ</p><a href="#top">ページの上へ ↑</a></footer>'
def tile(v):
 description='SIDE A + SIDE B' if v['format']=='tape' else ('2 DISCS' if len(v['discs'])>1 else 'TRACKLIST')
 return f'''<article class="volume-card"><a href="/volumes/{v['id']}.html">{pattern(v['pattern'])}<div class="card-meta"><span>PREMIUM CUTS</span><span>{v['display_code']}</span></div><h3>{e(v['title'])}<span>↗</span></h3><div class="card-bottom"><span>{description}</span><span>{v['count']} ENTRIES</span></div></a></article>'''
def row(t):
 badge=f'<span class="mix-marker">{e(t["mix_marker"])}</span>' if t.get('mix_marker') else ''
 play=f'<button type="button" class="pc-inline-play" data-play-id="{t["id"]}" data-play-scope="volume:{t["volume"]}" aria-label="{e(t["title"])}を再生">▶</button>' if t['id'] in players else ''
 return f'''<li class="track-row" data-id="{t['id']}"><span class="track-pos">{position_label(t)}</span><a class="track-main" href="/tracks/{t['id']}.html"><strong>{e(t['title'])}</strong><span>{e(t['artist'])}</span>{badge}</a>{essential_badge(t)}{play}<a class="row-arrow" href="/tracks/{t['id']}.html" aria-label="{e(t['title'])}の詳細">↗</a></li>'''
N=len(tracks)
home=head('Premium Cuts Listed — 一曲の先に、また一曲。','Masanori SuzukiのPremium Cuts。その収録曲だけを、作品と曲順からたどる音楽アーカイブ。')+'<body id="top">'+header('volumes')+f'''<main id="main"><section class="hero wrap"><div class="hero-top"><span class="eyebrow">THE PREMIUM CUTS ARCHIVE</span><span class="eyebrow">JAZZ, BRASIL, FRENCH & MANY MORE</span></div><div class="hero-content hero-type"><h1><span>Premium Cuts</span><i>Listed.</i></h1><div class="hero-type-footer"><p class="hero-jp">一曲の先に、<br>また一曲。</p><div><p class="hero-copy">鈴木雅尭の「Premium Cuts」で出会った音楽を。<br>作品を開き、曲順をたどり、好きな一曲を見つける。</p><a class="round-link" href="#collection">レコード棚をのぞく <span>↓</span></a></div></div></div><div class="hero-bottom"><span>MIXED BY MASANORI SUZUKI</span><span>07 TAPES + 15 MIX CDS &nbsp; / &nbsp; {N} ENTRIES</span></div></section><section class="essentials-teaser wrap"><div><span class="eyebrow">FEATURE 01 / SELECTED BY DJ NAOYAMAN</span><h2>Premium Cuts<br><i>Essentials.</i></h2><p>何度でも戻りたくなる、24の音源。<br>DJ Naoyamanが選ぶ、Premium Cutsの核。</p><a class="text-link" href="/features/essentials.html">特集をひらく ↗</a></div><a class="essentials-symbol" href="/features/essentials.html" aria-label="Premium Cuts Essentials 特集へ">{pattern(23)}<span>24 ESSENTIAL RECORDINGS ↗</span></a></section><section class="collection wrap" id="collection"><div class="section-heading"><div><span class="eyebrow">LA COLLECTION</span><h2>作品から、<i>ひらく。</i></h2></div><p>カセットとMIX CD。<br>番号が同じでも、別々の作品として。</p></div><div class="collection-label">MIX TAPES / 001—007</div><div class="volume-grid">'''+''.join(tile(v) for v in tape_volumes)+'''</div><div class="section-heading cd-section-heading"><div><span class="eyebrow">LES MIX CDS / #00—#14</span><h2>MIX CDから、<i>ひらく。</i></h2></div><p>カセットとは異なる15タイトル。<br>ディスクごとの曲順で。</p></div><div class="volume-grid">'''+''.join(tile(v) for v in cd_volumes)+f'''<a class="index-card" href="/tracks.html"><span class="eyebrow">INDEX DES MORCEAUX</span><strong>すべての曲を<br><i>ひとつの棚に。</i></strong><span class="index-number">{N}<small>曲目</small></span><span class="index-bottom">曲名・アーティストから探す <b>↗</b></span></a></div></section><section class="about-strip wrap"><span class="star" aria-hidden="true"><svg class="asterisk-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="M32 3v58M3 32h58M11.5 11.5l41 41M11.5 52.5l41-41" fill="none" stroke="currentColor" stroke-width="3"/></svg></span><div><span class="eyebrow">À PROPOS</span><h2>好きな音楽を、<br>ゆっくり、深く。</h2><p>この棚に並ぶのは「Premium Cuts」の収録曲だけ。<br>まずは曲目と曲順を。音楽の背景や映像は、一曲ずつ大切に。</p><a class="text-link" href="/about.html">このアーカイブについて ↗</a></div></section></main>'''+footer()+'</body></html>'
(D/'index.html').write_text(home)
for v in tape_volumes:
 vid=v['id'];i=int(vid)
 page=head('Premium Cuts '+vid+' '+v['title']+' | Premium Cuts Listed',f'Premium Cuts {vid} {v["title"]}の収録曲一覧。Side AとSide Bの曲順から音楽をたどる。','/volumes/'+vid+'.html')+'<body id="top">'+header('volumes')+f'''<main id="main" class="wrap"><div class="breadcrumb"><a href="/#collection">作品一覧</a><span> / </span>PREMIUM CUTS {vid}</div><section class="volume-hero"><div class="volume-cover">{pattern(i)}<div class="cover-caption"><span>PREMIUM CUTS</span><b>{vid}</b></div></div><div class="volume-intro"><span class="eyebrow">MIXED BY MASANORI SUZUKI</span><h1>{e(v['title'])}<span>Premium Cuts {vid}</span></h1><p>{subtitles[i-1]}</p><div class="volume-stats"><span><b>{v['count']}</b> 曲目</span><span>SIDE A <b>{v['a']}</b></span><span>SIDE B <b>{v['b']}</b></span></div><div class="pills"><a href="#side-a">Side A ↓</a><a href="#side-b">Side B ↓</a></div></div></section><div class="record-layout"><aside class="record-sidebar"><span class="eyebrow">DANS CETTE MIXTAPE</span><a href="#side-a">Side A <span>{v['a']:02}</span></a><a href="#side-b">Side B <span>{v['b']:02}</span></a><p>曲名を選ぶと、<br>個別ページへ進めます。</p></aside><div class="track-sides">'''
 for side in ['A','B']:
  seq=[x for x in tracks if x['volume']==vid and x['side']==side];m=marks[vid][side]
  page+=f'<section class="side-section" id="side-{side.lower()}"><div class="side-heading"><h2>Side <i>{side}.</i></h2><span>{len(seq):02} ENTRIES</span></div><ol class="side-list">'
  for t in seq:
   for mark in m.get(t['position']-1,[]):page+=f'<li class="interlude"><span><svg class="asterisk-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="M32 3v58M3 32h58M11.5 11.5l41 41M11.5 52.5l41-41" fill="none" stroke="currentColor" stroke-width="3"/></svg></span>{e(mark)}</li>'
   page+=row(t)
  for mark in m.get(len(seq),[]):page+=f'<li class="interlude"><span><svg class="asterisk-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="M32 3v58M3 32h58M11.5 11.5l41 41M11.5 52.5l41-41" fill="none" stroke="currentColor" stroke-width="3"/></svg></span>{e(mark)}</li>'
  page+='</ol></section>'
 page+='</div></div><nav class="volume-pagination" aria-label="前後の作品">'
 if i>1:page+=f'<a href="/volumes/{i-1:03}.html">← {i-1:03} {titles[i-2]}</a>'
 else:page+='<a href="/#collection">← 作品一覧</a>'
 if i<7:page+=f'<a href="/volumes/{i+1:03}.html">{i+1:03} {titles[i]} →</a>'
 else:page+='<a href="/tracks.html">全曲一覧 →</a>'
 page+='</nav></main>'+footer()+'</body></html>';(D/f'volumes/{vid}.html').write_text(page)
# CD pages preserve one sequence per disc; no cassette sides are inferred.
for v in cd_volumes:
 vid=v['id'];seq=[t for t in tracks if t['volume']==vid]
 page=head(v['display_code']+' '+v['title']+' | Premium Cuts Listed',v['title']+'の収録曲をディスク順にたどる。','/volumes/'+vid+'.html')+'<body id="top">'+header('volumes')+f'''<main id="main" class="wrap"><div class="breadcrumb"><a href="/#collection">作品一覧</a> / {v['display_code']}</div><section class="volume-hero"><div class="volume-cover">{pattern(v['pattern'])}<div class="cover-caption"><span>PREMIUM CUTS / MIX CD</span><b>#{v['number']}</b></div></div><div class="volume-intro"><span class="eyebrow">MIXED BY MASANORI SUZUKI</span><h1>{e(v['title'])}<span>Premium Cuts {v['display_code']}</span></h1><p>一つのMIXを、一曲ずつ。</p><div class="volume-stats"><span><b>{v['count']}</b> 曲目</span><span><b>{len(v['discs'])}</b> DISC(S)</span></div><div class="pills">'''
 for disc in v['discs']:page+=f'<a href="#disc-{disc}">Disc {disc} ↓</a>'
 page+='</div></div></section><div class="cd-track-sides">'
 for disc in v['discs']:
  disk=[t for t in seq if t['disc']==disc]
  page+=f'<section class="side-section" id="disc-{disc}"><div class="side-heading"><h2>Disc <i>{disc}.</i></h2><span>{len(disk):02} ENTRIES</span></div><ol class="side-list">'+''.join(row(t) for t in disk)+'</ol></section>'
 page+='</div><nav class="volume-pagination" aria-label="作品一覧"><a href="/#collection">← 作品一覧</a><a href="/tracks.html?volume='+vid+'">この作品の全曲を検索 →</a></nav></main>'+footer()+'</body></html>'
 (D/f'volumes/{vid}.html').write_text(page)
# Source-backed editorial articles share explicit entry IDs; titles alone never merge recordings.
def player(t):
 video=players.get(t['id'])
 if not video:return ''
 return f'<section id="listen" class="song-editorial pc-listen-card" aria-label="この曲を聴く"><div><span class="eyebrow">ÉCOUTER CE MORCEAU</span><h2>この曲を聴く</h2><p>共通プレーヤーで再生。音楽を聴きながら、曲の背景を。</p><p>{e(video.get("note",""))}</p></div><div><button class="pc-play-button" type="button" data-play-id="{t["id"]}" data-play-scope="volume:{t["volume"]}">▶ この曲を聴く</button><p><a class="text-link" href="{e(video["url"])}" target="_blank" rel="noopener noreferrer">YouTubeで開く ↗</a></p></div></section>'
def editorial(t):
 a=articles.get(t['id'])
 if not a:return ''
 def refs(nums):return ''.join(f' <a class="cite" href="#reference-{n}" aria-label="出典{n}">[{n}]</a>' for n in nums)
 out='<article class="song-editorial"><span class="eyebrow">NOTES DE POCHETTE</span><h2 class="song-catch">'+e(a['catch'])+'</h2><p class="song-lead">'+e(a['intro'])+'</p><dl class="research-facts">'
 for label,value in [('発売年',str(a['year'])+'年' if a.get('year') else '未確定'),('国・活動圏',a['country']),('参照盤の発売国',a['press_country']),('ジャンルの手がかり',a['genre']),('参照したレコード',a['release']),('制作・録音年',a.get('recorded','未確認'))]:out+='<div><dt>'+label+'</dt><dd>'+e(value)+'</dd></div>'
 out+='</dl>'
 if a.get('note'):out+='<p class="research-note">'+e(a['note'])+'</p>'
 for heading,body,nums in a['sections']:out+='<section class="editorial-section"><h3>'+e(heading)+'</h3><p>'+e(body)+refs(nums)+'</p></section>'
 out+='<p class="research-note">聴き方の提案は、この曲を楽しむための鑑賞ガイドです。</p><section class="editorial-section"><span class="eyebrow">ÉCOUTER ENCORE</span><h3>関連曲を、棚の中から。</h3><div class="related-cuts">'
 for tid,reason in a['related']:
  x=track_by_id[tid];out+=f'<a href="/tracks/{tid}.html"><strong>{e(x["title"])}</strong><span>{e(x["artist"])}</span><small>{e(reason)}</small><b aria-hidden="true">↗</b></a>'
 out+='</div></section>'
 appearances=[track_by_id[x] for x in a['ids'] if x!=t['id']]
 if appearances:
  out+='<section class="editorial-section"><h3>ほかの収録先</h3><ul>'
  for x in appearances:
   v=next(v for v in volumes if v['id']==x['volume']);out+=f'<li><a href="/tracks/{x["id"]}.html">{e(v["display_code"])} {e(v["title"])} / {location_label(x)} ↗</a></li>'
  out+='</ul></section>'
 out+='<section class="research-sources"><span class="eyebrow">SOURCES & REPÈRES</span><h3>出典と資料メモ</h3><p>年は確認できた最も早い発売年を採用。活動国と盤の発売国、再発年は分けて記録しています。</p><ol>'
 for n,s in enumerate(a['sources'],1):out+=f'<li id="reference-{n}"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["label"])} ↗</a><p>{e(s["note"])}</p></li>'
 return out+'</ol><p class="research-note">資料確認日 '+research['updated']+' · 解説は確認資料の範囲で更新します。</p></section></article>'
# Every entry keeps a fixed URL. Original cassette entry URLs stay unchanged.
for t in tracks:
 v=next(x for x in volumes if x['id']==t['volume']);same=[x for x in tracks if x['volume']==t['volume'] and x['side']==t['side']];pos=same.index(t)
 title=t['title'];loc=location_label(t);status=''
 marker=f'<span class="mix-marker">{e(t["mix_marker"])}</span>' if t.get('mix_marker') else ''
 artist=f'<a class="artist-link" href="/tracks.html?artist={quote(t["artist"],safe="")}">{e(t["artist"])} <span>↗</span></a>' if not t['artist'].startswith('アーティスト未') else '<p class="artist-link">アーティスト未確認</p>'
 page=head(title+' — '+t['artist']+' | Premium Cuts Listed',t['artist']+'「'+title+'」。'+v['display_code']+' '+v['title']+'の収録曲。','/tracks/'+t['id']+'.html')+'<body id="top">'+header('tracks')+f'''<main id="main" class="wrap song-page"><div class="breadcrumb"><a href="/volumes/{t['volume']}.html">{v['display_code']} {e(v['title'])}</a> / {loc}</div><section class="song-hero"><div><span class="eyebrow">PREMIUM CUTS {v['display_code']} / {loc}</span><h1>{e(title)}</h1>{artist}{marker}{essential_badge(t)}</div><a class="song-cover" href="/volumes/{t['volume']}.html" aria-label="収録作品{e(v['title'])}へ">{pattern(v['pattern'])}<span>{v['display_code']} / {e(v['title'])} ↗</span></a></section><section class="song-info"><div><span class="eyebrow">DANS LA COLLECTION</span><h2>この曲の、<i>居場所。</i></h2></div><dl><div><dt>収録作品</dt><dd><a href="/volumes/{t['volume']}.html">Premium Cuts {v['display_code']}<br>{e(v['title'])} ↗</a></dd></div><div><dt>収録位置</dt><dd>{loc}</dd></div><div><dt>アーティスト</dt><dd>{e(t['artist'])}</dd></div></dl></section>'''
 if t['id'] in players:
  page=page.replace('<section class="song-info">',player(t)+'<section class="song-info">',1)
  page=page.replace(artist+marker+essential_badge(t)+'</div>',artist+marker+essential_badge(t)+'<p><a class="text-link" href="#listen">▶ この曲を聴く</a></p></div>',1)
 page+=editorial(t)
 page+=f'<div class="song-source"><a class="text-link" href="/volumes/{t["volume"]}.html">この作品のトラックリストを見る ↗</a></div><nav class="song-pagination" aria-label="前後の曲">'
 if pos>0:
  prev=same[pos-1];page+=f'<a href="/tracks/{prev["id"]}.html"><span>← PREVIOUS CUT</span><strong>{e(prev["title"])}</strong><small>{e(prev["artist"])}</small></a>'
 else:page+=f'<a href="/volumes/{t["volume"]}.html"><span>← TRACKLIST</span><strong>作品の曲目へ</strong></a>'
 if pos<len(same)-1:
  nxt=same[pos+1];page+=f'<a href="/tracks/{nxt["id"]}.html"><span>NEXT CUT →</span><strong>{e(nxt["title"])}</strong><small>{e(nxt["artist"])}</small></a>'
 else:page+=f'<a href="/volumes/{t["volume"]}.html"><span>TRACKLIST →</span><strong>作品の曲目へ</strong></a>'
 page+='</nav></main>'+footer()+'</body></html>';(D/'tracks'/f'{t["id"]}.html').write_text(page)
# A fully usable HTML list remains available with JavaScript disabled.
page=head('すべての曲 | Premium Cuts Listed',f'Premium Cutsの{N}曲目を作品、曲名、アーティストから検索。','/tracks.html')+'<body id="top">'+header('tracks')+f'''<main id="main" class="wrap catalog-page"><section class="catalog-heading"><div><span class="eyebrow">INDEX DES MORCEAUX</span><h1>すべての曲を、<br><i>ひとつの棚に。</i></h1></div><p>22作品の曲目を横断して。<br>気になる名前から、次の一曲へ。</p></section><form class="filters" role="search" onsubmit="return false"><label class="search-field"><span aria-hidden="true">⌕</span><input id="search" type="search" aria-label="曲名・アーティストを検索" placeholder="曲名・アーティストを検索"></label><select id="feature-filter" aria-label="特集"><option value="">すべての曲</option><option value="essentials">Premium Cuts Essentials</option></select><select id="series-filter" aria-label="シリーズ"><option value="">すべてのシリーズ</option><option value="tape">MIX TAPE</option><option value="cd">MIX CD</option></select><select id="volume-filter" aria-label="収録作品"><option value="">すべての作品</option>'''+''.join(f'<option value="{v["id"]}">{v["display_code"]} {v["title"]}</option>' for v in volumes)+'''</select><select id="side-filter" aria-label="収録面・ディスク"><option value="">すべての面・ディスク</option><option value="A">Side A</option><option value="B">Side B</option><option value="D1">Disc 1</option><option value="D2">Disc 2</option></select><select id="sort" aria-label="並べ替え"><option value="order">作品・曲順</option><option value="title">曲名 A–Z</option><option value="artist">アーティスト A–Z</option></select><button class="reset" type="button" id="reset">条件をクリア</button></form><div class="list-caption"><span id="result-count" aria-live="polite">'''+str(N)+''' 曲目</span><span>曲名 / アーティスト / 収録作品</span></div><ol class="catalog-list" id="catalog-list">'''+''.join(f'<li class="catalog-row"><a class="catalog-title" href="/tracks/{t["id"]}.html"><strong>{e(t["title"])}</strong><span>{e(t["artist"])}</span><small class="mix-marker">{e(t.get("mix_marker",""))}</small></a><a class="volume-tag" href="/volumes/{t["volume"]}.html">{next(v["display_code"] for v in volumes if v["id"]==t["volume"])} / {position_label(t)}</a><a class="row-arrow" href="/tracks/{t["id"]}.html" aria-label="{e(t["title"])}の詳細">↗</a></li>' for t in tracks)+'''</ol><div class="no-results" id="no-results" hidden><span><svg class="asterisk-icon" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="M32 3v58M3 32h58M11.5 11.5l41 41M11.5 52.5l41-41" fill="none" stroke="currentColor" stroke-width="3"/></svg></span><h2>該当する曲が見つかりませんでした。</h2><p>別の綴りで検索するか、条件をクリアしてみてください。</p></div><p class="list-note">同じ曲が複数の作品に収録されている場合は、作品ごとに表示します。</p></main>'''+footer()+'</body></html>';(D/'tracks.html').write_text(page)
page=head('このサイトについて | Premium Cuts Listed','Premium Cuts ListedのPremium Cutsの音楽と収録作品について。','/about.html')+'<body id="top">'+header('about')+'''<main id="main" class="wrap about-page"><div class="eyebrow">À PROPOS DE CETTE COLLECTION</div><h1>好きな音楽を、<br><i>ゆっくり、深く。</i></h1><div class="about-body"><section><h2>Premium Cutsの収録曲を、たどる。</h2><p>Premium Cuts Listedは、Masanori Suzuki（鈴木雅尭）による「Premium Cuts」に収録された楽曲を紹介する、個人制作のアーカイブです。カセット7作品とMIX CD 15タイトルを、作品別・Side別・ディスク別の曲順で紹介しています。同じ番号でもカセットとMIX CDは別作品として掲載します。</p><p>サイトの構成はCRATE DIGGIN’を参考にしています。掲載対象を決めるのはPremium Cutsのトラックリストです。</p></section><section><h2>曲順と、短い合図も大切に。</h2><p>各作品のSide AとSide Bを、収録順にたどれます。intro、jingle、commercial、intermissionなどは曲間の区切りとして記載し、名前のある曲目の件数には含めていません。</p></section><section><h2>一曲の背景を、深く知る。</h2><p>制作年と発売年、アーティストの活動国と録音地、原曲とカバー。それぞれの違いを大切にしながら、音楽の背景を紹介します。</p></section><section><h2>一曲ずつ、育てる。</h2><p>まずは作品と曲の入口をつくりました。曲の背景、国やジャンルとのつながり、関連アーティスト、音源・動画は、資料を確かめながら少しずつ加えていきます。詳しい解説が加わっても、作品ごとの曲順からたどる入り口はそのままです。</p></section><section><h2>デザインについて。</h2><p>ブルーとクリーム色、紙の質感、リズムのある幾何学模様。フランスの音楽誌や小さなレコード店を思わせる棚を目指しました。各作品の模様は、このサイト独自のデザインです。</p></section><a class="round-link" href="/#collection">作品の棚へ戻る <span>↗</span></a></div></main>'''+footer()+'</body></html>';(D/'about.html').write_text(page)
# Shared PLAYER page; the playback instance remains outside the replaced main content.
playable_volumes=[v for v in volumes if any(t['volume']==v['id'] and t['id'] in players for t in tracks)]
options='<option value="all">指定音源のあるすべての曲</option>'+''.join(f'<option value="volume:{v["id"]}">{e(v["display_code"])} {e(v["title"])}</option>' for v in playable_volumes)
page=head('PLAYER | Premium Cuts Listed','Premium Cutsの収録曲を作品の曲順で連続再生。音楽を聴きながら解説やトラックリストを読む。','/player.html')+'<body id="top">'+header('player')+'<main id="main" class="wrap pc-player-page"><span class="eyebrow">THE LISTENING ROOM</span><h1>Listen.<br><i>Dig a little deeper.</i></h1><p>音楽を聴きながら、レコードの背景へ。<br>指定音源のある曲を、作品ごとの曲順で。</p><button type="button" class="pc-play-button" data-play-all>▶ すべての曲を聴く</button><div class="pc-queue-tools"><label for="pc-scope">再生する曲順</label><select id="pc-scope">'+options+'</select><span id="pc-queue-count"></span><button type="button" id="pc-show-all">すべての音源を表示</button><button type="button" id="pc-refresh">最新の曲を確認</button><span id="pc-catalog-status" role="status" aria-live="polite"></span></div><ol id="pc-queue-list" class="pc-queue-list"></ol><noscript><p>連続再生にはJavaScriptを有効にしてください。各楽曲ページのYouTubeリンクからも聴けます。</p></noscript></main>'+footer()+'</body></html>'
(D/'player.html').write_text(page)
# Curated Essentials membership is explicit and independent of future player additions.
feature_rows=''
for n,t in enumerate(essential_tracks,1):
 v=next(v for v in volumes if v['id']==t['volume'])
 feature_rows+=f'<li class="essential-cut"><span class="essential-number">{n:02}</span><div><a class="essential-song" href="/tracks/{t["id"]}.html"><strong>{e(t["title"])}</strong><span>{e(t["artist"])}</span></a><a class="essential-origin" href="/volumes/{t["volume"]}.html">{e(v["display_code"])} · {location_label(t)} ↗</a></div><button type="button" class="pc-inline-play" data-play-id="{t["id"]}" data-play-scope="volume:{t["volume"]}" aria-label="{e(t["title"])}を再生">▶</button><a class="text-link" href="/tracks/{t["id"]}.html">解説 ↗</a></li>'
page=head('Premium Cuts Essentials | Premium Cuts Listed',essentials['description'],'/features/essentials.html')+'<body id="top">'+header('essentials')+f'<main id="main" class="wrap essentials-page"><div class="breadcrumb"><a href="/">HOME</a> / FEATURE 01</div><section class="essentials-heading"><div><span class="eyebrow">SELECTED BY DJ NAOYAMAN / 24 RECORDINGS</span><h1>Premium Cuts<br><i>Essentials.</i></h1><p class="song-lead">何度でも戻りたくなる、<br>このコレクションの核。</p><p>DJ Naoyamanが選ぶ、Premium Cutsの24音源。<br>ジャズ、ブラジル、フレンチ・ポップ。その境目を越えて、<br>好きな音楽へ戻るための特集です。</p></div><div class="essentials-symbol">{pattern(23)}<span>THE HEART OF THE COLLECTION</span></div></section><div class="list-caption"><span>24 ESSENTIAL RECORDINGS</span><span>作品・曲順で掲載</span></div><ol class="essential-list">{feature_rows}</ol><p class="list-note">同じ録音の重複収録はひとつにまとめています。Berry Lipmanの通常版とDisco版は、それぞれの音源として掲載。</p><p><a class="text-link" href="/tracks.html?feature=essentials">全曲一覧でEssentialsを絞り込む ↗</a></p></main>'+footer()+'</body></html>'
(D/'features/essentials.html').write_text(page)

# Each mix has an explicit queue-start action, independent from browsing.
for v in playable_volumes:
 pagefile=D/f'volumes/{v["id"]}.html';markup=pagefile.read_text()
 markup=markup.replace('<div class="pills">',f'<button type="button" class="pc-play-button" data-play-volume="{v["id"]}">▶ この作品の曲順で聴く</button><div class="pills">',1)
 pagefile.write_text(markup)
# Matching sharing and home-screen assets.
(D/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#f2e8d7"/><circle cx="32" cy="32" r="25" fill="#126887"/><circle cx="32" cy="32" r="10" fill="#f2e8d7"/><circle cx="32" cy="32" r="3" fill="#126887"/></svg>')
im=Image.new('RGB',(1200,630),'#f2e8d7');draw=ImageDraw.Draw(im);font='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';draw.line((50,65,1150,65),fill='#126887',width=2);draw.text((60,120),'Premium',font=ImageFont.truetype(font,100),fill='#126887');draw.text((60,240),'Cuts Listed.',font=ImageFont.truetype(font,92),fill='#126887');draw.text((65,520),'THE PREMIUM CUTS ARCHIVE / TAPES + MIX CDS',font=ImageFont.truetype(font,23),fill='#126887');
for x in range(810,1140,40):draw.rectangle((x,115,x+18,460),fill='#126887')
im.save(D/'og.png');icon=Image.new('RGB',(180,180),'#f2e8d7');dr=ImageDraw.Draw(icon);dr.ellipse((15,15,165,165),fill='#126887');dr.ellipse((60,60,120,120),fill='#f2e8d7');dr.ellipse((82,82,98,98),fill='#126887');icon.save(D/'apple-touch-icon.png')
urls=['/','/features/essentials.html','/tracks.html','/about.html','/player.html']+['/volumes/'+v['id']+'.html' for v in volumes]+['/tracks/'+t['id']+'.html' for t in tracks]
(D/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+origin+u+'</loc></url>' for u in urls)+'</urlset>');(D/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
print(json.dumps({'volumes':len(volumes),'entries':len(tracks),'corrected':sum(t['status']=='corrected' for t in tracks),'pending':sum(t['status']=='pending' for t in tracks),'counts':[(v['id'],v['count']) for v in volumes]},ensure_ascii=False))

# Project Pages lives below /premiumcuts rather than the domain root.
if base_path:
 for page in D.rglob('*.html'):
  markup=page.read_text()
  for attr in ['href','src']:
   markup=markup.replace(attr+'="/',attr+'="'+base_path+'/')
  page.write_text(markup)
 js=(D/'app.js').read_text().replace('href="/tracks/','href="'+base_path+'/tracks/').replace('href="/volumes/','href="'+base_path+'/volumes/').replace('href="/features/','href="'+base_path+'/features/')
 (D/'app.js').write_text(js)
(D/'.nojekyll').write_text('')
