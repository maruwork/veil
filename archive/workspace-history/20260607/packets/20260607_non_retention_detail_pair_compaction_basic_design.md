# Basic Design

## Intent

retention がない候補では、action 系と分類面を分けておく必要が弱く、2 行が連続して残る。そこで non-retention case に限って 1 行へ寄せ、retention がある候補の読み分けは維持する。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- retention がない時は `選別/review/判別/priority/level: <selection hint> | <selection reason> | <review hint> | <classification hint> | <priority> | <level>` とする
- retention がある時は現行の 2 行構成を維持する
- `variants/target` と headline は現行のまま維持する
- JSON payload は変更しない
