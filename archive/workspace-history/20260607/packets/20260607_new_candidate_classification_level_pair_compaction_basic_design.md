# Basic Design

## Intent

detail branch の `判別` と `priority/level` はどちらも「その候補をどの強さでどう見るか」を示す分類面の情報であり、続けて読む意味が近い。別行のままだと視線が縦に伸びるため、意味を変えず 1 行 compact へ寄せる。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- 表示は `判別/priority/level: <classification hint> | <classification reason> | <priority> | <level>` とする
- `variants/target` は独立行のまま維持する
- action 系の `選別/review` / `選別/review/保留` は現行のまま維持する
- low-priority branch は現行 4 行 compact を維持する
- JSON payload は変更しない
