# Basic Design

## Intent

detail branch の `priority` と `level` はどちらも採用強度の入口情報であり、前後関係が近い。別行のままだと review 時の視線移動が増えるため、意味を変えず 1 行 compact へ寄せる。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- 表示は `priority/level: <priority> | <level> | <reason>` とする
- low-priority branch は現行 4 行 compact を維持する
- JSON payload は変更しない
