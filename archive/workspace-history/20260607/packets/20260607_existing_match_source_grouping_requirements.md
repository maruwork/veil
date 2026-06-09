# Requirements

## Theme

VEIL tuning wave 13: existing-match source grouping

## Goal

`veil-normalize.py` の text 出力で、existing-match を source file ごとに固めて見やすくする。

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

1. existing-match が source file ごとにまとまる
2. new-candidate detail は維持する
3. JSON 契約は維持する
4. docs / skills / current companion が source grouping 契約を共有する
