# source label path compaction basic design

## Intent

text 出力の最初の 1 行は overview 用なので、full path を毎回出さず、人が識別できる短い label に寄せる。

## Design

1. rules-dir source の text label は path basename 優先で短く表示する
2. db source の text label も path basename 優先で短く表示する
3. JSON の `source` と `source_type` は変更しない
4. docs / skills では text label は source 名だけを読む契約にする

## Invariants

- text だけを compact 化する
- JSON 契約 unchanged
- source type の判別は維持する
