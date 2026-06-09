# VEIL vocab.db 監査補助 実装計画

Status: Draft
Date: 2026-06-07

## 1. ゴール

既存 `vocab.db` がある時に、cleanup 前の監査材料を非破壊で出せるようにする。

## 2. 道のり

1. 監査スクリプトを追加する
2. 判別補助と seed 集合を接続する
3. text / json 出力を整える
4. 文書に使い方を追記する
5. 無DB時と仮DB時の smoke を行う

## 3. タスク

1. `veil-audit-db.py` を追加する
2. 無DB時の `skip` を入れる
3. 仮DBで `keep / review / drop-candidate` を確認する
4. README / 設計書 / manual に補助の位置づけを書く

## 4. 検査

- `python -m py_compile veil-audit-db.py`
- DB なしで `skip`
- 仮DBで text / json 両方の出力確認

## 5. 完了の定義

- 将来 `vocab.db` があった時に、その場で安全に監査できる
