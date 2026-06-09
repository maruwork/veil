# Detailed Design

## Code

1. `veil-normalize.py` に lowercase phrase token の noun-like 判定 helper を追加する
2. space を含む lowercase phrase で occurrence_count == 1 の時、noun-like token がなければ `境界が曖昧な候補` を返す
3. occurrence_count >= 2 の phrase は従来どおり `説明語候補` を維持する

## Surface

1. `README.md` に single-occurrence phrase は保守側に残す旨を追記する
2. `docs/veil-design.md` と 2 skills を同契約へそろえる
3. `index/project-current-work.md` を新 bundle へ切り替える
