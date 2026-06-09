# Basic Design

## Intent

`existing-match` の `表記ゆれ:` は重要だが、`normalized` と同一の単一 variant が 1 回だけなら新情報がない。そこでそのケースだけ省略し、情報価値がある時だけ残す。

## Design

- text 出力の `existing-match` branch だけを変更する
- `variant_counts` が 1 件で、sole variant を正規化した値が `normalized` と一致し、count が 1 の時だけ `表記ゆれ:` を出さない
- それ以外は現行どおり `| 表記ゆれ: ...` を維持する
- source suffix / source header の出し分けは現行のまま維持する
- JSON payload は変更しない
