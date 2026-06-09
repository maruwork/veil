# Execution Report

## Bundle

- bundle id: `VEIL-TUNING-032`
- theme: `detail reason suppression`

## What Changed

- `veil-normalize.py` の non-low-priority `new-candidate` text renderer から理由文を外した
- retention あり branch は hint-only の 2 行にそろえた
- retention なし branch は hint-only の 1 行にそろえた
- `README.md`、`docs/veil-design.md`、2 つの `veil-capture` skill、`index/project-current-work.md` を同じ契約へ追従させた

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke
  - retention あり:
    - `選別/review/保留: 保留寄り | 短い review に残す | 後で再観察する`
    - `判別/priority/level: 説明語候補 | 保留候補 | 観察`
  - retention なし:
    - `選別/review/判別/priority/level: 先に採る候補 | 短い review に残す | 説明語候補 | 次に見る | 推奨`
- JSON smoke
  - `rtk python veil-normalize.py --text "close" --json`
  - JSON contract unchanged
- surface readback
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
  - `index/project-current-work.md`

## Result

- wave 36 close
- detail branch text output changed to hint-only
