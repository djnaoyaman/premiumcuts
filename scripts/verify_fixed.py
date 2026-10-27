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
assert len({t['videoId'] for t in public['audio']})==37
assert all(t['id'] not in (p/'dist/tracks.html').read_text().split('<main')[1] for t in m)
print('PASS fixed 675 Songs exact records/order, 32 Essentials order, baseline hashes, My-Spin isolation')
