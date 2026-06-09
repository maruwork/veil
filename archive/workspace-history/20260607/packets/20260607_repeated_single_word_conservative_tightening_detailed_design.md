# Detailed Design

## Code

1. `veil-normalize.py` の single-word lowercase 判定で、`occurrence_count >= 2` の自動昇格条件を `>= 3` へ tighten する
2. `occurrence_count == 2` の時は `境界が曖昧な候補` を返し、理由を repeated single-word だがまだ広すぎる旨にする

## Surface

1. `README.md` に repeated single-word は 2 回だけでは保守側のまま、と追記する
2. `docs/veil-design.md` と 2 skills も同じ契約へそろえる
3. `index/project-current-work.md` を新 bundle へ切り替える
