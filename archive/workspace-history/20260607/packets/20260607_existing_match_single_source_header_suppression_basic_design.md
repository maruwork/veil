# Basic Design

## Intent

source header は grouping に有効だが、1 件しかない場合は独立行の価値が低い。1 件 source だけを line suffix 化し、複数件 source の grouping 効果は維持する。

## Design

- text 出力の `existing-match` branch だけを変更する
- source file ごとの件数が 1 件の時は header 行を出さない
- 1 件 source の `existing-match` 行は `... | 表記ゆれ: ... | source: <file>` とする
- 2 件以上の source は現行の `source: <file> (<count>件)` header を維持する
- JSON payload は変更しない
