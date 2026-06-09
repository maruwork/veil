# Execution Report

## Bundle

- id
  - `VEIL-TUNING-028`
- theme
  - `existing-match single-source header suppression`

## What Changed

- `veil-normalize.py` の `existing-match` で、source file が 1 件だけの時は独立 header を出さず、item 行末へ `| source: <file>` を付けるようにした
- 複数件 source の grouping は維持
- `README.md`、`docs/veil-design.md`、2 つの capture skill を新契約へ追従
- `index/project-current-work.md` を wave 32 close 状態へ更新

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `checkpoint`、`summary`、`verification` が `| source: <file>` 付きの 1 行になり、独立 header が消えることを確認
- text smoke で source grouping が必要な時だけ header を維持する実装であることを確認
- new-candidate branch unchanged を確認
- `rtk python veil-normalize.py --text "summary\nsummary\nverification\ncheckpoint\ncheckpoint" --json`
- `rtk rg -n "1 件 source|複数件 source|source: <file>" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md`

## Result

- 1 件 source の existing-match で独立行を 1 行削減
- 複数件 source の grouping 効果は維持
- new-candidate / low-priority / JSON unchanged
