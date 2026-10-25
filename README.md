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
