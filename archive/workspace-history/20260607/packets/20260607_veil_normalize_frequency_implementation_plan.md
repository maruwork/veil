# VEIL 正規化頻度補助 実装計画

Status: Draft
Date: 2026-06-07

## 1. ゴール

`veil-normalize.py` から、候補語の揺れ統合に加えて頻度と採用順目安を読めるようにする。

## 2. 道のり

1. 入力保持方法を重複込みへ変える
2. cluster 集計へ回数情報を足す
3. text / json 出力へ頻度情報を足す
4. 文書側へ補足を反映する
5. 最低限の smoke を行う

## 3. タスク

1. `veil-normalize.py` の candidate 読み取りを変更する
2. `cluster_candidates()` の返却値へ回数情報を追加する
3. 頻度目安 helper を追加する
4. README / 設計書 / skill の説明を更新する
5. `--text` 入力で頻度集計の smoke を行う

## 4. 検査

- `python -m py_compile veil-normalize.py`
- `python veil-normalize.py --text "current state\ncurrent states\ncurrent state"` で回数が見える
- `python veil-normalize.py --json --text "..."` で `occurrence_count` と `variant_counts` が出る

## 5. 完了の定義

- 段階導入の最初の判断材料として頻度が見える
- 文書と実装の説明が一致している
