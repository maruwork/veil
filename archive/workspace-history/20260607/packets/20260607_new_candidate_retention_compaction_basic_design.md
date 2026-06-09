# Basic Design

## Intent

保留候補では `保留処理` と `保留理由` が 2 行に分かれていて、detail branch の読み行数がまだ多い。意味を落とさず一行 compact に寄せる。

## Chosen Shape

- `保留: 後で再観察する | 説明語候補だが頻度か困り度が足りず、次の再出現を待つ`

## Non-Goals

- 保留情報の削除
- low-priority compact branch の統合
- JSON compact 化

