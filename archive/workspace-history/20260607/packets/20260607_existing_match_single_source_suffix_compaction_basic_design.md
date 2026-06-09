# existing-match single source suffix compaction basic design

## Intent

grouped source header を file 名 header にした流れに合わせて、single-source existing-match も file 名だけで source を示す。

## Design

1. single-source existing-match line suffix を `| source: <file>` から `| <file>` にする
2. grouped source header `c.md:` は維持する
3. JSON 出力は変更しない
4. docs / skills には「1 件 source は行末 file suffix を見る」と書く

## Invariants

- existing-match 本文の `normalized -> preferred [level]` 形式は維持する
- `表記ゆれ` 省略条件は変えない
- grouped source と single-source の見分けは維持する
