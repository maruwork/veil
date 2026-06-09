# Execution Report

## Theme

VEIL tuning wave 11: candidate-first ordering

## Result

- `veil-normalize.py` の text 出力で、各節の `new-candidate` を `existing-match` より前に並べた
- compact existing-match branch は維持した
- `README.md`、`docs/veil-design.md`、2 つの capture skill、`index/project-current-work.md` を同契約へ更新した

## Evidence

- command:
  - `rtk python -m py_compile veil-normalize.py`
- command:
  - `rtk python veil-normalize.py --text "current state\nverification\nskill\nsummary\nsummary"`
- command:
  - `rtk python veil-normalize.py --text "current state\nverification\nskill\nsummary\nsummary" --json`
- command:
  - `rtk rg "new-candidate|existing-match|group 内" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md index/project-current-work.md`

## Verification Summary

- text 出力:
  - `summary`, `verification` が先
  - `current state`, `skill` が後
- JSON 出力:
  - key contract unchanged
- surface alignment:
  - README / design / 2 skills / current companion が candidate-first ordering 契約を共有する

## Scope Check

- changed:
  - `veil-normalize.py`
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
  - `index/project-current-work.md`
- unchanged:
  - JSON structure
  - `veil-lint.py`
  - `veil-sync.py`
  - schema / DB
  - UI

## Completion Decision

- wave 11 completion condition:
  - PASS
