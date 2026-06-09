# Basic Design

## Intent

`existing-match` は既存統合先が確定しているため、候補検討の主対象ではない。source ごとの grouping を残したまま、一件ごとの表示をさらに短くする。

## Chosen Shape

- source header:
  - `source: c.md (2件)`
- item line:
  - `- normalized -> preferred [level] | 表記ゆれ: ...`

## Non-Goals

- source header の除去
- JSON compact 化
- level や source 情報の削除

