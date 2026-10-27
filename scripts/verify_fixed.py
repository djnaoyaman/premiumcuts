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
assert len({t['videoId'] for t in public['audio']})==43
assert all(t['id'] not in (p/'dist/tracks.html').read_text().split('<main')[1] for t in m)
print('PASS fixed 675 Songs exact records/order, 33 Essentials order, baseline hashes, My-Spin isolation')

# Audio for an existing Songs entry does not add it to either curated collection.
assert next(t for t in public["audio"] if t["id"] == "001-a-02")["videoId"] == "8pQBEa4zRMw"
assert "001-a-02" not in json.load(open("features.json"))["essentials"]["track_ids"]
assert not any(t["videoId"] == "8pQBEa4zRMw" for t in public["myspin"])

# Explicit owner selection extends, never replaces, the original frozen list.
assert f['essentials_ids']==f['essentials_revision']['previous_essentials_ids']+['001-b-02']
assert len(f['essentials_ids'])==33
assert next(t for t in public['audio'] if t['id']=='001-b-02')['videoId']=='oDhgHoPfGNI'
assert '001-a-03' not in f['essentials_ids'] and '001-a-09' not in f['essentials_ids']

# Owner-designated videos attach to existing Songs only.
for track,video in [("001-b-10","KmptGhVdutA"),("001-b-11","W6_akbmZSpk"),("001-b-13","Epr8SGiUXxc"),("001-b-14","v2CIOv_4Mbk")]:
 assert next(t for t in public["audio"] if t["id"]==track)["videoId"]==video
 assert track not in f["essentials_ids"]
 assert not any(t["videoId"]==video for t in public["myspin"])
