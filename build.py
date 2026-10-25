from pathlib import Path
import json,html,re,shutil,unicodedata,collections,os
from urllib.parse import quote
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).parent;D=P/'dist';U=P/'source-images';e=html.escape
origin=os.environ.get('SITE_ORIGIN','https://premium-cuts-listed.mossyelf3.chatgpt.site').rstrip('/')
base_path=os.environ.get('BASE_PATH','').rstrip('/')
titles=['ON THE AIR','SINCERELY','COMMERCIALS','AUDIOSCAPE','JINGLES','COUNSELING','HOLIDAY MUSIC']
subtitles=['ラジオの向こうで、音楽に出会う。','一曲ずつ、気持ちをつないで。','日常の隙間に、小さな音楽を。','音が描く、もうひとつの風景。','短い合図から、次の曲へ。','気分に寄り添う、レコードの時間。','休日には、少し遠くの音楽を。']
# Editorial taglines describe the archive experience, not the mix creator's stated intent.
files=['画像1.jpg','画像2.jpg','image(20261025-152132).png','Premium Cuts 004 AUDIOSCAPE.jpg','Premium Cuts 005 JINGLES 1.jpg','Premium Cuts 006 COUNCERING.jpg','Premium Cuts 007 HOLIDAY MUSIC.png']
for path in ['tracks','volumes','assets']: (D/path).mkdir(parents=True,exist_ok=True)
# Replace the superseded, out-of-scope catalog completely.
for f in (D/'tracks').glob('*.html'):f.unlink()
for n in ['style.css','app.js']:shutil.copy2(P/'src'/n,D/n)
for i in range(1,8):
 shutil.copy2(U/f'{i:03}.jpg',D/f'assets/source-{i:03}.jpg')
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
pending={('001','A',11):'画像の「JULIAN BAREY ORC.」のアーティスト表記を照合予定。',('001','A',15):'画像の「THE LIPSTICS / BIM BA BA BI BAAA」をもとに転記。正式表記を照合予定。',('001','B',4):'画像の「VIA SZBABA / RAZOM」をもとに転記。アーティスト名・曲名とも要照合。',('001','B',1):'曲名は画像どおり。別作品と取り違えないよう照合予定。',('003','B',2):'アーティストの正式表記と版を照合予定。',('005','A',3):'曲名は画像どおり。正式表記を照合予定。',('005','A',13):'画像では二つの曲名がハイフンで連結。メドレー／曲目の区切りを照合予定。',('005','B',4):'アーティストの正式表記を照合予定。',('005','B',5):'アーティスト名・曲名の正式表記を照合予定。',('006','A',11):'画像の英語表記を仮転記。原曲名・正式表記を照合予定。',('006','B',6):'アーティスト名と編成の正式表記を照合予定。',('006','B',11):'画像の「PETER BEASSON / WALLE-STREET」をもとに転記。正式表記を照合予定。',('006','B',15):'画像は「BEEN TO CANNAN」。正式曲名・アーティストの照合後に修正予定。',('007','A',7):'画像は「SVENNE & LOTTA / I WANT YOU BACK」。曲名の先頭語の有無を照合予定。',('007','B',5):'画像の「NICK AYOUB / MONTRIAL EAST」とは別曲。アーティストと音源を照合予定。',('007','B',13):'画像の「CEBION GLICOSE / VIVA A ALEGRIA」をもとに転記。名義の扱いを照合予定。'}
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
# Interludes are not counted as named songs. Their original positions are retained.
marks={
 '001':{'A':{0:['intro — tuning'],12:['intermission — on the air 1']},'B':{0:['intermission — on the air 2'],13:['outro — off the air'],15:['chao']}},
 '002':{'A':{0:['intro'],16:['intermission']},'B':{11:['intermission'],17:['outro']}},
 '003':{'A':{0:['OPENING SHOW'],8:['COMMERCIAL'],14:['THE MIDDLE']},'B':{10:['COMMERCIAL'],17:['CLOSING SHOW']}},
 '004':{'A':{0:['BREAK 1']},'B':{0:['BREAK 2'],12:['BREAK 3'],15:['AUDIOSCAPE']}},
 '005':{'A':{0:['JINGLE 1'],9:['JINGLE 2'],17:['JINGLE 3']},'B':{0:['JINGLE 4'],6:['JINGLE 5'],16:['JINGLE 6']}},
 '006':{'A':{0:['counseling 1'],13:['counseling 2'],16:['counseling 3']},'B':{11:['counseling 4'],14:['counseling 5']}},
 '007':{'A':{0:['JINGLE'],8:['JINGLE'],17:['JINGLE']},'B':{4:['JINGLE'],13:['JINGLE']}}}
