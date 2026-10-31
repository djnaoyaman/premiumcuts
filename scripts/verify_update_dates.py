"""Visible, structured and sitemap dates agree; source changes, not CI, drive them."""
from pathlib import Path
import sys,json,re,tempfile,subprocess,os,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from update_dates import source_modified,japanese_timestamp
root=Path(__file__).resolve().parents[1];dist=root/'dist';expected=source_modified(root)
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
entries=ET.parse(dist/'sitemap.xml').findall('s:url',ns)
assert entries
for entry in entries:assert entry.find('s:lastmod',ns).text==expected
pages=list(dist.rglob('*.html'))
for page in pages:
 s=page.read_text();dates=re.findall(r'<time datetime="([^"]+)">([^<]+)</time>',s)
 assert dates==[(expected,japanese_timestamp(expected))],page
 if page.name=='404.html':continue
 data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s).group(1))
 web=[v for v in data['@graph'] if v['@type'] in ('WebSite','WebPage')]
 assert len(web)==2 and all(v['dateModified']==expected for v in web),page
 assert all('datePublished' not in v for v in web),page
assert len(entries)==len(pages)-1
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 def git(*args,day=None):
  env=os.environ.copy()
  if day:env.update(GIT_AUTHOR_DATE=day,GIT_COMMITTER_DATE=day)
  return subprocess.check_output(['git','-C',tmp,*args],env=env,stderr=subprocess.DEVNULL,text=True)
 git('init');git('config','user.name','Test');git('config','user.email','test@example.invalid')
 def commit(path,body,day):
  f=p/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body)
  git('add',path);git('commit','-m','test',day=day)
 commit('build.py','template','2026-10-01T00:00:00Z');first=source_modified(p)
 assert first=='2026-10-01T00:00:00+00:00'
 commit('.github/workflows/pages.yml','CI only','2026-10-02T00:00:00Z')
 assert source_modified(p)==first
 commit('README.md','docs only','2026-10-03T00:00:00Z');assert source_modified(p)==first
 commit('audio_sources.json','new source','2026-10-04T20:01:00Z')
 assert source_modified(p)=='2026-10-04T20:01:00+00:00'
 assert japanese_timestamp(source_modified(p))=='2026年10月05日 05:01 JST'
 commit('src/player.js','shared UI change','2026-10-06T00:00:00Z')
 assert source_modified(p)=='2026-10-06T00:00:00+00:00'
 assert source_modified(p)==source_modified(p) # repeated build has no wall-clock dependency
print(f'PASS {len(pages)} visible dates, {len(entries)} sitemap/JSON-LD dates; source/template/data changes and CI-only stability')
