# VEIL 正規化判別補助 実装計画

Status: Draft
Date: 2026-06-07

## 1. ゴール

`veil-normalize.py` の出力に、頻度と並んで軽い判別補助を表示する。

## 2. 道のり

1. 判別補助 helper を追加する
2. cluster 結果へ補助ラベルと理由を追加する
3. text / json 出力へ反映する
4. 文書へ注意書きを足す
5. 軽い smoke を行う

## 3. タスク

1. `veil-normalize.py` に `classification_hint` helper を追加する
2. 代表表記ベースで補助ラベルと理由を返す
3. README / 設計書 / skill に補足を追加する
4. `--text` で識別子候補 / 固有名候補 / 説明語候補 / 境界が曖昧な候補の smoke を行う

## 4. 検査

- `python -m py_compile veil-normalize.py`
- `python veil-normalize.py --text "status=close\nSQLite\ncurrent state\nclose-ish"` で補助ラベルが見える
- `python veil-normalize.py --json --text "..."` で `classification_hint` と `classification_reason` が出る

## 5. 完了の定義

- 頻度を見る前に「何の種類の語か」をざっと切れる
- ただし最終判定は user 側に残る
