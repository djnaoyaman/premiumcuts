from pathlib import Path
import re
snippet='''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-H3JRZ1NCM9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-H3JRZ1NCM9');
</script>'''
files=list(Path('dist').rglob('*.html'))
assert files
for f in files:
 s=f.read_text();head=s.split('</head>')[0]
 assert s.count(snippet)==1 and snippet in head,f
 assert s.count('googletagmanager.com/gtag/js?id=')==1,f
 assert s.count("gtag('config',")==1,f
 for name in ['analytics.js','analytics-privacy.js']:
  assert len(re.findall(r'<script[^>]+src="[^"]*/'+re.escape(name)+r'\?',s))==1,f
  assert name in head,f
 assert head.index('analytics-privacy.js')<head.index(snippet),f
for name in ['analytics.js','analytics-privacy.js']:
 assert Path('dist',name).read_bytes()==Path('src',name).read_bytes(),name
print(f'PASS exact Google tag/config and analytics assets once in head across {len(files)} pages')
