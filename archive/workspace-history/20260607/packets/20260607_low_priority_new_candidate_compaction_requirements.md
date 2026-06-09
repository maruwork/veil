# Requirements

## Theme

VEIL tuning wave 14: low-priority new-candidate compaction

## Goal

`veil-normalize.py` の text 出力で、低優先の `new-candidate` を短く見せる。

## Scope In

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Scope Out

- JSON contract change
- schema change
- lint runtime
- UI

## Required Outcome

1. `観察 + 保留候補 + 今は見送る` の low-priority new-candidate が compact 表示になる
2. `先に採る候補` や `後で再観察する` は詳細表示を維持する
3. JSON 契約は維持する
4. docs / skills / current companion が low-priority compaction 契約を共有する
