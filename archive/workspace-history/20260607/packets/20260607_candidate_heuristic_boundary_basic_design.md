# Basic Design

## Problem

`normalize` の細かい閾値や phrase / single-word の保守化条件が、user confirmation を経ないまま authority surface で強いルールとして読める状態になっている。

## Direction

- 土台実装は残す
- candidate threshold の細則は provisional heuristic へ格下げする
- どこまでが foundation で、どこからが未承認 heuristic かを current / README / design へ明記する

## Foundation

- SQLite canonical migration
- `lint / normalize / audit / sync` の mainline 整理
- `必須 / 推奨 / 観察` の level 契約
- retention hint / shortlist / compact output の存在

## Provisional Heuristic

- repeated single-word 一般語の threshold
- lowercase phrase の threshold
- single-word / phrase の candidate 昇格回数
- `capture` と `normalize` のどちらで厳しく落とすかの細線引き
