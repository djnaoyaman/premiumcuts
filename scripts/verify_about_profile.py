from pathlib import Path
import json,re
p=Path(__file__).resolve().parents[1]
c=json.loads((p/'about_profile.json').read_text());s=(p/'dist/about.html').read_text()
assert s.index('class="about-profile"') < s.index('class="about-gallery"')
assert s.count('class="about-profile"')==1 and s.count('class="about-poster"')==20
assert '<details class="profile-details"' not in s
for text in [c['name'],c['lead']]: assert text in s
assert len(c['lead'])<150 and len(c['links'])==1
assert c['links'][0]['url']=='https://djnaoyaman.github.io/profile.html'
assert '鈴木雅尭' in s and 'サイト編集' in s
for old in ['15歳','足立区','叔父','大学時代','妻と聴いた','マーケティングやブランディング','SAYAとは同級生','about-gallery-story','about-gallery-coda']:
 assert old not in s,old
assert 'dateModified' in s and 'site-updated' in s
print('PASS: compact intent-led site-editor profile, central author link, selector distinction, 20 posters retained')
