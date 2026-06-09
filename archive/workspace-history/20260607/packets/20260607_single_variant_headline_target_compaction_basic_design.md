# Basic Design

## Intent

single-variant 候補では、headline の `normalized [level] x<count>` と `variants: variant x<count>` がほぼ同じ情報になりやすい。そこで冗長ケースだけ `target` を headline へ寄せ、detail 行を 1 行減らす。

## Design

- non-low-priority `new-candidate` の text 出力だけを変更する
- `variant_count == 1` かつ sole variant が `normalized` と同じ意味で重複する時だけ compact を適用する
- compact 時の headline は `- [new-candidate] normalized [level] x<count> | <target>` とする
- compact 時は `variants/target` 行を出さない
- multi-variant や variant 情報が冗長でない時は `variants/target` 行を維持する
- JSON payload は変更しない
