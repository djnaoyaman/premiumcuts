# Premium Cuts Listed

Masanori Suzuki（鈴木雅尭）によるPremium Cutsの収録曲アーカイブ。

## 現在の範囲

- Premium Cuts 001–007、7作品・227曲目（イントロ、ジングル、CMなどを除く）
- 作品ごとのSide A／Bと曲順、原資料画像
- 曲名・アーティスト・原表記による横断検索
- 作品・Side絞り込み、曲名／アーティスト順の並べ替え
- 曲目ごとの固定URLと表記の修正記録
- ブルーとクリームのレスポンシブデザイン

掲載対象は提供されたPremium Cutsのトラックリストのみ。CRATE DIGGIN’は構成の参考であり、そこから楽曲を流用しない。

## 編集

`selection.tsv` が画像から読み取った選曲データ。確定した綴りの修正と照合待ちの注記は `build.py` に保持。`catalog.json` と `dist/data.js` は生成物。

```sh
python -m pip install Pillow
python build.py
python -m http.server 8000 --directory dist
```

`dist/` がビルド不要の静的サイト。スタイルと操作は `src/`、原資料画像は `source-images/001.jpg`〜`007.jpg` に保存。`dist/` は生成物です。

現段階ではYouTube埋め込みと詳しい楽曲解説を実装しない。制作年、発売年、活動国、録音地、ジャンル、背景、関連音楽は、出典を確認して曲ごとに追加する。
