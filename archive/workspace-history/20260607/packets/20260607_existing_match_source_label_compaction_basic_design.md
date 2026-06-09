# existing-match source label compaction basic design

## Intent

grouped source header の意味は保持したまま、独立 header の文字数を減らす。file 名そのものを header と見なせるので、`source:` 接頭辞は省略する。

## Design

1. grouped `existing-match` source header を `f"{source_file}:"` にする
2. 1 件 source の item 行末 `| source: <file>` はそのまま維持する
3. JSON 出力は変更しない
4. docs / skills には「複数件 source の時は file 名 header を見る」と書く

## Invariants

- grouped source だけ独立 header を持つ
- 1 件 source は item 行末で source を読む
- source grouping 件数や item 並び順は変えない
