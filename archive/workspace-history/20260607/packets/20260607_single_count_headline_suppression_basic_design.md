# single-count headline suppression basic design

## Intent

single-occurrence の `x1` は情報量が低いので、headline から外して可読性を上げる。複数回出現した時だけ count を強調する。

## Design

1. non-low-priority `new-candidate` headline は `occurrence_count > 1` の時だけ `x<count>` を付ける
2. `occurrence_count == 1` の時は level だけ表示する
3. JSON の `occurrence_count` は維持する
4. docs / skills には `count > 1` の時だけ headline count を読むと記す

## Invariants

- low-priority branch unchanged
- existing-match branch unchanged
- JSON 契約 unchanged
