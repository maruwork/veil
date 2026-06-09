# Basic Design

## Intent

detail branch の `選別/review` と `保留` はどちらも「今回どう扱うか」を示す action 系の補助情報であり、続けて読む意味が近い。別行のままだと保留寄り候補で縦に伸びるため、意味を変えず 1 行 compact へ寄せる。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- retention がある時は `選別/review/保留: <selection hint> | <selection reason> | <review hint> | <retention hint>` とする
- retention がない時は現行の `選別/review: ...` を維持する
- `判別` は分類根拠として独立行のまま維持する
- low-priority branch は現行 4 行 compact を維持する
- JSON payload は変更しない
