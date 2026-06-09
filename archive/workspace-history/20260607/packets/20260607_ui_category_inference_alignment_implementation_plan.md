# VEIL UI カテゴリ自動推定整合 実装計画

Status: Draft
Date: 2026-06-07

## 1. ゴール

UI のカテゴリ自動推定を、現在の判別補助と同じ方向へ寄せる。

## 2. 道のり

1. `inferCat()` の判定順を見直す
2. manual の推定説明を更新する
3. 必要な文書補足を入れる
4. 軽い smoke を行う

## 3. タスク

1. `ui/js/convert.js` の `inferCat()` を更新する
2. `docs/manual.html` のカテゴリ推定表を更新する
3. 必要なら設計書に cat 推定方針を追記する
4. Node か browser 不要の軽い JS smoke を行う

## 4. 検査

- `inferCat("status=close") -> 2`
- `inferCat("path/to/close.md") -> 2`
- `inferCat("SQLite") -> 5`
- `inferCat("current state") -> 1`
- `inferCat("close-ish") -> 7`
- `inferCat("close") -> 7`

## 5. 完了の定義

- UI 側の自動推定が慎重側へ倒れ、`veil-normalize.py` と逆向きにならない
