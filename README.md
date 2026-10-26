# Premium Cuts Listed

Masanori Suzuki（鈴木雅尭）によるPremium Cutsの収録曲アーカイブ。

## 現在の範囲

- カセット001–007の7作品・227曲目、MIX CD #00–#14の15タイトル・448曲目、合計22作品・675曲目
- 作品ごとのSide A／B・Discごとの曲順
- 曲名・アーティストによる横断検索
- 作品・Side絞り込み、曲名／アーティスト順の並べ替え
- 曲目ごとの固定URL
- ブルーとクリームのレスポンシブデザイン

掲載対象はPremium Cutsのトラックリストのみ。CRATE DIGGIN’は構成の参考であり、そこから楽曲を流用しない。

## 編集

`selection.tsv` がカセットの選曲データ。`cd_catalog.json` がMIX CDの選曲データ。`catalog.json` と `dist/data.js` は生成物。

```sh
python -m pip install Pillow
python build.py
python -m http.server 8000 --directory dist
```

`dist/` がビルド不要の静的サイト。スタイルと操作は `src/`。`dist/` は生成物です。

指定されたYouTube音源と、確認できた資料に基づく楽曲解説を掲載する。制作年、発売年、活動国、録音地、ジャンル、背景、関連音楽は、出典を確認して曲ごとに追加する。


## 共通PLAYER

CRATE DIGGIN’とsuburbia CLASSICAの共通操作を参考に、単一のYouTube IFrame APIプレーヤーを実装。前後の曲、停止、再生・一時停止、シーク、作品別の連続再生、VIDEO / ART / HYBRID全画面表示を提供します。配色はPremium Cuts Listedのブルーとクリームを維持します。

`research.json`の明示的な楽曲IDとYouTube IDを使います。別アーティストの同名曲は結合しません。全曲再生では同じ動画を重複させず、作品別再生ではトラックリスト順を維持します。再生対象は指定音源のある曲だけです。

`src/player.js`が再生と内部ナビゲーションを担当し、ページ閲覧ではプレーヤーと曲順を作り直しません。曲順変更は再生操作またはPLAYERの作品選択でのみ行います。「この曲を聴く」は共通プレーヤーにつながります。再生不可の指定動画も別動画へ自動差し替えせず、YouTubeリンクを残します。

`node scripts/verify_player.cjs`で作品別曲順、重複、API準備前の停止、再生・一時停止、次曲、終端、エラー、シークを検証します。実際の配信可否はブラウザと地域により異なるため、別途確認します。

## 開いたままの更新

公開カタログは`version.json`と`catalog-public.json`で配信します。プレーヤーは起動時、ページ移動時、タブに戻った際と60秒ごとに更新を確認し、PLAYERの「最新の曲を確認」からも取得できます。再生中のYouTubeインスタンスと現在の音源を保持し、既存の再生順を維持して追加音源を末尾に加えます。作品や全曲を選び直すと最新の収録順になります。更新取得に失敗しても既存の曲は消しません。

ヘッダーと装飾のマークはSVGで描画し、端末による絵文字への置換を避けています。


## Editorial names and articles

`catalog_style.py` applies shared song and artist display names before any HTML, search data or player queues are generated. Song titles lead and artist names follow. Intro, Interlude and Outro are mix annotations; they are never part of an artist name. IDs, positions and the 675 appearances stay stable. Original-language diacritics and official acronyms are retained; unverified identities remain explicit.

Name corrections were checked against the published Premium Cuts #09 and #13 tracklists at TICRO MARKET and Virus Pro, the #10 listing at Jet Set, original-release catalogs and the music sources linked in each article. Similar names alone are insufficient for merging performers or recordings.

Source-backed editorial coverage is now 477 distinct articles across 515 catalog appearances. The current research pass covered all 675 entries; 160 appearances remain unresolved pending recording, performer or source confirmation. Each new article includes its own headline, introduction, three detailed sections, internal related-track links and a bibliography.

All 24 selected recordings have editorial pages. The Berry Lipman normal and Disco recordings remain separate; their exact first issues and the Joe Pugliese cover release year remain unconfirmed. Dates are earliest verified releases for the relevant recording, never automatically composition, recording or remaster dates.

Validation includes `python build.py`, `node scripts/verify_player.cjs` and `python scripts/verify_catalog.py`.


## Record-shelf artwork

`artwork.py` supplies 23 original square SVG sleeves: seven tapes, fifteen mix CDs, and a dedicated Essentials feature. All use cobalt blue (#073DA8), warm ivory (#F4EFE5), consistent margins and sleeve typography. Flowing bands, quarter-circle modules, fine-line arcs, nested frames and negative-space patterns provide varied compositions across the series. Stable data-art IDs keep each cover identical on the home shelf, volume pages and track pages. The responsive cover containers stay square so the art is never cropped; the existing single-column mobile shelf and broader desktop/tablet layouts are preserved.

## Premium Cuts Essentials

`features.json` fixes DJ Naoyaman’s selected 24 recordings as an editorial feature. `/features/essentials.html` lists one entry per recording, with play, essay and mix links. Home and navigation link to the feature; matching appearances carry the Essentials badge and can be filtered in the catalog. Future player additions do not automatically join the selection.

## Explicit audio additions

`audio_sources.json` stores later user-specified YouTube recordings by stable catalog track ID. The builder merges these after the researched sources and includes the file in the public catalog version, so open players can receive the additions. This does not change the fixed Essentials selection.

`editorial_updates.json` adds later source-backed notes without replacing the larger research archive. Reference recordings are rendered as explicit external links and never added to the mix playback queue.
