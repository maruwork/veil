# Quality Gate

## Gate Summary

- theme:
  - VEIL tuning wave 7
- pass condition:
  - goal, path, checkpoint, task, design, traceability が切れず、runtime 範囲が `veil-normalize.py` に閉じている

## Checks

- goal explicit:
  - PASS
- path explicit:
  - PASS
- checkpoint explicit:
  - PASS
- task coverage:
  - PASS
- design explicit:
  - PASS
- traceability ready:
  - PASS
- blocker:
  - none

## Planned Commands

- `rtk python -m py_compile veil-normalize.py`
- `rtk python veil-normalize.py --text ... --json`
- `rtk rg "一般動詞|close|closing|updates" ...`

## Ready Decision

- ready for implementation:
  - YES
- next file to touch first:
  - `veil-normalize.py`
