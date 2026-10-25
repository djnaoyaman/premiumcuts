"""Shared display names for HTML, search and the audio queue."""
import re
import unicodedata

SMALL = {'a','an','and','as','at','but','by','for','from','in','into','of','on','or','the','to','with','und','et','son','e','y','de','da','do','dos','du','des','di','del','della','la','le','les','en','el','no','se','que','con','un','une','per','para','por'}
KEEP = {'L.O.V.E.','O.D.','M*A*S*H','M*A*S*H?','Mr.','P.C.','B.B.','L.A.','II','III','IV','DJ','ORF','TSU','SILVA','KEI','EIKO','ROE','YOHNO','YUCARI','D2','J.P.','J.N.','U-KNEEK'}

def clean(s):
 return re.sub(r'\s+',' ',unicodedata.normalize('NFC',s).replace('\u3000',' ').replace('’',"'").replace('‘',"'")).strip()

def title_style(s):
 # Keep already sentence-cased titles and original-language spelling intact.
 words=s.split()
 allcaps=s.isupper()
 out=[]
 for i,w in enumerate(words):
  if w in KEEP:out.append(w);continue
  if w.lower() in SMALL and i and not words[i-1].endswith((':','—')):w=w.lower()
  elif allcaps:
   w=w.capitalize() if "'" in w else w.title()
  out.append(w)
 return ' '.join(out)

