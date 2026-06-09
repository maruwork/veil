# Execution Report

## Bundle

- id
  - `VEIL-TUNING-025`
- theme
  - `single-variant headline target compaction`

## What Changed

- `veil-normalize.py` の non-low-priority `new-candidate` で、single-variant かつ variant 情報が headline と重複する時だけ `target` を headline へ寄せるようにした
- compact 条件に当たる時は `variants/target` 行を省く
- multi-variant または重複しない時は `variants/target` 行を維持
- `README.md`、`docs/veil-design.md`、2 つの capture skill を新契約へ追従
- `index/project-current-work.md` を wave 29 close 状態へ更新

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `verification` が `- [new-candidate] verification [観察] x1 | v.md` になり、`variants/target` 行が省かれることを確認
- text smoke で multi-variant / non-redundant sample は `variants/target` 行を維持することを確認
- text smoke で low-priority `close` branch unchanged を確認
- `rtk python veil-normalize.py --text "summary\nsummary\nsummary-report\nverification" --json`
- `rtk rg -n "single-variant|headline の末尾" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md`

## Result

- single-variant の冗長ケースだけ detail 行を 1 行削減
- multi-variant と low-priority branch は維持
- existing-match unchanged
- JSON unchanged
