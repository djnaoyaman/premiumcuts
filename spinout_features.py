"""Sourced reading features over existing recordings; never add catalog members."""
from html import escape as e


def render_one_note_samba(dist, feature, myspin, head, header, footer):
    ids = [v['id'] for v in feature['versions']]
    recordings = [t for t in myspin if t['id'] in ids]
    assert [t['id'] for t in recordings] == ids and len(ids) == len(set(ids)) == 10
    assert all('berimbau' not in t['id'] for t in recordings)
    sources = {s['id']: s for s in feature['sources']}
    numbers = {sid: n for n, sid in enumerate(sources, 1)}

    def citations(ids):
        return '<span class="feature-citations">' + ' '.join(
            f'<a href="#source-{sid}" aria-label="出典 {numbers[sid]}：{e(sources[sid]["label"])}">[{numbers[sid]}]</a>'
            for sid in ids) + '</span>' if ids else ''

    story = ''.join(f'<section><h2>{e(s["heading"])}</h2><p>{e(s["text"])} {citations(s["sources"])}</p></section>' for s in feature['sections'])
    versions = ''
    for n, (track, annotation) in enumerate(zip(recordings, feature['versions']), 1):
        versions += f'''<li class="spinout-version"><span class="eyebrow">VERSION {n:02} / {track['year']}</span>
<h3><a href="/tracks/{track['id']}.html">{e(track['artist'])} ↗</a></h3><p class="spinout-version-title">{e(track['title'])}</p>
<p class="spinout-version-album">{e(track['album'])}</p><p>{e(track['note'])} {citations(annotation['sources'])}</p>
<button type="button" class="pc-play-button" data-play-id="{track['id']}" data-play-scope="feature:one-note-samba" aria-label="{e(track['artist'])}の{e(track['title'])}をこの特集で聴く">▶ この版を聴く</button>
<a class="text-link" href="{e(track['url'])}" target="_blank" rel="noopener noreferrer">YouTubeで開く ↗</a></li>'''
    references = ''.join(f'<li id="source-{sid}"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["label"])} ↗</a></li>' for sid, s in sources.items())
    page = head('One Note Samba — 一音から、いくつもの景色へ。 | Premium Cuts Listed', feature['dek'], '/features/one-note-samba.html')
    page += '<body id="top">' + header('myspin') + f'''<main id="main" class="wrap spinout-feature-page">
<section class="essentials-heading"><div><span class="eyebrow">SPINOUT / ONE SONG, TEN VERSIONS</span>
<h1>One Note<br><i>Samba.</i></h1><p class="song-lead">{e(feature['subtitle'])}</p><p>{e(feature['dek'])}</p></div></section>
<div class="spinout-story"><span class="eyebrow">THE STORY</span><div>{story}</div></div>
<section class="spinout-versions" aria-labelledby="feature-versions-title"><div class="section-heading"><div><span class="eyebrow">LISTEN!!! / 10 VERSIONS</span><h2 id="feature-versions-title">同じ曲を、聴き比べる。</h2></div></div>
<p class="list-note">{e(feature['display_note'])}</p><p>このページの再生は、以下の10版だけをSpinoutの選曲順でたどります。</p><ol class="spinout-version-list">{versions}</ol></section>
<section class="spinout-references" aria-labelledby="feature-references-title"><h2 id="feature-references-title">参考資料・出典</h2><ol>{references}</ol></section>
<p><a class="text-link" href="/my-spin.html">Spinoutの11曲へ戻る ↗</a></p></main>''' + footer() + '</body></html>'
    (dist / 'features/one-note-samba.html').write_text(page)
    return f'''<section class="spinout-features" aria-labelledby="spinout-features-title"><div class="section-heading"><div><span class="eyebrow">SPINOUT STORIES</span><h2 id="spinout-features-title">ひとつの曲から。</h2></div><p>その歴史を読み、いくつもの演奏を聴く。</p></div>
<div class="spinout-feature-shelf" tabindex="0" role="region" aria-label="同じ曲をめぐる特集"><a class="spinout-feature-card" href="/features/one-note-samba.html"><span class="eyebrow">FEATURE 01 / 10 VERSIONS</span><h3>One Note<br><i>Samba.</i></h3><p>{e(feature['subtitle'])}</p><span class="text-link">歴史を読む・聴き比べる ↗</span></a></div></section>'''
