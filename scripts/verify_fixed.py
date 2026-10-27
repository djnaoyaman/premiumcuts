"""Keep source archive identity/order separate from derived My-Spin and audio URLs."""
from pathlib import Path
import json,hashlib,csv,io
p=Path(__file__).resolve().parents[1]
f=json.loads((p/'baselines/premiumcuts-fixed.json').read_text())
c=json.loads((p/'catalog.json').read_text()); v={v['id']:v for v in c['volumes']}
actual=[dict(order=n,id=t['id'],work_id=t['volume'],work_title=v[t['volume']]['title'],format=t['format'],side=t['side'],position=t['position'],artist=t['artist'],title=t['title'],source='selection.tsv' if t['format']=='tape' else 'cd_catalog.json') for n,t in enumerate(c['tracks'],1)]
assert actual==f['songs'], 'Fixed Songs identity, metadata or order changed'
assert json.loads((p/'features.json').read_text())['essentials']['track_ids']==f['essentials_ids'], 'Fixed Essentials changed'
for line in (p/'baselines/SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  '); assert hashlib.sha256((p/'baselines'/name).read_bytes()).hexdigest()==digest,name
m=json.loads((p/'myspin.json').read_text());ids={t['id'] for t in m}
assert len(ids)==len(m) and not ids.intersection(t['id'] for t in actual)
public=json.loads((p/'dist/catalog-public.json').read_text())
assert public['myspin']==m and len(public['tracks'])==675
assert not ids.intersection(t['id'] for t in public['audio'])
preserved=json.loads((p/'baselines/audio-preserved.json').read_text())
actual_audio={t['id']:t['videoId'] for t in public['audio']}
assert all(actual_audio.get(k)==v for k,v in preserved.items()), 'Previously selected recording changed'
assert len(actual_audio)==len(public['audio']), 'Duplicate audio track ID'
assert set(actual_audio).issubset(t['id'] for t in actual), 'Audio outside fixed Songs'
assert all(t['id'] not in (p/'dist/tracks.html').read_text().split('<main')[1] for t in m)
print('PASS fixed 675 Songs exact records/order, 35 Essentials order, baseline hashes, My-Spin isolation')

# Audio for an existing Songs entry does not add it to either curated collection.
assert next(t for t in public["audio"] if t["id"] == "001-a-02")["videoId"] == "8pQBEa4zRMw"
assert "001-a-02" not in json.load(open("features.json"))["essentials"]["track_ids"]
assert not any(t["videoId"] == "8pQBEa4zRMw" for t in public["myspin"])

# Explicit owner revision: one removal, then fixed Songs order.
previous=f['essentials_revision']['previous_essentials_ids']
assert set(previous)-set(f['essentials_ids'])=={'006-b-08'}
assert not set(f['essentials_ids'])-set(previous)
assert len(f['essentials_ids'])==35
source_order={t['id']:t['order'] for t in f['songs']}
assert f['essentials_ids']==sorted(f['essentials_ids'],key=source_order.get)
assert '006-b-08' in {t['id'] for t in public['tracks']}
assert next(t for t in public['audio'] if t['id']=='006-b-08')['videoId']
assert not next(t for t in public['tracks'] if t['id']=='006-b-08')['essentials']
assert 'cd-00-d1-21' in f['essentials_ids']
for track,video in [('001-a-03','oIBZHTDOuwo'),('001-a-09','v4q7wC_LSeg'),('001-b-07','houkrNCo1sQ')]:
 assert next(t for t in public['audio'] if t['id']==track)['videoId']==video
 assert not any(t['videoId']==video for t in public['myspin'])

# Owner-designated videos attach to existing Songs only.
for track,video in [("001-b-10","KmptGhVdutA"),("001-b-11","98zvoTetV3Y"),("001-b-13","Epr8SGiUXxc"),("001-b-14","v2CIOv_4Mbk")]:
 assert next(t for t in public["audio"] if t["id"]==track)["videoId"]==video
 assert track not in f["essentials_ids"]
 assert not any(t["videoId"]==video for t in public["myspin"])
