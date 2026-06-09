# detail label compaction execution report

## Summary

- bundle id:
  - `VEIL-TUNING-044`
- execution date:
  - `2026-06-07`
- result:
  - `complete`

## Scope

- non-low-priority detail line label を `review:` に短縮する
- `README.md`、`docs/veil-design.md`、capture skill 2 面、`index/project-current-work.md` を同契約へそろえる

## Changes

- `veil-normalize.py`
  - detail line label を `review:` へ短縮した
- `README.md`
  - detail line は `review:` の後ろの値だけを読む契約へ更新した
- `docs/veil-design.md`
  - same contract を反映した
- `skills/codex/veil-capture/SKILL.md`
  - `review: ...` の 1 行で読むことを反映した
- `skills/claude-code/veil-capture.md`
  - `review: ...` の 1 行で読むことを反映した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
  - pass
- text smoke
  - `review: 先に採る候補 | 説明語候補`
  - `review: 保留寄り | 後で再観察する | 説明語候補`
- JSON smoke
  - pass
  - value order unchanged

## Outcome

- detail line label を短縮した
- detail line の値順と JSON 契約は維持した
- docs / skills / current companion を同一契約へそろえた

## Next

- `capture 候補絞り込みの追加縮約`
- または `existing-match` 側の残る冗長行整理
