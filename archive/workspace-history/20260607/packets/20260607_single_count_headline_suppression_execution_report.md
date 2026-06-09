# single-count headline suppression execution report

## Summary

- bundle id:
  - `VEIL-TUNING-043`
- execution date:
  - `2026-06-07`
- result:
  - `complete`

## Scope

- non-low-priority `new-candidate` headline から single count の `x1` を除去する
- `README.md`、`docs/veil-design.md`、capture skill 2 面、`index/project-current-work.md` を同契約へそろえる

## Changes

- `veil-normalize.py`
  - `occurrence_count == 1` の時は headline の `x1` を出さないようにした
- `README.md`
  - count は 2 回以上の時だけ headline で読む契約へ更新した
- `docs/veil-design.md`
  - same contract を反映した
- `skills/codex/veil-capture/SKILL.md`
  - headline は `normalized [level]` を先に見て、必要時だけ `x<count>` を読むことを反映した
- `skills/claude-code/veil-capture.md`
  - headline は `normalized [level]` を先に見て、必要時だけ `x<count>` を読むことを反映した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
  - pass
- text smoke
  - `summary [推奨] x2 | s.md`
  - `verification [観察] | v.md`
- JSON smoke
  - pass
  - `summary occurrence_count = 2`
  - `verification occurrence_count = 1`

## Outcome

- single-count headline の `x1` を除去した
- multiple-count headline の `x<count>` は維持した
- docs / skills / current companion を同一契約へそろえた

## Next

- `capture 候補絞り込みの追加縮約`
- または `existing-match` 側の残る冗長行整理
