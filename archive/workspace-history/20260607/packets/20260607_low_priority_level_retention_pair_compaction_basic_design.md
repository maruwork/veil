# Basic Design

## Intent

low-priority branch はもともと圧縮済みだが、`level 提案` と `保留処理` は low-priority の判断軸として続けて読む意味が近い。別行のままだと still 4 行なので、意味を変えず 1 行 compact へ寄せる。

## Design

- low-priority branch の text 出力だけを変更する
- 表示は `level/保留処理: <level> | <retention>` とする
- `target: ...` は独立行のまま維持する
- non-low-priority / existing-match / JSON は変更しない
