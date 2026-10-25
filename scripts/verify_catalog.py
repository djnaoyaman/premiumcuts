"""Regression checks for credited names, recording coverage and public output."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
c=json.loads((root/'catalog.json').read_text());r=json.loads((root/'research.json').read_text())
byid={t['id']:t for t in c['tracks']}
assert len(c['tracks'])==len(byid)==675
assert (byid['cd-13-d1-01']['artist'],byid['cd-13-d1-01']['title'])==('Orchester Peter Jacques','Hamburgers')
assert (byid['cd-13-d1-03']['artist'],byid['cd-13-d1-03']['title'])==('Nuovo Sistema','In qualche maniera')
assert byid['cd-13-d1-07']['artist']=='Nina Shaw'
assert byid['cd-00-d2-02']['title']=='If I Were a Bell'
assert byid['cd-10-d1-24']['title']=='California Soul'
assert byid['cd-09-d1-27']['artist']=='April Set'
articles={i:a for a in r['articles'] for i in a['ids']};players=dict(r['players'])
for a in r['articles']:
 if a.get('youtube'):
  for i in a['ids']:players[i]=a['youtube']
 for i,_ in a['related']:assert i in byid,i
 for _,_,refs in a['sections']:assert all(1<=n<=len(a['sources']) for n in refs)
assert len({v['id'] for v in players.values()})==23
assert all(i in articles for i in players)
assert players['006-b-08']['id']=='xHVpXZHupHA'
assert players['cd-00-d1-21']['id']=='JNbxvLowZD8'
for t in byid.values():
 assert not re.search(r'^(intro|interlude)[.…~～]',t['artist'],re.I),t
 assert not re.search(r'\s{2,}',t['artist']+t['title']),t
for f in (root/'dist').rglob('*'):
 if f.suffix not in ('.html','.json','.js'):continue
 text=f.read_text()
 assert all(x.lower() not in text.lower() for x in ('listed.xlsx','DOCUMENT ORIGINAL','ご提供いただいた','source_row','source_name')),f
print(f'PASS 675 entries; 23 recording articles; {len(articles)} article pages; independent versions; public output scan')
