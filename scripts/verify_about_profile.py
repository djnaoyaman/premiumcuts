from pathlib import Path
from html.parser import HTMLParser
import json
p=Path(__file__).resolve().parents[1]
c=json.loads((p/'about_profile.json').read_text());s=(p/'dist/about.html').read_text()
assert 'provenance' not in c
assert s.index('class="about-profile"') < s.index('class="about-gallery"')
assert s.count('class="about-profile"')==1 and s.count('class="about-poster"')==20
assert '<details class="profile-details"><summary>' in s and '<details class="profile-details" open' not in s
for text in [c['name'],c['lead'],*c['paragraphs']]: assert text in s
assert len(c['paragraphs'])==3
assert '各作品の模様は、このサイト独自にデザインしたものです' not in s
css=(p/'src/style.css').read_text();assert 'prefers-reduced-motion:reduce' in css and '.profile-details::details-content{transition:none}' in css
assert 'height:auto' in css and 'content-visibility .28s allow-discrete' in css
print('PASS: approved profile, native closed disclosure, 20 posters retained, reduced-motion fallback')

assert 'about-gallery-story' not in s and 'about-gallery-coda' not in s
assert 'SAYAとは同級生' not in s
