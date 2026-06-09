# existing-match source count suppression execution report

## Summary

- bundle id:
  - `VEIL-TUNING-037`
- execution date:
  - `2026-06-07`
- result:
  - `complete`

## Scope

- `veil-normalize.py` の existing-match source header から件数表示を外す
- `README.md`、`docs/veil-design.md`、capture skill 2 面、`index/project-current-work.md` を同契約へそろえる

## Changes

- `veil-normalize.py`
  - grouped existing-match source header を `source: <file>` へ変更した
- `README.md`
  - source header は file 名のみを表示し、件数は行数で把握する契約へ更新した
- `docs/veil-design.md`
  - source header の count 非表示を反映した
- `skills/codex/veil-capture/SKILL.md`
  - grouped source の件数は header ではなく行数で読むことを反映した
- `skills/claude-code/veil-capture.md`
  - grouped source の件数は header ではなく行数で読むことを反映した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
  - pass
- text smoke
  - `source: c.md`
  - `- checkpoint -> チェックポイント [推奨]`
  - `- task -> タスク [必須]`
- JSON smoke
  - pass
  - JSON contract unchanged

## Outcome

- existing-match source header の冗長件数を除去した
- grouped source の可読性を落とさず text 出力をさらに軽くした
- docs / skills / current companion を同一契約へそろえた

## Next

- `capture 候補絞り込みの追加縮約`
- または `existing-match` 側の残る冗長行整理
