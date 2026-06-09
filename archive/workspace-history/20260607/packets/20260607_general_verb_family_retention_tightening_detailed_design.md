# Detailed Design

## Code

1. `veil-normalize.py` の `suggest_retention_hint()` で、single-word かつ general verb family なら occurrence_count に関係なく `今は見送る` を返す
2. 既存の shortlist ルールを再利用し、`短い review から外す寄り` へ落とす

## Surface

1. `README.md` の normalize 説明を「複数回でもまず今は見送る」へ明確化する
2. `docs/veil-design.md` と 2 skills も同じ契約へそろえる
3. `index/project-current-work.md` を新 bundle へ切り替える
