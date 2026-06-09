# review group count suppression execution report

## Summary

- bundle id:
  - `VEIL-TUNING-038`
- execution date:
  - `2026-06-07`
- result:
  - `complete`

## Scope

- `veil-normalize.py` の review group header から件数表示を外す
- `README.md`、`docs/veil-design.md`、capture skill 2 面、`index/project-current-work.md` を同契約へそろえる

## Changes

- `veil-normalize.py`
  - `短い review に残す (N件):` / `短い review から外す寄り (N件):` を件数なし header に変更した
- `README.md`
  - review group header は節名とその下の行数で把握する契約へ更新した
- `docs/veil-design.md`
  - review group header の count 非表示を反映した
- `skills/codex/veil-capture/SKILL.md`
  - review group header の件数は見ないことを反映した
- `skills/claude-code/veil-capture.md`
  - review group header の件数は見ないことを反映した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
  - pass
- text smoke
  - `短い review に残す:`
  - `短い review から外す寄り:`
- JSON smoke
  - pass
  - JSON contract unchanged

## Outcome

- review group header の冗長件数を除去した
- source header と同じく件数は行数で把握する契約にそろえた
- docs / skills / current companion を同一契約へそろえた

## Next

- `capture 候補絞り込みの追加縮約`
- または `existing-match` 側の残る冗長行整理
