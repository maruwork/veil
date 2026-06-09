# Basic Design

## Intent

detail branch の `variants` と `target` はどちらも書き込み判断の補助情報であり、前後関係が近い。別行のままだと review 時の視線移動が増えるため、意味を変えず 1 行 compact へ寄せる。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- 表示は `variants/target: <variant summary> | <target file>` とする
- low-priority branch は現行 4 行 compact を維持する
- JSON payload は変更しない
