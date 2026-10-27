"""Regression checks for credited names, recording coverage and public output."""
from pathlib import Path
from datetime import date
import json,re
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'catalog.json').read_text());r=json.loads((root/'research.json').read_text())
r['articles']+=json.loads((root/'editorial_updates.json').read_text())['articles']
byid={t['id']:t for t in c['tracks']}
assert byid['001-a-11']['title']=='Chanson des jumelles (Version instrumentale)'
assert byid['001-a-11']['artist']=='Julian Barey Orchestra'
assert byid['005-a-16']['artist']=='Dieter Reith Orchestra'
assert byid['005-a-16']['essentials'] and not byid['005-a-16']['remix']
assert len(c['tracks'])==len(byid)==675
assert (byid['cd-13-d1-01']['artist'],byid['cd-13-d1-01']['title'])==('Orchester Peter Jacques','Hamburgers')
assert (byid['cd-13-d1-03']['artist'],byid['cd-13-d1-03']['title'])==('Nuovo Sistema','In qualche maniera')
assert byid['cd-13-d1-07']['artist']=='Nina Shaw'
assert byid['cd-00-d2-02']['title']=='If I Were a Bell'
assert byid['cd-10-d1-24']['title']=='California Soul'
assert byid['cd-09-d1-27']['artist']=='April Set'
assert byid['002-b-05']['artist']=='Les Miladys'
assert byid['003-a-05']['artist']=='Uno Loop'
assert byid['003-b-13']['artist']=='Douglas Westlund & Kjell Öhman'
assert byid['003-a-08']['title']=='Dansa (Chante… comme si tu devais mourir)'
assert byid['002-b-08']['title']=='Aquarella'
articles={i:a for a in r['articles'] for i in a['ids']};players=dict(r['players'])
assert len(articles)==sum(len(a['ids']) for a in r['articles']), 'Duplicate editorial track ID'
assert len({a['catch'] for a in r['articles']})==len(r['articles']), 'Repeated editorial headline'
for a in r['articles']:
 assert a['ids'] and all(i in byid for i in a['ids']), a['ids']
 assert len(a['sections'])>=3 and a['intro'] and a['sources'], a['ids']
 assert a.get('year') is None or (isinstance(a['year'],int) and 1900<=a['year']<=date.today().year), a['ids']
 assert all(s['url'].startswith(('https://','http://')) and s['label'] and s['note'] for s in a['sources']), a['ids']
 if a.get('youtube'):
  for i in a['ids']:players[i]=a['youtube']
 for i,_ in a['related']:assert i in byid,i
 for _,_,refs in a['sections']:assert all(1<=n<=len(a['sources']) for n in refs)
players.update(json.loads((root/'audio_sources.json').read_text()))
assert len({v['id'] for v in players.values()})==46
explicit_sources=json.loads((root/'audio_sources.json').read_text())
assert all(i in articles or i in explicit_sources for i in players)
assert all(i in byid for i in explicit_sources)
for i in ('cd-01-d1-08','cd-05-d1-19'):
 assert byid[i]['remix'] and not byid[i]['essentials']
assert players['001-a-11']['id']=='i5qBz24yrAU'
assert byid['001-a-11']['artist']=='Julian Barey Orchestra'
assert players['006-b-08']['id']=='xHVpXZHupHA'
assert players['cd-00-d1-21']['id']=='JNbxvLowZD8'
for t in byid.values():
 assert not re.search(r'^(intro|interlude)[.…~～]',t['artist'],re.I),t
 assert not re.search(r'\s{2,}',t['artist']+t['title']),t
for f in (root/'dist').rglob('*'):
 if f.suffix not in ('.html','.json','.js'):continue
 text=f.read_text()
 assert all(x.lower() not in text.lower() for x in ('listed.xlsx','DOCUMENT ORIGINAL','ご提供いただいた','source_row','source_name')),f
print(f'PASS 675 entries; 35 selected recordings; {len(articles)} article pages; independent versions; public output scan')