(D/'data.js').write_text('const TRACKS='+json.dumps(tracks,ensure_ascii=False)+';\nconst VOLUMES='+json.dumps(volumes,ensure_ascii=False)+';')
(P/'catalog.json').write_text(json.dumps({'volumes':volumes,'tracks':tracks,'markers':marks},ensure_ascii=False,indent=2))
(P/'tracks.json').unlink(missing_ok=True)

def pattern(i,cls=''):
 return f'<div class="pattern p{i} {cls}" aria-hidden="true"><div class="pattern-layer"></div><div class="pattern-layer second"></div><span class="dot"></span></div>'
def head(title,desc,path='/'):
 return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{origin}{path}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{origin}{path}"><meta property="og:image" content="{origin}/og.png"><meta property="og:locale" content="ja_JP"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#f2e8d7"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="stylesheet" href="/style.css"><script defer src="/data.js"></script><script defer src="/app.js"></script></head>'''
def header(active=''):
 return '<a class="skip" href="#main">本文へ</a><header><a class="brand" href="/"><span class="brand-mark" aria-hidden="true">✳</span><span>Premium Cuts<br><b>Listed.</b></span></a><nav aria-label="メインナビゲーション">'+''.join(f'<a class="{"selected" if k==active else ""}" href="{u}">{n}</a>' for k,u,n in [('volumes','/#collection','作品から探す'),('tracks','/tracks.html','すべての曲'),('about','/about.html','このサイトについて')])+'</nav><span class="header-meta">LES BONNES<br>VIBRATIONS.</span></header>'
def footer():return '<footer><a class="footer-logo" href="/">Premium Cuts Listed<span>Une collection de bonnes vibrations.</span></a><p>Selection & mix by Masanori Suzuki<br>個人制作の収録曲アーカイブ</p><a href="#top">ページの上へ ↑</a></footer>'
def tile(v):
 return f'''<article class="volume-card"><a href="/volumes/{v['id']}.html">{pattern(int(v['id']))}<div class="card-meta"><span>PREMIUM CUTS</span><span>NO. {v['id']}</span></div><h3>{e(v['title'])}<span>↗</span></h3><div class="card-bottom"><span>SIDE A + SIDE B</span><span>{v['count']} ENTRIES</span></div></a></article>'''
def row(t):
 badge='<span class="dot-label" title="'+e(t['note'] or '')+'">要照合</span>' if t['status']=='pending' else ''
 return f'''<li class="track-row" data-id="{t['id']}"><span class="track-pos">{t['side']}{t['position']:02}</span><a class="track-main" href="/tracks/{t['id']}.html"><strong>{e(t['title'])}</strong><span>{e(t['artist'])}</span></a>{badge}<a class="row-arrow" href="/tracks/{t['id']}.html" aria-label="{e(t['title'])}の詳細">↗</a></li>'''
N=len(tracks)
home=head('Premium Cuts Listed — 一曲の先に、また一曲。','Masanori SuzukiのPremium Cuts。その収録曲だけを、作品と曲順からたどる音楽アーカイブ。')+'<body id="top">'+header('volumes')+f'''<main id="main"><section class="hero wrap"><div class="hero-top"><span class="eyebrow">THE PREMIUM CUTS ARCHIVE</span><span class="eyebrow">JAZZ, BRASIL, FRENCH & MANY MORE</span></div><div class="hero-content"><div><h1>Premium<br>Cuts <i>Listed.</i></h1><p class="hero-jp">一曲の先に、<br>また一曲。</p><p class="hero-copy">鈴木雅尭の「Premium Cuts」で出会った音楽を。<br>作品を開き、曲順をたどり、好きな一曲を見つける。</p><a class="round-link" href="#collection">レコード棚をのぞく <span>↓</span></a></div><div class="hero-art">{pattern(1)}<div class="art-caption"><span>UNE COLLECTION<br>DE BONNES VIBRATIONS.</span><span>001—007</span></div></div></div><div class="hero-bottom"><span>MIXED BY MASANORI SUZUKI</span><span>{len(volumes):02} MIX TAPES &nbsp; / &nbsp; {N} ENTRIES</span></div></section><section class="collection wrap" id="collection"><div class="section-heading"><div><span class="eyebrow">LA COLLECTION</span><h2>作品から、<i>ひらく。</i></h2></div><p>001から007へ。<br>それぞれのSide AとSide Bを、その順番で。</p></div><div class="volume-grid">'''+''.join(tile(v) for v in volumes)+f'''<a class="index-card" href="/tracks.html"><span class="eyebrow">INDEX DES MORCEAUX</span><strong>すべての曲を<br><i>ひとつの棚に。</i></strong><span class="index-number">{N}<small>曲目</small></span><span class="index-bottom">曲名・アーティストから探す <b>↗</b></span></a></div></section><section class="about-strip wrap"><span class="star" aria-hidden="true">✳</span><div><span class="eyebrow">À PROPOS</span><h2>好きな音楽を、<br>ゆっくり、深く。</h2><p>この棚に並ぶのは「Premium Cuts」の収録曲だけ。<br>まずは曲目と曲順を。音楽の背景や映像は、一曲ずつ大切に。</p><a class="text-link" href="/about.html">このアーカイブについて ↗</a></div></section></main>'''+footer()+'</body></html>'
(D/'index.html').write_text(home)
for v in volumes:
 vid=v['id'];i=int(vid)
 page=head('Premium Cuts '+vid+' '+v['title']+' | Premium Cuts Listed',f'Premium Cuts {vid} {v["title"]}の収録曲一覧。Side AとSide Bの曲順から音楽をたどる。','/volumes/'+vid+'.html')+'<body id="top">'+header('volumes')+f'''<main id="main" class="wrap"><div class="breadcrumb"><a href="/#collection">作品一覧</a><span> / </span>PREMIUM CUTS {vid}</div><section class="volume-hero"><div class="volume-cover">{pattern(i)}<div class="cover-caption"><span>PREMIUM CUTS</span><b>{vid}</b></div></div><div class="volume-intro"><span class="eyebrow">MIXED BY MASANORI SUZUKI</span><h1>{e(v['title'])}<span>Premium Cuts {vid}</span></h1><p>{subtitles[i-1]}</p><div class="volume-stats"><span><b>{v['count']}</b> 曲目</span><span>SIDE A <b>{v['a']}</b></span><span>SIDE B <b>{v['b']}</b></span></div><div class="pills"><a href="#side-a">Side A ↓</a><a href="#side-b">Side B ↓</a><a href="#source">原資料を見る ↗</a></div></div></section><div class="record-layout"><aside class="record-sidebar"><span class="eyebrow">DANS CETTE MIXTAPE</span><a href="#side-a">Side A <span>{v['a']:02}</span></a><a href="#side-b">Side B <span>{v['b']:02}</span></a><a href="#source">トラックリスト原資料</a><p>曲名を選ぶと、<br>個別ページへ進めます。</p></aside><div class="track-sides">'''
 for side in ['A','B']:
  seq=[x for x in tracks if x['volume']==vid and x['side']==side];m=marks[vid][side]
  page+=f'<section class="side-section" id="side-{side.lower()}"><div class="side-heading"><h2>Side <i>{side}.</i></h2><span>{len(seq):02} ENTRIES</span></div><ol class="side-list">'
  for t in seq:
   for mark in m.get(t['position']-1,[]):page+=f'<li class="interlude"><span>✳</span>{e(mark)}</li>'
   page+=row(t)
  for mark in m.get(len(seq),[]):page+=f'<li class="interlude"><span>✳</span>{e(mark)}</li>'
  page+='</ol></section>'
 page+=f'''<section class="source-section" id="source"><span class="eyebrow">DOCUMENT ORIGINAL</span><h2>曲目のもとになった資料。</h2><p>ご提供いただいたジャケット画像から曲順を転記しました。綴りを修正した箇所は個別ページに記録し、判読や名義の確認が必要な項目には「要照合」を表示しています。曲数は曲名のある項目の数です。ジングル、CM、インタールードは区切りとして記載しています。</p><details><summary>Premium Cuts {vid} の原資料を開く ＋</summary><img loading="lazy" src="/assets/source-{vid}.jpg" alt="Premium Cuts {vid} {e(v['title'])}のジャケットとSide A・Side Bの曲目" width="600"></details></section></div></div><nav class="volume-pagination" aria-label="前後の作品">'''
 if i>1:page+=f'<a href="/volumes/{i-1:03}.html">← {i-1:03} {titles[i-2]}</a>'
 else:page+='<a href="/#collection">← 作品一覧</a>'
 if i<7:page+=f'<a href="/volumes/{i+1:03}.html">{i+1:03} {titles[i]} →</a>'
 else:page+='<a href="/tracks.html">全曲一覧 →</a>'
 page+='</nav></main>'+footer()+'</body></html>';(D/f'volumes/{vid}.html').write_text(page)
# Every named entry has an address; researching a song later does not change that address.
for t in tracks:
 v=next(x for x in volumes if x['id']==t['volume']);same=[x for x in tracks if x['volume']==t['volume'] and x['side']==t['side']];pos=same.index(t)
 title=t['title'];status={'pending':'原表記を照合中','corrected':'表記を修正済み','transcribed':'ジャケット画像から転記'}[t['status']]
 page=head(title+' — '+t['artist']+' | Premium Cuts Listed',f'{t["artist"]}「{title}」。Premium Cuts {t["volume"]} {v["title"]}のSide {t["side"]}収録曲。','/tracks/'+t['id']+'.html')+'<body id="top">'+header('tracks')+f'''<main id="main" class="wrap song-page"><div class="breadcrumb"><a href="/volumes/{t['volume']}.html">{t['volume']} {e(v['title'])}</a><span> / </span>SIDE {t['side']} — {t['position']:02}</div><section class="song-hero"><div><span class="eyebrow">PREMIUM CUTS {t['volume']} / SIDE {t['side']} / {t['position']:02}</span><h1>{e(title)}</h1><a class="artist-link" href="/tracks.html?artist={quote(t['artist'],safe='')}">{e(t['artist'])} <span>↗</span></a><p class="song-status">{status}</p></div><a class="song-cover" href="/volumes/{t['volume']}.html" aria-label="収録作品{e(v['title'])}へ">{pattern(int(t['volume']))}<span>{t['volume']} / {e(v['title'])} ↗</span></a></section><section class="song-info"><div><span class="eyebrow">DANS LA COLLECTION</span><h2>この曲の、<i>居場所。</i></h2></div><dl><div><dt>収録作品</dt><dd><a href="/volumes/{t['volume']}.html">Premium Cuts {t['volume']}<br>{e(v['title'])} ↗</a></dd></div><div><dt>収録位置</dt><dd>Side {t['side']} · {t['position']:02}<small>曲名のある項目を順に数えています。</small></dd></div><div><dt>アーティスト</dt><dd>{e(t['artist'])}</dd></div></dl></section>'''
 if t['note']:
  page+='<section class="notation-note"><span class="eyebrow">NOTE SUR LE TITRE</span><h2>表記について</h2><p>'+e(t['note'])+'</p><p class="original-label">原資料の表記<br><strong>'+e(t['original'])+'</strong></p>'
  if t['source']:page+=f'<a class="text-link" href="{e(t["source"])}" target="_blank" rel="noopener noreferrer">表記の照合に使った資料 ↗</a>'
  page+='</section>'
 page+=f'''<div class="song-source"><a class="text-link" href="/volumes/{t['volume']}.html#source">ジャケットのトラックリストを見る ↗</a><p>制作・発売年、国、ジャンル、制作背景は、出典を確かめながら順次追加します。音源・動画も同一の演奏や版を照合してから掲載します。</p></div><nav class="song-pagination" aria-label="同じ面の前後の曲">'''
 if pos>0:
  prev=same[pos-1];page+=f'<a href="/tracks/{prev["id"]}.html"><span>← PREVIOUS CUT</span><strong>{e(prev["title"])}</strong><small>{e(prev["artist"])}</small></a>'
 else:page+=f'<a href="/volumes/{t["volume"]}.html#side-{t["side"].lower()}"><span>← TRACKLIST</span><strong>Side {t["side"]} の曲目へ</strong></a>'
 if pos<len(same)-1:
  nxt=same[pos+1];page+=f'<a href="/tracks/{nxt["id"]}.html"><span>NEXT CUT →</span><strong>{e(nxt["title"])}</strong><small>{e(nxt["artist"])}</small></a>'
 else:page+=f'<a href="/volumes/{t["volume"]}.html"><span>TRACKLIST →</span><strong>作品の曲目へ</strong></a>'
 page+='</nav></main>'+footer()+'</body></html>';(D/'tracks'/f'{t["id"]}.html').write_text(page)
# A fully usable HTML list remains available with JavaScript disabled.
page=head('すべての曲 | Premium Cuts Listed',f'Premium Cuts 001–007の{N}曲目を作品、曲名、アーティストから検索。','/tracks.html')+'<body id="top">'+header('tracks')+f'''<main id="main" class="wrap catalog-page"><section class="catalog-heading"><div><span class="eyebrow">INDEX DES MORCEAUX</span><h1>すべての曲を、<br><i>ひとつの棚に。</i></h1></div><p>7作品の曲目を横断して。<br>気になる名前から、次の一曲へ。</p></section><form class="filters" role="search" onsubmit="return false"><label class="search-field"><span aria-hidden="true">⌕</span><input id="search" type="search" aria-label="曲名・アーティストを検索" placeholder="曲名・アーティストを検索"></label><select id="volume-filter" aria-label="収録作品"><option value="">すべての作品</option>'''+''.join(f'<option value="{v["id"]}">{v["id"]} {v["title"]}</option>' for v in volumes)+'''</select><select id="side-filter" aria-label="収録面"><option value="">両方の面</option><option value="A">Side A</option><option value="B">Side B</option></select><select id="sort" aria-label="並べ替え"><option value="order">作品・曲順</option><option value="title">曲名 A–Z</option><option value="artist">アーティスト A–Z</option></select><button class="reset" type="button" id="reset">条件をクリア</button></form><div class="list-caption"><span id="result-count" aria-live="polite">'''+str(N)+''' 曲目</span><span>曲名 / アーティスト / 収録作品</span></div><ol class="catalog-list" id="catalog-list">'''+''.join(f'<li class="catalog-row"><a class="catalog-title" href="/tracks/{t["id"]}.html"><strong>{e(t["title"])}</strong><span>{e(t["artist"])}</span></a><a class="volume-tag" href="/volumes/{t["volume"]}.html">{t["volume"]} / {t["side"]}{t["position"]:02}</a><a class="row-arrow" href="/tracks/{t["id"]}.html" aria-label="{e(t["title"])}の詳細">↗</a></li>' for t in tracks)+'''</ol><div class="no-results" id="no-results" hidden><span>✳</span><h2>該当する曲が見つかりませんでした。</h2><p>別の綴りで検索するか、条件をクリアしてみてください。</p></div><p class="list-note">同じ曲が複数の作品に収録されている場合は、作品ごとに表示します。画像の原表記でも検索できます。</p></main>'''+footer()+'</body></html>';(D/'tracks.html').write_text(page)
page=head('このサイトについて | Premium Cuts Listed','Premium Cuts Listedの掲載範囲、曲順、表記修正と調査方針について。','/about.html')+'<body id="top">'+header('about')+'''<main id="main" class="wrap about-page"><div class="eyebrow">À PROPOS DE CETTE COLLECTION</div><h1>好きな音楽を、<br><i>ゆっくり、深く。</i></h1><div class="about-body"><section><h2>Premium Cutsの収録曲を、たどる。</h2><p>Premium Cuts Listedは、Masanori Suzuki（鈴木雅尭）による「Premium Cuts」に収録された楽曲を紹介する、個人制作のアーカイブです。今回ご提供いただいた7作品のジャケット画像を起点に、作品別・Side別の曲目を整理しています。</p><p>サイトの構成はCRATE DIGGIN’を参考にしています。掲載対象を決めるのはPremium Cutsのトラックリストです。</p></section><section><h2>曲順と、短い合図も大切に。</h2><p>各作品のSide AとSide Bは、画像の並び順を維持しています。intro、jingle、commercial、intermissionなどは曲間の区切りとして記載し、名前のある曲目の件数には含めていません。二曲の境界が曖昧な項目は、現段階では画像どおりの一項目として残しています。</p></section><section><h2>綴りを直す。原表記も残す。</h2><p>確認できた誤植は修正し、個別ページに修正内容と照合資料を記録します。判読しづらいもの、同名アーティストや別バージョンとの取り違えがあり得るものは「要照合」として残します。大文字・小文字、アクセント、読みやすい句読点は必要に応じて整えています。</p><p>制作年と発売年、アーティストの活動国と録音地、原曲とカバー、アルバム版と別ミックスを分けて調べます。資料で確認できない情報を、推測で埋めることはしません。</p></section><section><h2>一曲ずつ、育てる。</h2><p>まずは作品と曲の入口をつくりました。曲の背景、国やジャンルとのつながり、関連アーティスト、音源・動画は、資料を確かめながら少しずつ加えていきます。詳しい解説が加わっても、作品ごとの曲順からたどる入り口はそのままです。</p></section><section><h2>デザインについて。</h2><p>ブルーとクリーム色、紙の質感、リズムのある幾何学模様。ご提供の参考画像を手がかりに、フランスの音楽誌や小さなレコード店を思わせる棚を目指しました。各作品の模様はこのサイト独自のもので、実際のジャケットは作品ページの原資料欄に掲載しています。</p></section><a class="round-link" href="/#collection">作品の棚へ戻る <span>↗</span></a></div></main>'''+footer()+'</body></html>';(D/'about.html').write_text(page)
# Matching sharing and home-screen assets.
(D/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#f2e8d7"/><circle cx="32" cy="32" r="25" fill="#126887"/><circle cx="32" cy="32" r="10" fill="#f2e8d7"/><circle cx="32" cy="32" r="3" fill="#126887"/></svg>')
im=Image.new('RGB',(1200,630),'#f2e8d7');draw=ImageDraw.Draw(im);font='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';draw.line((50,65,1150,65),fill='#126887',width=2);draw.text((60,120),'Premium',font=ImageFont.truetype(font,100),fill='#126887');draw.text((60,240),'Cuts Listed.',font=ImageFont.truetype(font,92),fill='#126887');draw.text((65,520),'THE PREMIUM CUTS ARCHIVE / 001—007',font=ImageFont.truetype(font,23),fill='#126887');
for x in range(810,1140,40):draw.rectangle((x,115,x+18,460),fill='#126887')
im.save(D/'og.png');icon=Image.new('RGB',(180,180),'#f2e8d7');dr=ImageDraw.Draw(icon);dr.ellipse((15,15,165,165),fill='#126887');dr.ellipse((60,60,120,120),fill='#f2e8d7');dr.ellipse((82,82,98,98),fill='#126887');icon.save(D/'apple-touch-icon.png')
urls=['/','/tracks.html','/about.html']+['/volumes/'+v['id']+'.html' for v in volumes]+['/tracks/'+t['id']+'.html' for t in tracks]
(D/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+origin+u+'</loc></url>' for u in urls)+'</urlset>');(D/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
print(json.dumps({'volumes':len(volumes),'entries':len(tracks),'corrected':sum(t['status']=='corrected' for t in tracks),'pending':sum(t['status']=='pending' for t in tracks),'counts':[(v['id'],v['a'],v['b']) for v in volumes]},ensure_ascii=False))

# Project Pages lives below /premiumcuts rather than the domain root.
if base_path:
 for page in D.rglob('*.html'):
  markup=page.read_text()
  for attr in ['href','src']:
   markup=markup.replace(attr+'="/',attr+'="'+base_path+'/')
  page.write_text(markup)
 js=(D/'app.js').read_text().replace('href="/tracks/','href="'+base_path+'/tracks/').replace('href="/volumes/','href="'+base_path+'/volumes/')
 (D/'app.js').write_text(js)
(D/'.nojekyll').write_text('')
