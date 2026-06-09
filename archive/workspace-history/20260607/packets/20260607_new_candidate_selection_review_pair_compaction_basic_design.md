# Basic Design

## Intent

detail branch の `選別` と `review` はどちらも「今回どの扱いに寄せるか」を示す review 補助情報であり、並べて読む意味が近い。別行のままだと review 時の視線移動が増えるため、意味を変えず 1 行 compact へ寄せる。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- 表示は `選別/review: <selection hint> | <selection reason> | <review hint>` とする
- `判別` は分類根拠として独立行のまま維持する
- low-priority branch は現行 4 行 compact を維持する
- JSON payload は変更しない
