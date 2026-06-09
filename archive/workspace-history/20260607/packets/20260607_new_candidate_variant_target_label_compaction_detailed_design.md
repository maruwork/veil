# Detailed Design

## Code

1. `veil-normalize.py` の `new-candidate` detail line を `variants/target:` から `variants:` へ変更する
2. 出力形は `variants: <variants> | <target>` にする

## Surface

1. `README.md` の該当 normalize 説明を `variants:` 契約へ修正する
2. `docs/veil-design.md` と 2 skills も同じ label へそろえる
3. `index/project-current-work.md` を新 bundle へ切り替える