# IDs remain stable when a credited name or title is corrected.
EDITS={
 'cd-13-d1-01':('Orchester Peter Jacques','Hamburgers','Intro'),
 'cd-13-d1-02':('アーティスト未確認','Chante',''),
 'cd-13-d1-03':('Nuovo Sistema','In qualche maniera',''),
 'cd-13-d1-07':('Nina Shaw','Love So Fine',''),
 'cd-13-d1-08':('Betty Chung','Bye Bye Love',''),
 'cd-13-d1-09':('Ricky May','Tomorrow',''),
 'cd-13-d1-10':('Vince Tempera','La preda','Interlude'),
 'cd-13-d1-20':('TSU Jazz Ensemble','Jazzman','Interlude'),
 'cd-13-d1-22':('Berry Lipman & His Orchestra','I Like It',''),
 'cd-09-d1-03':('Fritz Maldener','Short Walk',''),
 'cd-09-d1-04':("Steve 'n' Leila",'You Made a Lover Out of Me',''),
 'cd-09-d1-07':('Dario Marcello','Rio mon amour',''),
 'cd-09-d1-08':('The Flying Machine',"Maybe We've Been Loving Too Long",'Interlude'),
 'cd-09-d1-09':('Las 4 Monedas y Gregory','Trauma',''),
 'cd-09-d1-10':('Rune Öfwerman','Hush',''),
 'cd-09-d1-11':('Noel Quinlan','I Shot the Sheriff',''),
 'cd-09-d1-13':('Wakefield Sun','Sing a Simple Song',''),
 'cd-09-d1-14':('Laura del Valle','I Got Love',''),
 'cd-09-d1-15':("Judge's Nephews",'Si Tu Querer',''),
 'cd-09-d1-19':('Ghalib Ghallab','Night in Tunisia',''),
 'cd-09-d1-20':('H.P. Riot','Do It for Yourself','Interlude'),
 'cd-09-d1-21':('Sergio Franchi','More',''),
 'cd-00-d1-12':('Paul Mauriat','La fête',''),
 'cd-00-d1-20':('Yehudit Ravitz','Taj Mahal','Interlude'),
 'cd-00-d2-07':('Gérard Baqué','Tant de nuits (Bitter Sweet Samba)',''),
 'cd-00-d2-09':('Ana Maria e Maurício','Figa de Guiné',''),
 'cd-00-d2-21':('Teddy Parker','Bossa Nova in Panama',''),
 'cd-00-d1-23':('Augusto Martelli','Summertime',''),
 'cd-00-d2-02':('Petula Clark','If I Were a Bell',''),
 'cd-02-d1-07':('Maggie Eaves Singers','I Will Wait for You',''),
 'cd-04-d1-06':('The Mirza Men','Eleanor Rigby',''),
 'cd-04-d1-17':('AViVA','Te Quiero Means I Love You',''),
 'cd-04-d1-19':('Roland Shaw Orchestra','Jump Up',''),
 'cd-04-d1-26':('Patty Weaver','Laughter in the Rain',''),
 'cd-07-d1-08':('Max Greger','Moliendo café',''),
 'cd-07-d1-11':('18th Century Concepts',"Can't Hurry Love",''),
 'cd-07-d1-17':('Elenore Ost','The Hustle','Interlude'),
 'cd-07-d1-18':('Brave Combo','The Hustle',''),
 'cd-07-d1-27':('Sandiego',"Can't Take My Eyes Off You",''),
 'cd-08-d1-20':('KG 22 Band',"Love the One You're With",''),
 'cd-08-d1-25':('Perry Dominguez','Billie Jean',''),
 'cd-10-d1-08':('Johnny Ray',"You're My Everything",'Interlude'),
 'cd-10-d1-10':('Doris',"Don't Let It Rain",''),
 'cd-10-d1-24':('Mona Richardson','California Soul',''),
 'cd-11-d1-03':('Ernie Castel 4 feat. Elaine Terzi','Mr. Weatherman',''),
 'cd-11-d1-15':('Monna Bell',"Swearin' to God",''),
 'cd-11-d1-26':('Two Nations','Independence',''),
 'cd-12-d1-05':('Erica & Chinquinho','Chattanooga Choo Choo',''),
 'cd-12-d1-13':('Cañones y Mantequilla','No me tomes el pelo',''),
 'cd-12-d1-27':('Chico Arnez, His Orchestra & Choir','A banda',''),
 'cd-13-d1-14':('Les Requins','Campus No. 8',''),
 'cd-13-d1-28':('Dynamite Brass','Fura de fila',''),
 'cd-13-d1-30':("Liz Damon's Orient Express",'Loneliness Remembers','Outro'),
 'cd-02-d1-03':('La Nueva Banda Santisteban','The Suitcase',''),
 'cd-09-d1-27':('April Set','Yesterday When I Was Young',''),
 'cd-14-d1-10':('Clarence Curvan Club','Rip Van Winkle','Interlude'),
 'cd-14-d1-11':('Edmundo Ros','London Is the Place for Me',''),
 'cd-14-d1-18':('The Manzanilla Sound',"Ain't No Mountain High Enough",''),
 'cd-14-d1-21':('Terry McCullough',"I've Got the Melody",''),
 'cd-01-d1-13':('Franck Fernandel','Un Américain dans les rues de Rio',''),
 '001-b-09':('Evinha (Eva)','Moon River',''),
 '003-b-02':('Monserate starring Lyda Zamora','Eso Beso',''),
 '004-a-02':('The Morgan-James','If It Comes to That',''),
 'cd-00-d2-05':('The Morgan-James','If It Comes to That',''),
 '003-b-09':('The Morgan-James Duo',"You Don't Know What Love Is",''),
 'cd-00-d2-27':('The Morgan-James Duo',"You Don't Know What Love Is",''),
 '005-a-04':('Stan Reynolds and His Orchestra','True Love',''),
 'cd-00-d2-03':('Stan Reynolds and His Orchestra','True Love',''),
 'cd-00-d1-03':('Daniela und Ann','The Pain in My Heart',''),
 'cd-00-d1-14':('Les Petits Chanteurs du Rock','Aquarela',''),
 'cd-03-d1-08':('Rhetta Hughes','Walk On By',''),
 'cd-11-d1-23':('Konstantin Orbelyen Orchestra','曲名未確認',''),
}
ALIASES={
 'lucifer and co.':'Lucifer and Co.', 'gerard baque':'Gérard Baqué',
 'portinho e sua orquestra':'Portinho e sua Orquestra',
 'frank fernandel':'Franck Fernandel',
 'armand trovajoli':'Armando Trovajoli',
 'daniel und ann':'Daniela und Ann',
 'april set feat. pecombo':'April Set feat. Pecombo',
 'steve jackson et son orchestra':'Steve Jackson et son orchestre',
 'jorge antonio alves et son orchestra':'Jorge Antonio Alves et son orchestre',
 'pete rugolo et son orchestre':'Pete Rugolo et son orchestre',
}
TITLES={
 'night and day':'Night and Day','baile en la noche':'Baile en la noche',
 'la fete':'La fête','la fête':'La fête', 'figa da guine':'Figa de Guiné',
 'moliendo cafe':'Moliendo café', 'copa sete no samba':'Copa Sete no Samba',
 'deixa isso pra lá':'Deixa isso pra lá', 'portami con te':'Portami con te',
 'if i were a bell':'If I Were a Bell', 'zozoi(italiana)':'Zozoï (Italian version)',
 'theme from "black belt jones"':'Theme from “Black Belt Jones”',
}
MARK = re.compile(r'^(intro(?:duce premium cuts)?|interlude)\s*(?:[.…~～—-]+)\s*',re.I)
ENDMARK=re.compile(r'\s*(?:[.…~～—-]+)\s*(outro|interlude)$',re.I)

def normalize_tracks(tracks):
 for t in tracks:
  t['artist']=clean(t['artist']);t['title']=clean(t['title'])
  for field in ('artist','title'):
   m=MARK.match(t[field])
   if m:t['mix_marker']='Intro' if m[1].lower().startswith('intro') else 'Interlude';t[field]=t[field][m.end():]
  m=ENDMARK.search(t['title'])
  if m:t['mix_marker']=m[1].capitalize();t['title']=t['title'][:m.start()]
  if t['id'] in EDITS:
   artist,title,marker=EDITS[t['id']];t.update(artist=artist,title=title)
   if marker:t['mix_marker']=marker
  artist=t['artist']
  if artist.isupper() and artist not in KEEP:
   artist=' '.join(w if w in KEEP else w.title() for w in artist.split())
  artist=re.sub(r"(?<=\w)'([ST])\b",lambda m:"'"+m[1].lower(),artist)
  artist=re.sub(r'\bfeat\.', 'feat.',artist,flags=re.I)
  t['artist']=ALIASES.get(artist.lower(),artist)
  t['title']=TITLES.get(t['title'].lower(),title_style(t['title']))
  if t['artist']=='アーティスト未記載':t['artist']='アーティスト未確認'
